# Implementation Report

**Release:** Special Profile v3.5  
**Scope:** Daily engineering activity, version synchronization, latest-project ordering, and controlled discovery.

## Delivered

- Daily scheduled refresh at 06:17 WIB.
- Rolling 180-day authored-commit snapshot.
- Authenticated tracking for approved private projects with only one aggregate commit total persisted.
- Generic source-file version resolution through a privacy-safe registry.
- Semver-aware stage updates for release-candidate projects.
- Automatic ordering of Current Engineering Focus by latest approved activity date.
- Daily detection of recent public repositories.
- Detection of additional private public-safe labels from encrypted configuration.
- Explicit pending-review queue with no automatic publication.
- Approval and ignore helper commands.
- Loop-safe workflow triggers and guarded fast-forward publication.
- Standardized private-work index with version, condition, latest activity, and case-study access.
- Per-project private commit counts removed from tracked JSON, SVG, and README.
- Schema, privacy, deterministic rendering, policy, and unit-test coverage.

## Privacy boundary

Tracked files contain no private repository identifiers, branches, SHAs, or commit messages. Private source access exists only during the workflow through encrypted read-only configuration.

## Operational boundary

A new private repository cannot be discovered until the fine-grained token is granted access and a public-safe label is added to the encrypted mapping. This is intentional least-privilege behavior.
