# OrthoBreath — PKM-KC 2026 Prototype

## Project context

OrthoBreath is a five-student health-tech prototype that received PKM-KC 2026 funding. The product concept connects parent accounts, child profiles, dental observations, breathing-session records, history, notifications, and combined reports.

**Role:** Full-stack contributor across application flow, device-related work, testing support, and project communication  
**Evidence level:** funded prototype; private implementation

## Product boundary

```text
Parent account
  -> child profile
  -> dental capture and breathing-session records
  -> history and notification flow
  -> combined report
  -> future prediction-service boundary
```

The frontend uses Firebase Authentication and Firestore-backed records. Prediction behavior remains behind an API-ready boundary and is mock-first until a model, dataset, evaluation protocol, consent model, and privacy controls are completed.

## Engineering focus

- keep parent and child identity relationships explicit;
- separate captured observations from generated or predicted interpretation;
- preserve chronological scan and session history;
- design a combined report contract without implying clinical diagnosis;
- keep future model integration replaceable behind a service boundary;
- document consent, privacy, and evaluation as unfinished requirements.

## What the funding proves

Funding is a program achievement and confirms the proposal advanced through its funding process. It does not by itself prove clinical effectiveness, medical-device readiness, model accuracy, or production adoption.

## Current limitations

- The prototype is not a released medical device.
- No clinical accuracy claim is made.
- Model integration and validation remain incomplete.
- Health-data consent, retention, access, and privacy controls require formal completion before real-world use.
- Any device or capture workflow requires supervised testing and domain-expert review.
