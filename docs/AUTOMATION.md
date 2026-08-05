# Profile Automation

The profile separates three maintenance concerns:

1. public repository metadata;
2. the privacy-reviewed rolling 180-day authored-commit snapshot;
3. a controlled review queue for newly detected projects.

## Source of truth

- `portfolio/profile.json` — generated current focus plus stable positioning, experience, and recognition;
- `portfolio/projects.json` — curated case-study and Selected Work records;
- `portfolio/proof-assets.json` — evidence boundaries;
- `portfolio/activity-sources.json` — approved public repositories for the recently-updated table;
- `portfolio/private-project-registry.json` — approved public-safe metadata and version-source rules for private projects;
- `portfolio/repository-activity.json` — generated public metadata;
- `portfolio/engineering-activity.json` — sanitized rolling 180-day authored-commit snapshot;
- `portfolio/discovered-projects.json` — generated review queue that never auto-publishes;
- `assets/engineering-activity.svg` — generated local visualization.

## Local quality commands

```bash
python -m pip install -r requirements-dev.txt
python scripts/portfolio_ci.py update
python scripts/portfolio_ci.py final-check
```

`update` regenerates the SVG, README, proof report, and generated summary. `final-check` validates schemas, activity arithmetic, registry alignment, project-discovery privacy, deterministic outputs, evidence, links, anchors, repository policy, workflows, and tests.

## Daily workflow

`update-profile-activity.yml` runs:

- every day at 06:17 WIB;
- manually through `workflow_dispatch`;
- after relevant source or automation changes reach `main`.

It performs this sequence:

```text
checkout latest main
→ remove non-persistent branches
→ refresh approved public repositories
→ detect new project candidates
→ refresh authenticated private aggregates and source versions when configured
→ rebuild current focus by latest approved activity
→ regenerate README and local SVG
→ run final-check
→ commit only meaningful changes
→ guarded fast-forward main
→ synchronize develop when safe
```

Generated output paths are intentionally excluded from the push trigger, so the bot's own commit does not start another refresh loop.

## Refreshing private activity safely

Provide encrypted repository secrets:

- `PROFILE_ACTIVITY_TOKEN` — fine-grained token with read-only access to only the selected private repositories;
- `PROFILE_PRIVATE_REPOSITORIES_JSON` — JSON mapping approved public labels to private `owner/repository` identifiers.

The tracked registry contains only safe labels, descriptions, focus text, condition policy, and version-source paths. Repository identifiers remain in the encrypted mapping.

Local example:

```bash
export PROFILE_ACTIVITY_TOKEN='set-locally-not-in-git'
export PROFILE_PRIVATE_REPOSITORIES_JSON='{"Approved project label":"owner/private-repository"}'
python scripts/discover_projects.py --write
python scripts/update_engineering_activity.py --verify
python scripts/update_engineering_activity.py --write
python scripts/portfolio_ci.py update
python scripts/portfolio_ci.py final-check
```

Never commit either secret, raw API responses, private URLs, branch names, SHAs, or commit messages.

## New project behavior

- Existing approved private projects update version, aggregate commits, latest date, condition policy, and profile order automatically.
- Existing approved public repositories update their metadata automatically.
- New public repositories enter `portfolio/discovered-projects.json` as `pending_review`.
- New private labels supplied through the encrypted mapping enter the same queue without repository identifiers.
- Nothing is added to README Selected Work without explicit curation and evidence review.

See [Controlled Project Discovery](PROJECT_DISCOVERY.md) for review commands.

## Security model

- official Actions are pinned to immutable commit SHAs;
- workflows declare explicit permissions, concurrency, and timeouts;
- the normal repository token is not treated as cross-repository private access;
- private identifiers live only in encrypted runtime configuration;
- the committed snapshot contains approved labels, versions, conditions, counts, and dates only;
- the discovery queue has `auto_publish: false` enforced by schema and validation;
- no workflow force-pushes `main` or `develop`.
