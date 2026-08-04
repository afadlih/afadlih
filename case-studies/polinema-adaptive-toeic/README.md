# Polinema Adaptive TOEIC

**Status:** pilot-operations release candidate
**Role:** Fullstack Developer

Polinema Adaptive TOEIC combines micro-learning, assessments, deterministic mastery updates, content governance, research cohorts, and anonymous exports for a campus pilot context.

## Problem

An adaptive learning pilot needs learning features and research operations to agree on participant identity, consent, cohort assignment, evidence, content versions, and export rules.

## Product flow

```text
Roster / registration -> Consent and cohort -> Learning -> Assessment
  -> mastery evidence -> deterministic recommendation -> research export
```

## Implementation focus

- Students use NIM-based access; staff roles use NIP-based access.
- Assessment attempts support autosave, expiry, scoring, and mastery evidence.
- Recommendation ordering remains deterministic; Gemini is only used for guarded explanatory assistance.
- Content uses draft, review, publish, archive, and version history states.
- Research operations cover cohorts, freeze, exclusions, survey data, audit, and anonymous exports.

## Deep dives

1. [Adaptive Assessment and Mastery Evidence](features/01-adaptive-assessment.md)
2. [Research Cohort Operations](features/02-research-operations.md)
3. [Versioned Content Workflow](features/03-content-validation.md)

## Current limits

- SMTP production, SSO or SIAKAD integration, and centralized object storage remain external integration work.
- The current state is for pilot preparation, not institution-wide production use.
