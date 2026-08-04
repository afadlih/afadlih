# Optional Evidence Upgrade Checklist

The current profile uses reviewed documentation and source-level verification appropriate to each project's visibility. Additional evidence is optional and may only be published after it is current, reproducible, and privacy-safe.

## Capture requirements

- tie test output to a source commit or release identifier;
- state the command, environment, expected result, and observed result;
- use representative sample data rather than personal, student, patient, or company data;
- remove tokens, cookies, internal hosts, credentials, QR secrets, and infrastructure details;
- ensure screenshots remain readable at GitHub content width;
- explain what the evidence proves and what it does not prove.

## Useful future evidence

### InternLog AI

Daily-record workflow, weekly readiness, AI review states, document validation, DOCX output, and reproducible CI results.

### AquaSense

Container health, device provisioning, telemetry freshness, command acknowledgement and timeout states, alarm lifecycle, and commissioning checks.

### FormAI

Form analysis, deterministic mapping trace, dry-run blockers, execution progress, row-level diagnostics, and frontend/backend test results.

### Supporting projects

Use source-linked architecture decisions, integration tests, or deployment notes when they improve understanding. Do not add screenshots merely for decoration.

## Review decision

Evidence is publishable only when all answers are **yes**:

- Does it prove a specific implementation claim?
- Is it tied to a known revision?
- Is the content safe to publish?
- Does the case study explain its significance?
- Are limitations still stated accurately?
