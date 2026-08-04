# Feature Deep Dive — MQTT Realtime Telemetry

## Context

A weather-sensitive device needs more than a sensor chart. The interface must explain which device produced the data, when it was observed, what operating mode is active, and whether a command was acknowledged.

## Topic boundary

The documented target contract separates concerns per device:

```text
smart-clothesline/{deviceId}/telemetry
smart-clothesline/{deviceId}/status
smart-clothesline/{deviceId}/command
smart-clothesline/{deviceId}/ack
smart-clothesline/{deviceId}/health
```

This avoids mixing telemetry, control intent, and health events in one ambiguous stream.

## UI state

The dashboard normalizes incoming payloads into an operational model containing sensor readings, mode, clothesline state, source timestamp, and freshness. The interface should render loading, live, stale, offline, unknown, and fault conditions explicitly.

## Command behavior

User actions such as open, close, automatic mode, or manual mode are published as commands. The UI tracks pending state until an acknowledgement or timeout arrives. Sending the MQTT message is not treated as proof that the actuator moved.

## Trade-off

MQTT provides low-latency decoupling, but it requires topic governance, reconnect handling, payload validation, and a clear retained-message policy. The project documents these boundaries rather than treating realtime delivery as automatically reliable.

## Inspectable source

The public design at commit `8d61b3e1b1b94e27434ef5d02b2ecba91adbdd82` documents the topic contract, telemetry schema, command flow, and acknowledgement boundary.
