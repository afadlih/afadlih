# Feature Deep Dive — Device Health and Heartbeat Monitoring

## Context

Displaying the most recent sensor value without its age can mislead the operator. A dry reading from an offline device is not equivalent to a currently verified dry condition.

## Health model

The project separates operational state from data-health state. Reference conditions include:

```text
LIVE -> recent heartbeat and telemetry
STALE -> data exceeded freshness threshold
OFFLINE -> heartbeat unavailable beyond offline threshold
FAULT -> device reports a fault or invalid state
UNKNOWN -> health cannot yet be determined
```

## Detection flow

1. The device publishes telemetry or health events with a timestamp.
2. The dashboard or monitoring service records the latest observation per device.
3. Freshness is recalculated against documented thresholds.
4. State changes create visible alerts and may trigger notifications.
5. Reconnection clears or transitions the alert through an explicit lifecycle.

## Design decision

The last known sensor value can remain visible for context, but it must be visually separated from the current health conclusion. This preserves useful history without presenting stale data as live truth.

## Failure handling

Reconnect attempts use backoff; parsing or schema errors are recorded separately from connectivity errors. Firestore write failure should not change the physical device state, and notification failure should not be confused with device failure.

## Inspectable source

The pinned public design documents offline and stale states, heartbeat-derived alerts, reconnect behavior, and the separation between realtime control and stored history.
