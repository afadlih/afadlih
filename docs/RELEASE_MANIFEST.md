# Release Manifest — Special Profile v3.7

## Purpose

A copy-ready GitHub special-profile repository with education-aware scan-first information architecture, deterministic README generation, local SVG activity visualization, daily activity refresh, aggregate-only private metrics, source-derived versions, deep-dive case studies, and controlled project discovery.

## Permanent workflows

- `.github/workflows/validate-profile.yml`
- `.github/workflows/update-profile-activity.yml`

## README hierarchy

1. Hero and student-engineer positioning
2. Education
3. Selected engineering work
4. Currently building
5. Experience and recognition
6. Engineering approach
7. Engineering activity
8. Project and case-study library
9. Contact

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
