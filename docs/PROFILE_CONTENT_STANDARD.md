# Profile content standard

This profile follows a scan-first, evidence-deep structure.

## Presentation hierarchy

1. **Identity and positioning** — one role statement and a small set of focus areas.
2. **Current engineering focus** — version, condition, latest activity, and a concise engineering scope.
3. **Selected work** — the strongest projects with inspectable evidence and explicit boundaries.
4. **Engineering activity** — one rolling aggregate and period-level history, not per-project scorekeeping.
5. **Private work index** — approved project labels, versions, conditions, latest activity, and case-study access.
6. **Deep-dive case studies** — problem, architecture, decisions, evidence, limitations, and lessons.

## Metric policy

- Commit counts are context, not a quality score.
- Private activity is published only as one aggregate total for the selected portfolio set.
- Per-project private commit counts are queried transiently for aggregation and are never persisted or rendered.
- Activity labels state the time window and source so the numbers are not mistaken for lifetime contribution totals.
- Versions and development conditions are separate fields; a version number does not imply production readiness.

## Table policy

Tables are reserved for compact, comparable metadata. Long engineering explanations belong in prose or case studies.

The private project index uses only:

- project name;
- source-verified version;
- development condition;
- latest approved activity date;
- deep-dive availability.

## Case-study policy

A deep dive should include:

- context and problem;
- personal responsibility;
- architecture and data flow;
- key decisions and rejected alternatives;
- failure modes and testing;
- inspectable evidence;
- limitations and privacy boundaries;
- lessons and next engineering decisions.

Private projects use sanitized case studies. They must not reveal repository URLs, branches, SHAs, commit messages, credentials, production data, or internal infrastructure.

## References

- GitHub profile guidance: https://docs.github.com/en/account-and-profile/concepts/personal-profile
- GitHub README guidance: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- GitHub table formatting: https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-tables
