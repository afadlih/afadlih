# Commit-Ready Procedure

## 1. Apply the package

Use `APPLY-TO-CURRENT-REPO.ps1` with `-DryRun` first, inspect create/update/delete operations, then apply to the existing clone.

## 2. Work on develop

```bash
git fetch origin --prune
git switch develop
git pull --ff-only origin develop
```

## 3. Validate generated state

```bash
python -m pip install -r requirements-dev.txt
python scripts/portfolio_ci.py update
python scripts/portfolio_ci.py final-check
python scripts/review_discovered_project.py list
```

Review `portfolio/discovered-projects.json`. Detection is not publication. Approve or ignore candidates explicitly before merging.

## 4. Commit

```bash
git status --short
git diff --stat
git diff -- README.md

git add -A
git commit -m "feat(profile): add daily activity and controlled project discovery"
git push origin develop
```

## 5. Merge develop to main

Open a pull request from `develop` to `main`, require the profile validation check, and use a merge commit so the two persistent branches can remain aligned.

## 6. Configure runtime secrets

Daily public discovery works with the repository token. Private activity and private-label discovery require:

- `PROFILE_ACTIVITY_TOKEN`;
- `PROFILE_PRIVATE_REPOSITORIES_JSON`.

Without both secrets, checked-in private aggregates are preserved rather than replaced with incomplete data.
