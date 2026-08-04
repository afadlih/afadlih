# Daily-to-Weekly Logbook Lifecycle

## Goal

Convert daily factual records into weekly documentation without duplicating or silently rewriting the source data.

## State progression

```text
draft -> saved daily record -> weekly selection -> readiness check -> snapshot -> preview -> export preparation
```

## Data ownership

A daily record owns the activity date, description, category, evidence reference, and review state. A weekly logbook references eligible daily records and stores a snapshot only when a stable document version is needed.

## Validation

- Required dates and activity descriptions must exist.
- A record cannot be counted twice in the same weekly period.
- Stale or changed source records are surfaced before export.
- Preview reflects the exact snapshot intended for document generation.
- Missing evidence is shown as a readiness issue, not hidden.

## Trade-off

Referential data is easier to keep consistent, while document snapshots improve reproducibility. Using both requires clear rules about when a snapshot becomes immutable and when regeneration is required.

## Outcome

The document flow remains traceable from the weekly output back to the daily factual records that support it.
