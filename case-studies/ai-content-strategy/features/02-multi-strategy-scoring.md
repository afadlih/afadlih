# Multi-Strategy Scoring

## Goal

Make content strategy trade-offs visible by returning multiple distinct approaches instead of one opaque answer.

## Strategy set

- Emotional: prioritizes resonance and audience feeling.
- Educational: prioritizes clarity, usefulness, and explanation.
- Viral: prioritizes hook strength and share-oriented framing.

## Decision fields

The typed result includes engagement score, hook strength, CTA strength, reasoning, weaknesses, and improvement suggestions for each variation. The API also exposes comparison and optimization fields for the selected direction.

## Product behavior

```text
three variations -> validate each shape -> compare dimensions -> select index -> explain basis -> optimize final output
```

## Trade-off

The numbers are structured heuristics, not observed campaign metrics. Their value is consistency and comparability inside the product, not scientific prediction of reach or conversion.

## Evidence boundary

The public source verifies that the fields and validation flow exist. It does not verify the real-world accuracy of the scores.
