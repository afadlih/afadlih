# Smart Clothesline — Source Verification

**Repository:** `afadlih/smart-clothesline-iot-system`  
**Pinned commit:** `8d61b3e1b1b94e27434ef5d02b2ecba91adbdd82`

## Inspected implementation documentation

- `docs/DESIGN.md`

At the pinned revision, the document defines:

- ESP32, MQTT, Next.js, Firestore, Telegram, and historical analytics boundaries;
- device-scoped telemetry, status, command, acknowledgement, and health topics;
- explicit offline, stale, fault, and unknown operational states;
- pending-command timeout and reconnect expectations;
- local firmware rain fallback;
- Telegram as notification-only rather than a command path.

## Verification limit

This is source-level verification of the documented design, not a claim that physical hardware commissioning, latency targets, or every integration path has passed production testing.
