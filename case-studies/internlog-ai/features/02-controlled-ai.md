# Controlled AI Review

## Purpose

Use AI to improve clarity and completeness without allowing it to become the source of internship facts.

## Allowed behavior

- Identify vague or incomplete descriptions.
- Ask targeted follow-up questions.
- Suggest clearer wording from existing facts.
- Flag inconsistencies between a record and its selected category.
- Explain why a suggestion is being made.

## Disallowed behavior

- Invent activities, tools, outcomes, or responsibilities.
- Replace the original record without user approval.
- Mark a document ready when required evidence is absent.
- Present uncertain model output as verified fact.

## Control flow

```text
record -> validation -> AI request -> structured suggestion -> user review -> accept/reject/edit
```

## Failure handling

Model errors, invalid output, quota limits, and unavailable services should return a readable state while preserving the user's original data.

## Trade-off

A controlled review flow is slower than one-click generation, but it protects factual integrity and makes the system useful for real documentation rather than synthetic activity creation.
