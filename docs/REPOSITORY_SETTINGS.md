# Repository Settings Checklist

These settings are intentionally documented rather than changed by source code. Apply them in the GitHub repository settings after the package is merged.

## Branch protection for `main`

The profile has two write paths:

1. Human changes should use pull requests and pass `Validate special profile / validate`.
2. The scheduled activity workflow performs a normal fast-forward update only after the same complete `final-check` succeeds.

Recommended ruleset:

- require the `Validate special profile / validate` status check for pull requests;
- block force pushes and branch deletion;
- require conversation resolution before merging human pull requests;
- allow repository administrators to bypass only for recovery;
- do not configure a rule that blocks the repository `GITHUB_TOKEN` from making the validated fast-forward activity update.

The activity workflow never force-pushes. It records the starting `main` SHA, regenerates the data and local SVG, runs the complete quality gate, fetches `main` again, and refuses the update if `main` moved during generation.

If the repository is changed to require a pull request for every actor, enable **Allow GitHub Actions to create and approve pull requests** first and deliberately switch the workflow back to PR mode. Without that repository setting, `GITHUB_TOKEN` cannot create the automation PR.

## Actions permissions

Use **Read repository contents permission** as the default. Write permission is scoped only inside `update-profile-activity.yml`:

```yaml
permissions:
  contents: write
```

The workflow does not need `pull-requests: write`, a personal access token, or a force push.

## Activity workflow safety boundary

The scheduled workflow:

1. checks out the latest `origin/main`;
2. records the starting commit SHA;
3. queries only allowlisted public repositories;
4. excludes private, archived, and disabled repositories;
5. writes repository metadata and a bounded authored-commit sample;
6. regenerates the repository-owned SVG and README;
7. runs schema, proof, link, anchor, repository-policy, and unit-test gates;
8. commits only meaningful generated changes;
9. verifies that remote `main` still matches the starting SHA;
10. performs a normal fast-forward push to `main`.

Generated files are not included in the workflow's `push.paths` trigger, so the bot commit does not create a refresh loop.

## Security

Enable:

- Dependabot alerts and security updates;
- secret scanning;
- push protection;
- private vulnerability reporting when the repository will accept external reports.

Keep all actions pinned to immutable commit SHAs. Review Dependabot action updates before merging.

## Repository metadata

Recommended description:

> Full-stack developer profile focused on reliable AI workflows, operational systems, and on-premise IoT integration.

Recommended topics:

```text
profile-readme fullstack ai-engineering automation iot portfolio
```

The repository name must match the GitHub username exactly (`afadlih`) for GitHub to render it as the special profile repository.
