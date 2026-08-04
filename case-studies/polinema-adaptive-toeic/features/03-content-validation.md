# Feature Deep Dive — Versioned Content and Expert Validation

## Context

Editing published learning material in place can invalidate previous assessments and make research results difficult to interpret. Content needs a lifecycle and immutable historical versions.

## Content states

```text
draft -> in review -> approved -> published -> archived
              |-> changes requested
```

A new edit creates a version rather than overwriting the content used by earlier attempts.

## Validation record

Expert review can capture rubric criteria, scores, notes, decision, reviewer identity, and revision. The system keeps the decision tied to the exact content version that was inspected.

## Key decisions

- Separate authoring from approval permissions.
- Prevent an unapproved version from replacing published material.
- Preserve historical question and lesson versions referenced by attempts.
- Make “changes requested” an actionable state rather than an informal comment.
- Keep publication and archival operations auditable.

## Trade-off

Versioned content increases storage and workflow complexity, but it preserves the meaning of historical assessment evidence and avoids silent changes during a pilot.

## Boundary

The case study describes the controlled workflow without publishing private teaching material or reviewer records.
