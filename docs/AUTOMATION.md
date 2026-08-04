# Automation

This special profile repository keeps automation deliberately small. Structured profile data produces one public README; it does not export a second website data model.

## Source of truth

- `portfolio/profile.json` — positioning, experience, recognition, and engineering principles;
- `portfolio/projects.json` — curated project records and profile placement;
- `portfolio/proof-assets.json` — evidence boundaries for the three selected projects;
- `portfolio/activity-sources.json` — explicit allowlist of public repositories;
- `portfolio/repository-activity.json` — generated public metadata snapshot.

## Local commands

```bash
python -m pip install -r requirements-dev.txt
python scripts/portfolio_ci.py update
python scripts/portfolio_ci.py final-check
```

`update` regenerates deterministic artifacts. `final-check` validates schemas, README determinism, evidence, links, anchors, repository policy, workflows, and tests.

## Workflows

### `validate-profile.yml`

Runs on pull requests and relevant pushes. It executes the same final quality gate used locally.

### `update-profile-activity.yml`

Runs weekly or manually. It reads only the public repositories in `activity-sources.json`, refreshes metadata, regenerates the README, validates the result, and opens or updates a pull request only when meaningful content changes. It never pushes generated content directly to `main`.

## Security model

- public activity uses the repository `GITHUB_TOKEN`, not a personal access token;
- official actions are pinned to immutable commit SHAs;
- each workflow declares minimal permissions, concurrency, and timeout limits;
- private project repositories are never queried by the activity updater.
