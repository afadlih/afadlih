# Controlled Project Discovery

The repository scans for project candidates every day, but it never publishes a newly detected repository automatically.

## Why approval is required

A repository can be public while still being unsuitable for the profile. It may be an empty test, coursework, a temporary technical assessment, a fork, or a repository whose name and description do not communicate useful engineering work. Private repositories require an even stricter boundary because their identifiers must not be committed to this public profile repository.

## Daily detection flow

```text
GitHub public repositories
        +
encrypted private label mapping
        ↓
scripts/discover_projects.py
        ↓
portfolio/discovered-projects.json
        ↓
pending_review / ignored
        ↓
explicit approval on develop
        ↓
validated pull request to main
```

### Public candidates

A public repository becomes a candidate when it:

- belongs to `afadlih`;
- is not already in `portfolio/activity-sources.json`;
- is not archived;
- is not a fork;
- has been pushed within the rolling discovery window, currently 180 days.

Public candidates may include their public repository URL, language, description, and latest push date. They do not appear in the README until approved.

### Private candidates

The workflow cannot safely discover every private repository without broader account access. It therefore inspects only the public-safe labels present in the encrypted `PROFILE_PRIVATE_REPOSITORIES_JSON` mapping.

When the secret contains a label not present in `portfolio/private-project-registry.json`, the public repository records only:

- an opaque candidate ID;
- the approved public-safe label;
- review status;
- the reason it was detected.

The private repository identifier is never written to disk.

## Review commands

List candidates:

```bash
python scripts/review_discovered_project.py list
```

Ignore a candidate while keeping the decision stable across future scans:

```bash
python scripts/review_discovered_project.py ignore public-cabd49defca0
```

Approve a public repository for the recently-updated activity table:

```bash
python scripts/review_discovered_project.py approve-public \
  public-cabd49defca0 \
  --display-name "SEAL AI Engineer Technical Test"
```

A public approval adds the repository to `portfolio/activity-sources.json`. It does not automatically promote the repository into Selected Work; a curated `portfolio/projects.json` record and evidence are still required.

Approve a private candidate with public-safe metadata:

```bash
python scripts/review_discovered_project.py approve-private \
  private-0123456789ab \
  --condition "Active development" \
  --condition-strategy fixed \
  --public-summary "Public-safe description with no internal architecture or operational data." \
  --focus "Current engineering focus written for a public recruiter-facing profile." \
  --version-path package.json \
  --version-strategy json \
  --version-field version
```

After approval, the next authenticated daily refresh reads the version and commit aggregates, orders Current Engineering Focus by latest approved activity, and regenerates the README.

## Important limitation

A brand-new private repository is discoverable only after the fine-grained token is granted read access and a public-safe label is added to `PROFILE_PRIVATE_REPOSITORIES_JSON`. This is a GitHub authorization boundary, not a limitation that should be bypassed with an account-wide token.
