# Feature Deep Dive — Automation Rules and Safety Fallback

## Context

A device exposed to rain cannot depend entirely on the dashboard, internet connection, MQTT broker, or cloud database for immediate protective behavior.

## Layered control

```text
Firmware
  -> immediate rain fallback and actuator safety
MQTT + dashboard
  -> normal commands, mode changes, acknowledgement visibility
Backend
  -> history, alerts, configuration, notification orchestration
```

The immediate rule remains local:

```text
IF rain_detected = true
THEN retract clothesline locally
```

## Why the boundary matters

Keeping the fallback in firmware reduces dependence on remote services during a network outage. The dashboard still needs to report that local action after connectivity returns, rather than pretending every state change originated from a user command.

## Notification boundary

Telegram sends operational alerts and summaries. It does not accept hardware-control commands, publish MQTT commands, or act as a fallback command queue. This reduces the number of control surfaces that must be secured and reconciled.

## Trade-off

Local autonomy can create state divergence while the device is disconnected. Reconnection therefore requires status publication and reconciliation before the dashboard presents a confirmed state.

## Inspectable source

The public repository design pins the local rain fallback, dashboard control surface, Telegram notification-only decision, and failure-handling expectations to an inspectable revision.
