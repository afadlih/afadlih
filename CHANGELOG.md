# Changelog

## 3.4.0 — Daily refresh and controlled project discovery

- changed activity refresh from weekly to daily at 06:17 WIB;
- prevented generated bot commits from retriggering the refresh workflow;
- added an approved private project registry with generic version-source rules;
- rebuilt Current Engineering Focus automatically from the latest approved private activity;
- added semver-aware condition updates for release-candidate projects;
- added public repository discovery and private public-label discovery;
- enforced `auto_publish: false` for every discovered candidate;
- added review commands for approving or ignoring candidates;
- added schemas, privacy validation, workflow regression tests, and documentation;
- kept private repository identifiers only in encrypted runtime configuration.

## 3.3.0 — 180-day engineering activity and current versions

- replaced the sparse 30-day public sample with a privacy-reviewed 180-day authored-commit history;
- added aggregate commit counts for seven selected private projects;
- synchronized current project versions from their source repositories;
- separated version from development condition;
- replaced the wide Current Engineering Focus table with a more readable project list;
- preserved private repository URLs, branches, SHAs, and commit messages outside tracked outputs.
