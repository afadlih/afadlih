# Document Studio Readiness

## Goal

Show whether the complete documentation package is ready before users generate files or submit reports.

## Readiness domains

- Profile and internship identity data.
- Daily activity coverage.
- Weekly logbook completeness.
- Evidence references.
- Final-report preparation.
- Backup/export readiness.

## Status model

```text
complete | incomplete | stale | blocked | not-applicable
```

Each status should include a reason and a direct path to the record or configuration that needs attention.

## Design decisions

- Readiness is calculated from explicit rules, not a single percentage without explanation.
- Stale documents are separated from missing documents.
- Blocking issues prevent final export, while warnings remain visible but non-blocking.
- Preview occurs before final file generation.
- AI suggestions do not override deterministic readiness rules.

## Trade-off

Detailed readiness checks require more domain rules and test coverage, but they reduce late-stage document failure and make the workflow understandable to non-technical users.
