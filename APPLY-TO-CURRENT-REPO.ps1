[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [string]$TargetRepository,

    [string]$BackupDirectory,

    [switch]$DryRun,

    [switch]$SkipValidation
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$sourceRepository = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$target = (Resolve-Path -LiteralPath $TargetRepository).Path

if ($sourceRepository -eq $target) {
    throw 'Extract this package outside the target clone before applying it.'
}
if (-not (Test-Path -LiteralPath (Join-Path $target '.git'))) {
    throw "TargetRepository must be an existing Git clone with a .git directory: $target"
}

function Test-IsExcludedRelativePath {
    param([Parameter(Mandatory = $true)][string]$RelativePath)

    $segments = $RelativePath -split '[\\/]'
    return $segments -contains '.git' -or $segments -contains '__pycache__'
}

function Get-RepositoryFileMap {
    param([Parameter(Mandatory = $true)][string]$RepositoryPath)

    $map = @{}
    Get-ChildItem -LiteralPath $RepositoryPath -Recurse -File -Force | ForEach-Object {
        $relative = [System.IO.Path]::GetRelativePath($RepositoryPath, $_.FullName)
        if (-not (Test-IsExcludedRelativePath -RelativePath $relative)) {
            $map[$relative] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
        }
    }
    return $map
}

function Show-ApplyPlan {
    param(
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$TargetPath
    )

    $sourceMap = Get-RepositoryFileMap -RepositoryPath $SourcePath
    $targetMap = Get-RepositoryFileMap -RepositoryPath $TargetPath

    $created = @($sourceMap.Keys | Where-Object { -not $targetMap.ContainsKey($_) } | Sort-Object)
    $updated = @($sourceMap.Keys | Where-Object { $targetMap.ContainsKey($_) -and $targetMap[$_] -ne $sourceMap[$_] } | Sort-Object)
    $deleted = @($targetMap.Keys | Where-Object { -not $sourceMap.ContainsKey($_) } | Sort-Object)

    Write-Host 'Profile package apply plan'
    Write-Host "  Source  : $SourcePath"
    Write-Host "  Target  : $TargetPath"
    Write-Host "  Create  : $($created.Count) files"
    Write-Host "  Update  : $($updated.Count) files"
    Write-Host "  Delete  : $($deleted.Count) files"
    Write-Host '  Preserve: .git only'
    Write-Host '  Verify  : strict profile quality gate before and after replacement'

    foreach ($entry in $created) { Write-Host "  + $entry" }
    foreach ($entry in $updated) { Write-Host "  ~ $entry" }
    foreach ($entry in $deleted) { Write-Host "  - $entry" }
}

function Invoke-ProfileValidation {
    param([Parameter(Mandatory = $true)][string]$RepositoryPath)

    Push-Location $RepositoryPath
    try {
        python -c "import jsonschema, yaml" 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw 'Validation dependencies are missing. Run: python -m pip install -r requirements-dev.txt'
        }
        python .\scripts\portfolio_ci.py final-check
        if ($LASTEXITCODE -ne 0) {
            throw "Profile validation failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

function Copy-RepositoryContent {
    param(
        [Parameter(Mandatory = $true)][string]$From,
        [Parameter(Mandatory = $true)][string]$To
    )

    Get-ChildItem -LiteralPath $From -Force |
        Where-Object { $_.Name -notin @('.git', '__pycache__') } |
        ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $To -Recurse -Force
        }
}

function Clear-RepositoryWorktree {
    param([Parameter(Mandatory = $true)][string]$RepositoryPath)

    Get-ChildItem -LiteralPath $RepositoryPath -Force |
        Where-Object { $_.Name -ne '.git' } |
        Remove-Item -Recurse -Force
}

if (-not $SkipValidation) {
    Write-Host 'Validating extracted package before touching the target...'
    Invoke-ProfileValidation -RepositoryPath $sourceRepository
}

Show-ApplyPlan -SourcePath $sourceRepository -TargetPath $target

if ($DryRun) {
    Write-Host ''
    Write-Host 'Dry run complete. No files were changed.'
    exit 0
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
if ([string]::IsNullOrWhiteSpace($BackupDirectory)) {
    $BackupDirectory = Join-Path (Split-Path -Parent $target) 'afadlih-profile-backups'
}
New-Item -ItemType Directory -Path $BackupDirectory -Force | Out-Null
$resolvedBackupDirectory = (Resolve-Path -LiteralPath $BackupDirectory).Path
$targetPrefix = $target.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
if ($resolvedBackupDirectory.StartsWith($targetPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'BackupDirectory must be outside TargetRepository.'
}

$workRoot = Join-Path ([System.IO.Path]::GetTempPath()) "afadlih-profile-apply-$([guid]::NewGuid().ToString('N'))"
$backupSnapshot = Join-Path $workRoot 'backup'
$stage = Join-Path $workRoot 'stage'
New-Item -ItemType Directory -Path $backupSnapshot, $stage -Force | Out-Null
$backupZip = Join-Path $resolvedBackupDirectory "afadlih-profile-before-$timestamp.zip"

try {
    Write-Host ''
    Write-Host "Creating rollback snapshot and backup: $backupZip"
    Copy-RepositoryContent -From $target -To $backupSnapshot
    Compress-Archive -Path $backupSnapshot -DestinationPath $backupZip -CompressionLevel Optimal -Force

    Write-Host 'Preparing staged package copy...'
    Copy-RepositoryContent -From $sourceRepository -To $stage

    if (-not $SkipValidation) {
        Write-Host 'Validating staged replacement...'
        Invoke-ProfileValidation -RepositoryPath $stage
    }

    if ($PSCmdlet.ShouldProcess($target, 'Replace special-profile worktree while preserving .git')) {
        Clear-RepositoryWorktree -RepositoryPath $target
        Copy-RepositoryContent -From $stage -To $target

        if (-not $SkipValidation) {
            Write-Host 'Validating applied repository...'
            Invoke-ProfileValidation -RepositoryPath $target
        }
    }
}
catch {
    Write-Warning "Apply failed: $($_.Exception.Message)"
    Write-Warning 'Restoring the pre-apply snapshot while preserving .git...'

    Clear-RepositoryWorktree -RepositoryPath $target
    Copy-RepositoryContent -From $backupSnapshot -To $target

    throw "Apply failed and the working tree was restored. Backup: $backupZip"
}
finally {
    if (Test-Path -LiteralPath $workRoot) {
        Remove-Item -LiteralPath $workRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ''
Write-Host 'Profile package applied and validated.'
Write-Host "Backup: $backupZip"
Write-Host 'Review before committing:'
Write-Host "  Set-Location '$target'"
Write-Host '  git switch -c feat/special-profile-v3'
Write-Host '  git status --short'
Write-Host '  git diff --stat'
Write-Host '  git diff -- README.md'
Write-Host '  git add -A'
Write-Host '  git commit -m "feat(profile): focus special profile on inspectable engineering work"'
