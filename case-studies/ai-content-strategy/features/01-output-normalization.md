# Structured Output Normalization

## Problem

Model output may arrive as a valid object, nested payload, JSON inside a code fence, legacy response, or unstructured text. Rendering those forms directly would make the UI fragile.

## Source-verified approach

At the pinned public commit, `lib/result-utils.ts` defines runtime guards for supported result shapes and a parser that normalizes model text before accepting it as application state.

```text
unknown payload
  -> supported object guard
  -> nested data guard
  -> text cleanup and JSON parse
  -> legacy fallback
  -> stable ResultState
```

## Validation responsibilities

- Confirm required fields and supported variation types.
- Ensure lists contain values of the expected type.
- Restrict the selected variation index to the valid range.
- Support both current and previous response contracts during migration.
- Keep fallback behavior readable when structured parsing fails.

## Trade-off

Runtime guards duplicate some compile-time types, but external model output is not protected by TypeScript at runtime. The duplication is justified at the trust boundary.

## Evidence

See the pinned paths in [the source-verification record](../evidence/source-verification.md).
