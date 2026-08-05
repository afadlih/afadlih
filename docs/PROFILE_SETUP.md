# Profile Setup

## GitHub profile repository

The public profile is rendered from the `README.md` in the special repository `afadlih/afadlih`.

## Local setup

```bash
python -m pip install -r requirements-dev.txt
python scripts/portfolio_ci.py final-check
```

## Persistent branch model

- `main` — public profile and generated daily activity;
- `develop` — manual edits and candidate approval.

## Daily automation secrets

In repository Settings → Secrets and variables → Actions, configure:

### `PROFILE_ACTIVITY_TOKEN`

Fine-grained read-only token limited to the private projects approved for aggregate activity and version reading.

### `PROFILE_PRIVATE_REPOSITORIES_JSON`

Encrypted JSON mapping public-safe labels to private repository identifiers. Labels must match `portfolio/private-project-registry.json`.

Example shape:

```json
{
  "Approved public label": "owner/private-repository"
}
```

Do not place real private repository identifiers in tracked documentation, tests, or JSON.

## New projects

The workflow scans public repositories daily and compares encrypted private labels against the approved registry. Review candidates with:

```bash
python scripts/review_discovered_project.py list
```

See [Controlled Project Discovery](PROJECT_DISCOVERY.md).
