<!-- PROFILE-README:GENERATED -->
<!-- Edit portfolio/*.json, then run: python scripts/portfolio_ci.py update -->

<p align="center">
  <img src="assets/profile-banner.svg" width="100%" alt="Animated engineering profile banner for Ahmad Fadlih Wahyu Sardana" />
</p>

<p align="center"><strong>Full-Stack Developer building reliable AI workflows, automation systems, and on-premise IoT products</strong></p>
<p align="center">
  <code>AI WORKFLOWS</code> ·
  <code>FULL-STACK SYSTEMS</code> ·
  <code>ON-PREMISE IOT</code> ·
  <code>SYSTEM INTEGRATION</code>
</p>
<p align="center">
  <a href="https://ahmad-fadlih-portfolio.vercel.app">Portfolio</a> ·
  <a href="https://id.linkedin.com/in/ahmad-fadlih-wahyu-sardana-706933283">LinkedIn</a> ·
  <a href="https://github.com/afadlih">GitHub</a>
</p>
<p align="center">
  <a href="#current-engineering-focus">Current focus</a> ·
  <a href="#selected-work">Selected work</a> ·
  <a href="#github-activity">GitHub activity</a> ·
  <a href="#contact">Contact</a>
</p>

> I turn complex operational flows into products with explicit states, validated outputs, observable failures, and practical documentation.

## What I build

**AI product workflows**  
Structured model output, validation, human review, deterministic fallback, and useful diagnostics.

**Operational full-stack systems**  
Clear domain states, role-aware interfaces, reliable data flows, testing, and maintainable delivery.

**On-premise and realtime integration**  
MQTT boundaries, device state, acknowledged commands, deployment constraints, and operator visibility.

## Current engineering focus

| Active project | Version / stage | Latest update | Current engineering focus |
| --- | --- | --- | --- |
| [AquaSense](case-studies/aquasense/README.md) | `2.3.0-rc15` | 2026-08-05 | Raspberry Pi 3B+ edge baseline, seven-container on-premise topology, provisioning safety, release hardening, and operator documentation. |
| **AquaSense Hardware Simulator** | `2.3.0-rc5` | 2026-07-31 | Standalone Wokwi and ESP32 MicroPython simulation, MQTT bridge, firmware workflow, telemetry readiness, and Core reconciliation. |
| [OrthoBreath](case-studies/orthobreath/README.md) | `1.7.2` | 2026-07-31 | MQTT device topics, session policies, dental and breathing examination flows, Firebase mapping, demo boundaries, and regression coverage. |
| [InternLog AI](case-studies/internlog-ai/README.md) | `2.8.1` | 2026-07-29 | Adaptive mentor language for IT and non-IT internships, logbook reliability, document auditing, multi-user foundations, and AI regression tests. |
| **SkripsiOps AI** | `Foundation` | 2026-07-30 | Evidence-first thesis workspace bootstrap with Docker environments, initial architecture, documentation, contribution rules, and automated tests. |
| [Polinema Adaptive TOEIC](case-studies/polinema-adaptive-toeic/README.md) | `Release candidate` | 2026-07-23 | Institutional authentication, password-reset approval, registration rosters, research freeze controls, media validation, RBAC, and audit logging. |

The table above is a curated snapshot of repositories currently under active development. Dates reflect the latest accessible commits reviewed for this profile, not fabricated deployment claims.

## Selected work

### 1. AquaSense

**On-Premise IoT Operations · Private source · Sanitized case study**

On-premise IoT operations platform for telemetry, alarms, device provisioning, acknowledged commands, audit records, and role-based control.

`Next.js` `React` `TypeScript` `MUI` `Go` `EMQX` `MQTTS` `Docker Compose`

**Inspectable evidence**

- Sanitized architecture and device-to-dashboard flow documented as a public case study
- Command lifecycle distinguishes request, delivery, acknowledgement, resulting state, and timeout
- Deployment and commissioning boundaries are stated instead of presented as completed production work

<details>
<summary><strong>Architecture, decisions, and current boundaries</strong></summary>

**Problem**  
Water monitoring and relay control need a trusted local workflow where telemetry, device identity, commands, acknowledgements, and operator actions remain visible.

**What I built**  
Designed a coarse-grained on-premise architecture that keeps device identity, telemetry, command acknowledgement, privileged access, and operational state explicit.

**Deep-dive topics**

- Telemetry Ingestion and Device Identity Boundary
- Acknowledged Command and Configuration Workflow
- Coarse-Grained On-Premise Deployment

**Current boundaries**

- Release-candidate software still requires target-server validation, company PKI, firewall review, backup testing, and device commissioning.
- Relay coil voltage, socket, driver circuit, load behavior, and fail-safe wiring must be verified before hardware commissioning.

</details>

[Case study](case-studies/aquasense/README.md)

---

### 2. InternLog AI

**AI Workflow Product · Private source · Sanitized case study**

Internship workflow product connecting daily logs, weekly logbooks, controlled AI review, document readiness, and export preparation.

`Next.js` `React` `TypeScript` `Firebase Auth` `Firestore` `Firebase Admin SDK` `Vitest`

**Inspectable evidence**

- Daily records remain the source of truth for downstream documents
- AI-assisted review is separated from factual records and requires user approval
- Document readiness exposes incomplete, stale, and blocked areas before export

<details>
<summary><strong>Architecture, decisions, and current boundaries</strong></summary>

**Problem**  
Internship records are often scattered across daily notes, weekly reports, evidence files, and final-document requirements.

**What I built**  
Built a traceable workflow where daily records become reviewed weekly outputs and AI suggestions remain optional, bounded, and user-approved.

**Deep-dive topics**

- Daily Log to Weekly Logbook Lifecycle
- Controlled AI Mentor and Recommendation Flow
- Document Studio Readiness Audit

**Current boundaries**

- Multi-user support remains a limited beta rather than a commercial SaaS release.
- File evidence and larger document assets are still handled outside Firestore to stay within the intended free-tier architecture.

</details>

[Case study](case-studies/internlog-ai/README.md)

---

### 3. AI Content Strategy

**AI Decision System · Public source · Source-verifiable**

Public decision-support application that generates multiple content strategies, validates structured model output, compares trade-offs, and recommends an execution path.

`Next.js 14` `TypeScript` `Tailwind CSS` `Gemini API` `Structured Output`

**Inspectable evidence**

- Public source is pinned to commit d3aedfd1dc8e76a29bf51a14fc12da4a77219de0 in the case-study evidence record
- Runtime type guards validate decision, previous-strategy, and legacy response shapes before rendering
- The API normalizes model output and exposes comparison, recommendation, execution, validation, and risk fields

<details>
<summary><strong>Architecture, decisions, and current boundaries</strong></summary>

**Problem**  
Many AI content tools return one answer without making trade-offs or selection logic visible.

**What I built**  
Implemented a typed Next.js and Gemini workflow with runtime guards, normalized result states, three strategy variants, scoring, recommendation, fallback behavior, and risk notes.

**Deep-dive topics**

- Structured Gemini Output Normalization
- Multi-Strategy Scoring Matrix
- Decision Recommendation and Trade-Off Reasoning

**Current boundaries**

- Model output still requires human judgment.
- Heuristic scoring is not a substitute for real campaign measurement.

</details>

[Repository](https://github.com/afadlih/AI-Content-Strategy---SEO-Assistant--Web-App-) · [Case study](case-studies/ai-content-strategy/README.md)

## Additional case study

### 4. FormAI

**AI Automation · Private source · Sanitized case study**

AI-assisted Google Form automation platform with form analysis, deterministic CSV mapping, AI fallback, validation, execution modes, and row-level diagnostics.

`Python` `FastAPI` `Next.js` `TypeScript` `Gemini API` `Selenium` `CSV Contracts`

**Inspectable evidence**

- Analyze-first workflow before execution
- Deterministic CSV mapping before AI fallback
- Dry-run preview before mutating submission
- Duplicate guard and row-level diagnostics
- Fast HTTP mode plus browser execution mode

<details>
<summary><strong>Architecture, decisions, and current boundaries</strong></summary>

**Problem**  
Repeated Google Form submission is slow, inconsistent, and risky when many respondents, rules, or answer sources are involved.

**What I built**  
Designed an operator-facing workflow where users can analyze a form, prepare structured data, preview mapping, execute safely, and inspect what happened per row.

**Deep-dive topics**

- Form Analyzer
- Deterministic CSV Mapping and AI Fallback
- Dry-Run Preview, Validation, and Diagnostics

**Current boundaries**

- The form must be analyzed again when its structure changes.
- Some forms still require browser execution instead of the faster HTTP submission path.

</details>

[Case study](case-studies/formai/README.md)

## Experience & recognition

- **PT Pindad (Persero) — Intern** (Current)  
  Working on software and system-integration tasks. Public descriptions remain NDA-safe and exclude internal infrastructure, credentials, and operational data.
- **PKM-KC 2026 Funding Recipient — OrthoBreath**  
  Full-stack contributor to a five-student health-tech prototype covering application flow, device-related work, testing support, and project communication. No clinical-readiness claim is made.

## More projects

| Project | What it demonstrates | Access |
| --- | --- | --- |
| **Smart Clothesline IoT** | Realtime dashboard for sensor telemetry, clothesline state, automation rules, alerts, history, and operational diagnostics. | [Repository](https://github.com/afadlih/smart-clothesline-iot-system) · [Case study](case-studies/smart-clothesline/README.md) |
| **Polinema Adaptive TOEIC** | Responsive TOEIC micro-learning platform with institutional roles, research cohorts, content workflows, assessments, deterministic mastery updates, and research exports. | [Case study](case-studies/polinema-adaptive-toeic/README.md) |
| **OrthoBreath** | Prototype dashboard for child profiles, dental capture, breathing-session monitoring, scan history, notifications, and combined reporting. | [Case study](case-studies/orthobreath/README.md) |

## GitHub activity

<p align="center">
  <img src="assets/public-activity.svg" width="100%" alt="Generated public commit activity from allowlisted repositories" />
</p>

<sub>The chart is generated inside this repository from a bounded GitHub public commit API sample. Private repositories are excluded, and the values are not presented as lifetime totals.</sub>

## Public work, recently updated

<!-- PROFILE-ACTIVITY:START -->
| Repository | Last public update | Language |
| --- | --- | --- |
| [GitHub Profile System](https://github.com/afadlih/afadlih) | 2026-08-05 | Python |
| [Smart Clothesline IoT](https://github.com/afadlih/smart-clothesline-iot-system) | 2026-06-10 | TypeScript |
| [Ahmad Fadlih Portfolio](https://github.com/afadlih/Ahmad-Fadlih-Portfolio) | 2026-05-22 | TypeScript |
| [AI Content Strategy](https://github.com/afadlih/AI-Content-Strategy---SEO-Assistant--Web-App-) | 2026-04-27 | TypeScript |
| [Next.js Framework Practice](https://github.com/afadlih/Pemrograman_Berbasis_Framework_Semester_6) | 2026-04-16 | TypeScript |
<!-- PROFILE-ACTIVITY:END -->

This snapshot is generated from an allowlisted set of public repositories. Private repository metadata is never published by the updater.

## How I work

- Keep deterministic rules separate from AI fallback.
- Validate external and generated data before it reaches the UI or execution path.
- Represent pending, failed, blocked, and completed states explicitly.
- Document limitations and deployment boundaries as carefully as features.
- Prefer evidence that can be inspected over decorative claims.

## Contact

Open to full-stack, AI product engineering, workflow automation, and system-integration opportunities.

[Portfolio](https://ahmad-fadlih-portfolio.vercel.app) · [LinkedIn](https://id.linkedin.com/in/ahmad-fadlih-wahyu-sardana-706933283)

<sub>Private projects are shown through sanitized case studies, not fabricated public demos.<br>Public projects include source-level evidence pinned to inspectable commits.<br>The current-focus snapshot was reviewed against accessible repository activity on 2026-08-05.<br>A professional public email is intentionally omitted until a durable address is configured.</sub>
