# Recommendation and Trade-Off Reasoning

## Goal

Turn generated variations into an actionable decision with an explanation, not merely a ranked list.

## Source-verified response fields

The decision response includes a selected variation index, comparison summary, decision basis, trade-off analysis, optimized caption and hashtags, final recommendation, execution steps/tip, risk note, confidence level, and validation status.

## Flow

```text
validated variations
  -> comparison
  -> selected strategy
  -> optimization
  -> execution guidance
  -> risk and validation notes
```

## Design principle

Recommendation text should explain why a strategy won and what the user should do next. Risk and validation fields remain visible so polished copy does not hide uncertainty.

## Trade-off

More structure increases prompt and parsing complexity. It also gives the frontend stable sections and makes the recommendation easier to audit than a single long model response.

## Evidence

See the pinned API and result-normalization paths in [the source-verification record](../evidence/source-verification.md).
