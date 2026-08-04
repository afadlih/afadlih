# Feature Deep Dive — Form Analyzer

## Context

Google Forms can contain required questions, option sets, repeated labels, conditional sections, and field identifiers that are safer for submission than their visible wording. Starting automation from a URL alone would push these uncertainties into the execution phase.

## Responsibility

The analyzer converts the target form into a normalized model that later stages can reason about.

```text
Input:  target form URL
Output: form identity, questions, entry identifiers, types,
        required flags, options, warnings, and analysis revision
```

## Key decisions

- Treat successful analysis as an execution prerequisite.
- Preserve stable entry identifiers when available instead of relying only on visible labels.
- Return unresolved or unsupported structures as explicit warnings.
- Store enough revision context to detect when a previous mapping may be stale.
- Keep analysis read-only; it must never submit answers.

## Failure handling

An invalid URL, inaccessible form, unsupported field, or incomplete structure produces a blocked analysis state. The operator receives a reason and can retry after correcting access or form structure. The system should not continue by guessing a schema.

## Trade-off

Re-analysis adds an extra step, but it prevents stale templates from silently targeting the wrong fields. For bulk automation, this safety cost is preferable to faster but opaque execution.

## Public evidence boundary

This document describes the maintained workflow. Parser responses and target-form captures are not published because the project and its operational data are private.
