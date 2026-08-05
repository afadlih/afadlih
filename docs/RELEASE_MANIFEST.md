# Release Manifest — Special Profile v3.4

## Purpose

A copy-ready GitHub special-profile repository with deterministic README generation, local SVG activity visualization, daily public/private activity refresh, source-derived versions, and controlled project discovery.

## Permanent workflows

- `.github/workflows/validate-profile.yml`
- `.github/workflows/update-profile-activity.yml`

## Generated outputs

- `README.md`
- `assets/engineering-activity.svg`
- `portfolio/repository-activity.json`
- `portfolio/engineering-activity.json`
- `portfolio/discovered-projects.json`
- `docs/PROOF_ASSET_REPORT.md`
- `docs/GENERATED_UPDATE_SUMMARY.md`

## Approval sources

- `portfolio/activity-sources.json`
- `portfolio/private-project-registry.json`
- `portfolio/projects.json`
- `portfolio/proof-assets.json`

## Release gate

```bash
python scripts/portfolio_ci.py final-check
```

A package is push-ready only after the extracted archive passes the complete gate.
