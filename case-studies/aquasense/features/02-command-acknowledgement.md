# Acknowledged Command Workflow

## Problem

A successful HTTP response or MQTT publish confirms only that software accepted a request. It does not confirm that a relay moved or that the physical system reached the requested state.

## State model

```text
requested -> queued -> published -> acknowledged -> applied
                            |              |
                            v              v
                          failed         timeout
```

## Design

- The web layer creates a command request with a stable identifier.
- The device bridge publishes the normalized command to the expected device topic.
- The UI displays a pending state while acknowledgement is outstanding.
- The device acknowledgement references the command identifier and reports the resulting state.
- A timeout closes the pending state without pretending the physical action completed.
- Audit records retain actor, target device, requested action, timestamps, and final status.

## Why this matters

The distinction makes failure readable to operators and prevents optimistic UI state from becoming an unsafe operational claim.

## Trade-off

Acknowledgement adds protocol complexity and requires firmware or edge-controller cooperation. The alternative—assuming publish equals success—is simpler but unreliable for physical control.

## Commissioning note

Software acknowledgement cannot replace electrical verification. Relay voltage, socket, driver/interface circuit, contact load, protection, and fail-safe behavior must be checked before commissioning.
