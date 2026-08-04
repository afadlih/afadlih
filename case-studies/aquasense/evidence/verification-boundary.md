# AquaSense — Public Verification Boundary

## Evidence level

`documented-private`

AquaSense is presented as a sanitized private-system case study. The public profile documents architecture, device boundaries, command state, deployment constraints, and commissioning risks without exposing company infrastructure, credentials, private source, or operational data.

## Claims supported by this repository

- Telemetry enters through an MQTT device boundary before reaching application services and the operator interface.
- Command state distinguishes request, transport, acknowledgement, resulting state, failure, and timeout.
- Device provisioning and privileged access use explicit state and role boundaries.
- The software is described as release-candidate/on-premise work that still requires target-host validation, PKI, firewall, backup, and hardware commissioning checks.

## Claims intentionally excluded

- Production deployment at PT Pindad or another organization.
- Industrial certification, safety certification, or hardware commissioning completion.
- Relay wiring correctness before coil voltage, socket, driver, load, protection, and fail-safe behavior are verified.
- Public performance, uptime, or field-reliability metrics.

## Privacy review

No internal IP address, hostname, credential, certificate, company network diagram, private repository metadata, or operational dataset is published.
