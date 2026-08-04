# Working Tree Audit and Final Direction

## Problems corrected

- The profile previously mixed README generation, website export, project discovery, candidate intake, and multiple reports in one repository.
- Decorative hero content competed with the actual engineering evidence.
- Three private projects were presented without a sufficiently explicit verification boundary.
- Candidate promotion could create structurally invalid records.
- Documentation described gates and outputs that no longer matched the implementation.
- The apply helper performed destructive cleanup before establishing a safe rollback path.
- Activity data lacked formal schemas and could use an unnecessary personal token.

## Final repository direction

- `portfolio/*.json` is the curated source of truth.
- `README.md` is the only public generated profile artifact.
- AquaSense and InternLog AI are private projects represented through sanitized documentation.
- AI Content Strategy is the public selected project with source evidence pinned to an immutable commit.
- FormAI remains an additional private case study; public supporting projects provide complementary code evidence.
- Activity automation reads an explicit public allowlist and does not create timestamp-only commits.
- The strict gate is expected to pass in the released package. Generated activity updates are proposed through pull requests rather than pushed directly to the protected branch.

## Deliberately removed

```text
website-export/
portfolio/site-config.json
portfolio/candidate-projects.json
scripts/export_website_data.py
scripts/validate_website_export.py
scripts/promote_candidate.py
scripts/validate_candidates.py
scripts/generate_candidate_report.py
scripts/discover_public_repos.py
.github/workflows/website-export.yml
.github/workflows/candidate-intake.yml
assets/profile/hero-monochrome-banner.png
```

The candidate workflow was removed rather than patched because manual curation is safer and clearer for a seven-project profile repository.
