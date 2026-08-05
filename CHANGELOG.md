# Changelog

## 3.7.0 — Education context and student-engineer positioning

- added a dedicated Education section directly after the hero;
- identified Politeknik Negeri Malang / State Polytechnic of Malang as the current institution;
- added D-IV Informatics Engineering and Department of Information Technology context;
- refined the hero role to state the current student status without weakening the full-stack, AI, and IoT positioning;
- linked the institution to the official JTI Polinema website;
- added schema, deterministic rendering, repository-policy checks, regression tests, and content-standard guidance for education data;
- kept NIM, GPA, temporary school email, and unverified graduation dates out of the public profile.

## 3.6.0 — Scan-first profile information architecture

- moved the three flagship projects directly below the hero;
- reduced Currently Building to three editorial priorities;
- moved experience and recognition before activity metrics;
- merged What I Build and How I Work into one Engineering Approach section;
- consolidated additional case studies, supporting projects, and recent public repositories into one project library;
- moved the private project metadata index into a collapsed activity detail;
- removed duplicate top-level sections and redundant GitHub self-links;
- kept full technical depth in the existing case-study documents;
- updated schemas, synchronization limits, policy validation, tests, and documentation.

## 3.5.0 — Standardized aggregate activity and case-study index

- removed per-project commit counts from README, SVG, and checked-in activity data;
- retained one clearly labeled 180-day aggregate for approved private work;
- standardized the private project index into project, version, condition, latest activity, and deep-dive columns;
- preserved sanitized case-study links and public-safe project scope;
- updated validation and regression tests to reject published per-project commit counts;
- added `docs/PROFILE_CONTENT_STANDARD.md` to keep summary, tables, activity, and case studies consistent.

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
