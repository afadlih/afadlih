# Feature Deep Dive — Adaptive Assessment and Mastery Evidence

## Context

An adaptive learning recommendation must be explainable from stored learning evidence. A generated suggestion without traceable assessment data would be difficult to reproduce in a research setting.

## Assessment flow

```text
attempt created
  -> answers autosaved
  -> submission or expiry
  -> deterministic scoring
  -> evidence recorded by skill
  -> mastery updated
  -> recommendation ordered
```

## Key decisions

- Keep scoring and mastery updates deterministic.
- Persist attempt state so interrupted sessions can recover safely.
- Separate raw answers, scoring output, and mastery evidence.
- Tie recommendation changes to recorded evidence rather than free-form model output.
- Use AI only for guarded explanatory assistance, not as the authoritative score source.

## Failure and edge states

The workflow distinguishes active, submitted, expired, incomplete, and invalid attempts. Repeated submission is idempotent or rejected explicitly so an assessment cannot update mastery twice.

## Research value

Because evidence and recommendation order are reproducible, researchers can later explain why a learner received a particular next activity without reconstructing an opaque prompt conversation.

## Boundary

This private case study describes the domain model. It does not publish student records, institution credentials, or unreviewed outcome metrics.
