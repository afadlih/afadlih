# Feature Deep Dive — Deterministic CSV Mapping and AI Fallback

## Context

A batch row can contain explicit respondent data, human overrides, reusable business rules, and fields that require generated text. Treating all of those sources as equivalent would make the final answer difficult to explain or reproduce.

## Value precedence

```text
Manual override
  -> CSV entry identifier
  -> CSV semantic label mapping
  -> deterministic rule
  -> AI fallback
  -> final validation
```

The first valid source wins. AI is only considered for unresolved fields and cannot replace a valid manual or CSV value.

## Traceability

Each planned field carries metadata such as:

- resolved value;
- selected source;
- original column or rule reference;
- validation result;
- warning or blocker reason.

This trace lets the operator answer “why will this value be submitted?” before execution starts.

## Trade-offs

Entry-identifier templates are less friendly to edit manually, but they are more stable when question wording changes. Semantic label matching is easier for humans but requires ambiguity detection. Supporting both is useful as long as their precedence is explicit.

## AI boundary

Generated fallback remains constrained by the question type, allowed options, required format, and project validation rules. A generated value that fails those checks becomes a blocker rather than being submitted optimistically.

## Public evidence boundary

The private mapping implementation and real respondent files are not published. The case study states the design contract without exposing personal data or credentials.
