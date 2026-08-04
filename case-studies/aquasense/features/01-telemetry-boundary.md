# Telemetry and Device Identity Boundary

## Context

Telemetry is useful only when the platform can identify which device produced it, whether the message is structurally valid, and whether the data is fresh enough to influence an operator decision.

## Boundary

```text
sensor/device -> MQTT topic -> device bridge -> validated domain event -> application state
```

The device bridge is responsible for translating transport-level messages into application-level events. This keeps MQTT topic rules, payload validation, and device identity outside the web interface and core presentation flow.

## Responsibilities

- Validate the expected tenant/site/device topic structure.
- Reject or quarantine malformed payloads instead of silently coercing them.
- Attach device identity and message time to the normalized event.
- Preserve last-seen and freshness information so stale data is not presented as current truth.
- Separate simulator identity from commissioned hardware identity.

## Failure states

- Unknown device or invalid topic.
- Payload schema mismatch.
- Stale timestamp or repeated message.
- Broker connection loss.
- Device heartbeat timeout.

## Trade-off

A strict boundary adds validation code and explicit error states, but it prevents the rest of the product from depending on raw broker messages and ambiguous device identity.

## Public evidence boundary

This document describes the architecture decision and supported public claim. It does not publish private topic names, credentials, certificates, or a production broker configuration.
