# Coarse-Grained On-Premise Deployment

## Goal

Keep important architectural boundaries without turning a small on-premise deployment into an unnecessarily large microservice platform.

## Packaging approach

The system groups related responsibilities into a limited set of deployable containers while preserving logical separation between web access, domain behavior, identity/access, device communication, data storage, broker, and reverse proxy concerns.

```text
reverse proxy
  -> web / BFF
  -> core domain bundle
  -> access bundle
  -> device bridge
  -> MQTT broker
  -> database
```

## Operational requirements

- Versioned container images and repeatable compose configuration.
- Explicit health checks and dependency readiness.
- Environment validation before startup.
- Non-default host port options for restricted corporate environments.
- TLS/PKI integration that can use organization-issued certificates.
- Backup, restore, log retention, and incident-oriented diagnostics.

## Trade-off

Coarse-grained deployment reduces operational overhead compared with many independently deployed services. It also creates larger failure domains, so internal module boundaries, tests, and observability remain important.

## Release boundary

A local healthy compose run is not equivalent to production readiness. Target-server resources, firewall policy, certificate handling, backup restore, broker security, and hardware commissioning must be validated in the final environment.
