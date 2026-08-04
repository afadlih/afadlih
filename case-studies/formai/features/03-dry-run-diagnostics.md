# Feature Deep Dive — Dry-Run Preview and Diagnostics

## Context

Bulk submissions are difficult to reverse. Validation that happens only after a failed run is too late, especially when one malformed row can hide among many successful rows.

## Preview contract

Dry run executes the planning pipeline without sending answers. It should expose:

- final value and source for every field;
- missing required values;
- unsupported option or format errors;
- duplicate or already-processed rows;
- selected execution mode;
- planned, blocked, and warning counts.

## State model

```text
analyzing -> mapping -> validating -> ready
                              |-> blocked
ready -> running -> completed
              |-> partial
              |-> failed
```

Preview and execution are separate states. A blocked row cannot enter the run queue until the operator changes its input or explicitly excludes it.

## Diagnostics

Run diagnostics are recorded per row and per stage so a failure can distinguish mapping, validation, transport, browser interaction, and response confirmation. A summary count alone is not enough for recovery.

## Recovery behavior

Retry should target failed rows rather than resubmitting the entire batch. Duplicate guards and run identifiers reduce accidental repeated submissions.

## Public evidence boundary

No live form, respondent data, browser session, or production log is included in this public profile. The documented states are the safe portfolio-level representation of the private implementation.
