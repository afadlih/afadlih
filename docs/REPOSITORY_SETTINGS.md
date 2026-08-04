# Repository Settings Checklist

These settings are intentionally documented rather than changed by source code. Apply them in the GitHub repository settings after the package is merged.

## Branch protection for `main`

Create a ruleset targeting `main` and enable:

- require a pull request before merging;
- require the `Validate special profile / validate` status check;
- require branches to be up to date before merging;
- block force pushes and branch deletion;
- require conversation resolution before merging;
- allow repository administrators to bypass only for recovery.

The scheduled activity workflow opens a pull request, so it does not require a branch-protection bypass.

## Actions permissions

Use **Read repository contents permission** as the default. Write permissions are scoped only to `update-profile-activity.yml`, which needs `contents: write` and `pull-requests: write` to maintain its automation branch and pull request.

Do not add a personal access token. The workflows are designed to use the repository `GITHUB_TOKEN` only.

## Security

Enable:

- Dependabot alerts and security updates;
- secret scanning;
- push protection;
- private vulnerability reporting when the repository will accept external reports.

Keep all actions pinned to immutable commit SHAs. Review Dependabot action updates before merging.

## Repository metadata

Recommended description:

> Full-stack developer profile focused on reliable AI workflows, operational systems, and on-premise IoT integration.

Recommended topics:

```text
profile-readme fullstack ai-engineering automation iot portfolio
```

The repository name must match the GitHub username exactly (`afadlih`) for GitHub to render it as the special profile repository.
