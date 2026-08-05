# Engineering Activity Data Provenance

## Scope

`portfolio/engineering-activity.json` is a rolling 180-day snapshot of commits authored by the profile owner and indexed by GitHub Commit Search. It includes aggregate counts for selected private projects only when authenticated private access is configured.

It is not a lifetime contribution total and may differ from GitHub's contribution calendar because search indexing, attribution, merge commits, email association, repository visibility, and calendar rules are not identical.

## Daily refresh

The scheduled workflow runs every day at 06:17 WIB. It first identifies the most recent indexed authored commit, then anchors the inclusive 180-day window to that date. This prevents an inactive day from shifting the chart while still allowing new indexed work to move the window forward.

## Public history

Monthly or partial-month totals use authenticated GitHub commit-search queries:

```text
author:<username> author-date:<start>..<end>
```

The output stores only labels, date ranges, and aggregate counts.

## Selected private activity

Each approved private project is queried with:

```text
repo:<encrypted-runtime-identifier> author:<username> author-date:<start>..<end>
```

The runtime identifier comes from `PROFILE_PRIVATE_REPOSITORIES_JSON`. The tracked `private-project-registry.json` supplies the public-safe label, focus text, condition policy, case-study path, and version-source rule.

The output stores:

- approved public label;
- source-resolved version;
- curated or semver-derived condition;
- aggregate authored-commit count;
- latest authored-commit date;
- approved public summary;
- optional sanitized case-study path.

The output never stores the private repository identifier, URL, branch, SHA, or commit message.

## Version and condition updates

Versions are read from approved source paths such as `package.json` or a release heading in `README.md`. A semver condition policy automatically maps release-candidate and pre-release versions to their correct public stage; product conditions that cannot be inferred safely remain curated in the registry.

## New repository discovery

Public repositories are scanned daily for recent, non-fork, non-archived candidates. Private discovery is limited to additional public-safe labels in the encrypted mapping. Candidates enter a tracked review queue with `auto_publish: false` and do not appear in the README until explicitly approved.

## Reproducibility boundary

The committed JSON and generated SVG are deterministic. Live API retrieval is not fully reproducible because GitHub Search indexes can change. Every checked-in snapshot therefore records its bounded window and date rather than claiming permanent historical completeness.
