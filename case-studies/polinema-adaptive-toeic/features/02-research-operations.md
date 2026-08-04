# Feature Deep Dive — Research Cohort and Consent Operations

## Context

A campus pilot combines product operations with research controls. Participant identity, consent, cohort assignment, exclusions, and study timing must remain consistent with the learning records.

## Operational model

```text
invitation
  -> participant code
  -> consent decision
  -> eligibility check
  -> cohort assignment
  -> pre-test / intervention / post-test
  -> exclusion or completion
  -> anonymized export
```

## Key decisions

- Use study-specific participant identifiers for research operations.
- Store consent and eligibility as explicit states, not notes.
- Freeze cohort membership before the pilot to prevent silent reassignment.
- Record exclusion reason and audit metadata without deleting the underlying operational history.
- Separate identifiable operational data from the anonymous export shape.

## Access boundary

Students, lecturers, administrators, researchers, and validators do not receive the same capabilities. Server-side authorization protects cohort changes and exports; hiding controls in the UI alone is insufficient.

## Export behavior

Research exports select approved fields, replace direct identity with study codes, and preserve enough provenance to reproduce the dataset version. Exporting a CSV is treated as a controlled operation with audit information.

## Boundary

The public profile does not expose rosters, consent records, research datasets, or institution-specific integration details.
