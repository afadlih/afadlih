# Repository Settings and Two-Branch Policy

This profile repository uses exactly two persistent branches.

## Branch roles

### `main`

`main` is the live production branch. GitHub renders the public profile README from this branch.

Allowed writes:

1. a reviewed merge from `develop`;
2. the validated public-activity workflow, which performs a normal fast-forward update after the complete quality gate passes.

Do not develop features, repair files, or experiment directly on `main`.

### `develop`

`develop` is the only branch used for human changes. Documentation, profile data, scripts, assets, and workflow edits are committed here first.

Human release flow:

```text
develop
   ↓ validation
pull request: develop → main
   ↓ review and merge
main
```

Do not create permanent `feature/*`, `fix/*`, `automation/*`, or Dependabot version-update branches in this repository. The repository workflow removes branches other than `main` and `develop`.

## Daily working commands

Start work:

```bash
git fetch --prune origin
git switch develop
git pull --ff-only origin develop
```

Validate before pushing:

```bash
python scripts/portfolio_ci.py final-check
```

Push the integration branch:

```bash
git push origin develop
```

Then open one pull request from `develop` into `main`.

After the pull request is merged, synchronize locally:

```bash
git fetch --prune origin
git switch develop
git merge --ff-only origin/main
git push origin develop
```

The activity workflow also fast-forwards `develop` automatically when it is safe. It leaves `develop` unchanged when that branch contains work not yet present in `main`.

## Automatic branch hygiene

`update-profile-activity.yml` enforces the two-branch policy in two places:

1. a branch-creation event deletes a newly created branch unless its name is `main` or `develop`;
2. each scheduled, manual, or `main` refresh removes any stale remote branch outside the allowlist.

The cleanup uses repository-scoped `GITHUB_TOKEN` permissions and never force-pushes either persistent branch.

Scheduled Dependabot version updates are intentionally disabled because every Dependabot pull request creates another remote branch. Dependency upgrades must be reviewed and applied through `develop`. Dependabot alerts and repository security scanning may remain enabled in GitHub settings.

## Branch protection for `main`

Recommended ruleset:

- require the `Validate special profile / validate` status check for human pull requests;
- block force pushes and branch deletion;
- require conversation resolution before merging;
- allow repository administrators to bypass only for recovery;
- permit the repository `GITHUB_TOKEN` to perform the validated activity fast-forward update.

The activity workflow records the starting `main` SHA, regenerates the public data and repository-owned SVG, runs `final-check`, fetches `main` again, and refuses to publish when `main` moved during generation.

## Actions permissions

Use read-only repository permissions by default. Write permission is scoped inside the activity workflow:

```yaml
permissions:
  contents: write
```

The workflow does not require `pull-requests: write`, a personal access token, or a force push.

## Security

Enable:

- Dependabot alerts;
- secret scanning;
- push protection;
- private vulnerability reporting when external reports are accepted.

Keep every GitHub Action pinned to an immutable commit SHA. Review dependency changes manually on `develop` before promoting them to `main`.

## Repository metadata

Recommended description:

> Full-stack developer profile focused on reliable AI workflows, operational systems, and on-premise IoT integration.

Recommended topics:

```text
profile-readme fullstack ai-engineering automation iot portfolio
```

The repository name must match the GitHub username exactly (`afadlih`) for GitHub to render it as the special profile repository.
