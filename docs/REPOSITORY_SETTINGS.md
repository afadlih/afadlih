# Repository Settings

## Persistent branches

Keep only:

- `main` — public, validated profile;
- `develop` — manual development and review branch.

The activity workflow removes other persistent branches and synchronizes `develop` to `main` only when `develop` contains no unmerged work.

## Main branch protection

Recommended settings:

- require a pull request before manual changes are merged;
- require `Validate special profile`;
- require conversation resolution;
- block force pushes;
- block branch deletion;
- permit GitHub Actions to write generated daily activity commits after the complete gate passes.

## Required Actions secrets

### `PROFILE_ACTIVITY_TOKEN`

Use a fine-grained token with:

- repository access limited to the approved private projects;
- Contents: read-only;
- Metadata: read-only.

### `PROFILE_PRIVATE_REPOSITORIES_JSON`

Store a JSON object whose keys are public-safe labels matching `portfolio/private-project-registry.json` and whose values are private repository identifiers.

Adding a new label to the secret does not publish the project. It enters the controlled discovery queue until safe metadata is approved on `develop`.

## Schedule

The activity workflow uses:

```yaml
cron: "17 23 * * *"
```

This corresponds to 06:17 WIB every day. GitHub schedule execution can be delayed during platform load, so the time is approximate rather than a service-level guarantee.
