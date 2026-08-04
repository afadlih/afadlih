# Commit-Ready Guide

## 1. Preview safely

From the extracted package:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force

.\APPLY-TO-CURRENT-REPO.ps1 `
  -TargetRepository 'D:\path	ofadlih' `
  -DryRun
```

Review the listed create, update, and delete operations.

## 2. Apply with automatic backup

```powershell
.\APPLY-TO-CURRENT-REPO.ps1 `
  -TargetRepository 'D:\path	ofadlih'
```

The helper validates the package, creates a rollback snapshot and ZIP backup, applies the files, runs `final-check`, and restores the previous worktree if validation fails. The existing `.git` directory is preserved.

## 3. Review through a branch

```powershell
Set-Location 'D:\path	ofadlih'
git switch -c feat/special-profile-v3
git status --short
git diff --stat
git diff -- README.md
python .\scripts\portfolio_ci.py final-check
```

## 4. Commit and push

```powershell
git add -A
git commit -m "feat(profile): focus special profile on inspectable engineering work"
git push -u origin feat/special-profile-v3
```

Open a pull request to `main`, confirm the **Validate special profile** check passes, inspect all links in the rendered README, and then merge.

## 5. Complete manual settings

Follow:

- `docs/REPOSITORY_SETTINGS.md` for rulesets, Actions permissions, and security;
- `docs/PROFILE_SETUP.md` for bio, location, website, and pinned repositories.
