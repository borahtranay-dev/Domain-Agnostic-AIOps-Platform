# Phases.md
# AIOps Self-Healing Platform — Phased Development Plan

> **Planning baseline:** Current Project Review Report.  
> The project is being developed as a **domain-agnostic AIOps self-healing platform**, with the **e-commerce system as the first reference implementation**.
>
> Development follows a strict sequential phase plan from **P0 through P12**. Each phase has a defined outcome, and later-phase implementation should not begin before the current phase is formally complete.

---

# 1. Purpose

This document defines the project's phased development plan.

The phases provide the controlled progression from:

```text
Governance
   ↓
Technical Foundation
   ↓
Shared Contracts / Domain Foundation
   ↓
Component Construction
   ↓
Incident Detection
   ↓
AI Diagnosis / RAG
   ↓
Remediation
   ↓
Developer Cockpit
   ↓
End-to-End Integration
   ↓
Hardening
   ↓
Staging
   ↓
Release
   ↓
Post-MVP Evolution
```

The purpose of this sequencing is to prevent the four team members and their AI coding assistants from independently building incompatible versions of the same system.

---

# 2. Development Governance

## 2.1 Sequential development

The project follows:

```text
P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10 → P11 → P12
```

A later phase should not be treated as active implementation work until the current phase is formally complete.

## 2.2 Why the project uses strict phases

The project consists of:

- four team members,
- four AI coding assistants,
- one shared codebase,
- multiple independently developed application components.

The sequential methodology provides a controlled point at which shared contracts and architectural decisions are established before parallel implementation.

---

# 3. Phase Status Summary

| Phase | Name | Goal | Status |
|---|---|---|---|
| P0 | Governance & Repository Bootstrap | Establish rules, ownership, repository structure | **COMPLETE** |
| P1 | Technical Foundation | Working local development environment; all applications boot and connect | **COMPLETE** |
| P2 | Contract & Domain Foundation | Shared API/event schemas, domain model, database schema | **NOT STARTED** |
| P3 | Parallel Component Construction | Each member builds their core component against shared contracts | **NOT STARTED** |
| P4 | Event & Incident Pipeline | Real webhook ingestion and incident lifecycle | **NOT STARTED** |
| P5 | AI Diagnosis & RAG | Real RAG pipeline analyzing real incidents | **NOT STARTED** |
| P6 | Remediation & GitHub Automation | AI-suggested fixes become real, human-approved GitHub PRs | **NOT STARTED** |
| P7 | Developer Cockpit | Full dashboard UI for the incident/approval workflow | **NOT STARTED** |
| P8 | End-to-End Integration | Full golden-path testing across all components | **NOT STARTED** |
| P9 | Hardening | Security, performance, and reliability pass | **NOT STARTED** |
| P10 | Staging | Staging environment, deployment pipeline, rollback demonstration | **NOT STARTED** |
| P11 | Release | Production release | **NOT STARTED** |
| P12 | Post-MVP | Ongoing evolution and scaling | **NOT STARTED** |

---

# 4. P0 — Governance & Repository Bootstrap

## Goal

Establish:

- project rules,
- ownership,
- repository structure,
- team conventions.

## Deliverables

The project should have:

- defined team ownership,
- repository structure,
- contribution conventions,
- collaboration rules for the four members and their AI coding assistants.

## Status

**COMPLETE**

---

# 5. P1 — Technical Foundation

## Goal

Establish a working local development environment in which the application's foundational components can boot and communicate.

## Technology foundation

The current project stack is:

- Backend API — Python 3.12 + FastAPI
- Background worker — Python 3.12 + RQ
- AI diagnosis engine — Python 3.12 + FastAPI + LangChain
- Frontend — TypeScript + Next.js / React
- Database — PostgreSQL
- Cache / message queue — Redis
- Containerization — Docker + Docker Compose
- CI/CD — GitHub Actions
- Version control/collaboration — Git / GitHub

## Current P1 state

The initial P1 foundation is complete:

- API skeleton boots,
- worker skeleton boots,
- AI-worker skeleton boots,
- web application skeleton boots,
- PostgreSQL connectivity is working,
- Redis connectivity is working,
- application communication has been checked,
- automated CI checks have been performed,
- manual end-to-end foundation testing has been performed.

## Important boundary

P1 foundation completion does **not** mean that the business functionality is complete.

The report explicitly states that:

- order handling is not implemented,
- real incident detection is not implemented,
- AI diagnosis is not implemented.

Those capabilities begin in later phases.

## Status

**COMPLETE / INITIAL FOUNDATION**

---

# 6. P2 — Contract & Domain Foundation

## Goal

Establish the shared foundation against which the remaining components will be built.

P2 must establish:

- shared API schemas,
- shared event schemas,
- generic domain model,
- database schema.

## Generic domain direction

The platform's reusable model includes concepts such as:

```text
Pipeline
PipelineRun
Service
Deployment
Environment
Event
Incident
Evidence
Diagnosis / RootCause
RemediationPlan
RemediationAction
Approval
Change / ExecutionResult
Verification
```

The e-commerce reference implementation must not turn its business concepts into mandatory universal platform entities.

## Why P2 is critical

P2 is the point at which the shared contracts and domain foundation are established before the project enters parallel component construction.

## Status

**NOT STARTED**

---

# 7. P3 — Parallel Component Construction

## Goal

Each member builds their core component against the shared contracts established in P2.

## Team responsibilities

### Rudra — AI / RAG Lead

Primary responsibility:

- AI diagnosis engine,
- `apps/ai-worker`,
- RAG pipeline,
- LLM integration,
- remediation-suggestion generation.

### Saurav — DevOps Lead

Primary responsibility:

- infrastructure,
- containerization,
- CI/CD pipeline,
- deployment.

Later, from P10 onward:

- staging,
- release readiness.

### Taranay — Backend Lead

Primary responsibility:

- core API,
- background worker,
- database design,
- shared API/event contracts.

### Vivek — Frontend Lead

Primary responsibility:

- Developer Cockpit,
- `apps/web`,
- incident viewing,
- AI-suggested-fix review/approval workflow.

## Boundary

Each component must use the shared contracts rather than creating independent versions of the project's domain model.

## Status

**NOT STARTED**

---

# 8. P4 — Event & Incident Pipeline

## Goal

Move from foundational skeletons to the real incident-processing pipeline.

## Primary outcomes

Implement:

- real webhook ingestion,
- event processing,
- incident lifecycle.

## Intended direction

Conceptually:

```text
Pipeline / Deployment Event
        ↓
Webhook Ingestion
        ↓
Normalized Event
        ↓
Incident
        ↓
Incident Lifecycle
```

Provider-specific event formats should be converted into the platform's shared event representation.

## Status

**NOT STARTED**

---

# 9. P5 — AI Diagnosis & RAG

## Goal

Implement the real RAG pipeline and use it to analyze real incidents.

## Primary outcome

The AI subsystem should move from skeleton/foundation code to an actual diagnosis workflow.

The project direction is to ground diagnosis in the system's relevant:

- logs,
- documentation,
- code,
- configuration,
- runbooks,
- historical information.

## Intended conceptual flow

```text
Incident
   ↓
Relevant Knowledge Retrieval
   ↓
Evidence
   ↓
RAG / LLM Analysis
   ↓
Probable Diagnosis
```

The RAG system grounds diagnosis; it does not make the diagnosis automatically infallible.

## Status

**NOT STARTED**

---

# 10. P6 — Remediation & GitHub Automation

## Goal

Turn AI-suggested fixes into real remediation actions through a human-approved GitHub workflow.

## Primary outcome

The project should demonstrate:

```text
AI-suggested fix
       ↓
Human review
       ↓
Human approval
       ↓
GitHub remediation
       ↓
Pull Request
```

The human approval step is required before consequential remediation is applied in the MVP.

## MVP integration

Git/GitHub is the concrete remediation integration.

The reusable platform should not treat GitHub-specific objects as universal domain concepts.

## Status

**NOT STARTED**

---

# 11. P7 — Developer Cockpit

## Goal

Implement the full dashboard UI for the incident and approval workflow.

## Primary user

The Developer Cockpit is the engineer-facing interface.

## Intended workflow visibility

The dashboard should allow engineers to inspect the progression from:

```text
Incident
   ↓
Evidence
   ↓
Diagnosis
   ↓
Remediation Proposal
   ↓
Approval
   ↓
Execution
   ↓
Verification
```

The UI should allow engineers to review and approve AI-suggested fixes as part of the governed remediation flow.

## Status

**NOT STARTED**

---

# 12. P8 — End-to-End Integration

## Goal

Connect all major components and test the complete golden path.

## Golden-path concept

The intended end-to-end path is:

```text
Event
  ↓
Incident
  ↓
Evidence
  ↓
AI Diagnosis
  ↓
Remediation Proposal
  ↓
Human Approval
  ↓
GitHub Remediation
  ↓
Verification
  ↓
Final Incident Outcome
```

## Purpose

P8 validates that:

- the components work together,
- the shared contracts are compatible,
- the complete operational workflow is executable,
- the Developer Cockpit reflects the underlying lifecycle.

## Status

**NOT STARTED**

---

# 13. P9 — Hardening

## Goal

Perform the security, performance, and reliability pass.

## Focus areas

### Security

Review:

- application boundaries,
- external integrations,
- credentials/secrets,
- AI-generated remediation controls.

### Performance

Evaluate the system's processing behavior against the project's operational goals.

### Reliability

Verify that failures in processing, remediation, and verification do not produce false claims of successful resolution.

## Status

**NOT STARTED**

---

# 14. P10 — Staging

## Goal

Move the system from development/integration validation toward a staging environment.

## Primary outcomes

Implement:

- staging environment,
- deployment pipeline,
- rollback demonstration.

## DevOps ownership

The DevOps Lead has explicit staging and release-readiness responsibility from this phase onward.

## Status

**NOT STARTED**

---

# 15. P11 — Release

## Goal

Prepare and perform the production release.

## Primary outcome

A production release of the platform/reference implementation.

## Status

**NOT STARTED**

---

# 16. P12 — Post-MVP

## Goal

Continue the platform's evolution and scaling after the MVP.

This phase provides the project with a path beyond the first implementation.

The domain-agnostic architecture allows future evolution toward additional supported domains/integrations through the adapter boundary.

## Status

**NOT STARTED**

---

# 17. Cross-Phase Architectural Boundary

Across all phases, maintain:

```text
              DOMAIN-AGNOSTIC CORE

Event
  ↓
Incident
  ↓
Evidence
  ↓
Diagnosis
  ↓
Remediation
  ↓
Approval
  ↓
Execution
  ↓
Verification

              ADAPTER BOUNDARY
                     ↓
        E-Commerce Reference Adapter
```

The e-commerce implementation is the first concrete reference environment.

It should not force the reusable platform core to depend on:

- orders,
- payments,
- inventory,
- other e-commerce-only concepts.

---

# 18. Cross-Phase AI Boundary

The AI subsystem should remain within its intended role:

```text
Retrieve
   ↓
Reason
   ↓
Diagnose
   ↓
Propose
```

It should not bypass the product's governed remediation path.

The MVP governance model remains:

```text
AI proposes
   ↓
Human approves
   ↓
System executes
   ↓
System verifies
```

---

# 19. Cross-Phase Verification Boundary

The project must preserve the distinction:

```text
Proposed
   ≠
Approved
   ≠
Executed
   ≠
Verified
   ≠
Resolved
```

This distinction becomes particularly important from P6 onward and is validated during P8.

---

# 20. Cross-Phase Success Metrics

The project's stated success targets are:

| Metric | Target |
|---|---|
| Mean Time to Detect (MTTD) | Reduce by 50% versus manual baseline |
| Mean Time to Resolve (MTTR) | Reduce by 30–50% versus manual baseline |
| Automated resolution rate | 70% or more of incidents resolved through AI-suggested, human-approved fixes |
| Service availability | 99.9% uptime or better |

These values are **targets**, not current results.

They must not be reported as achieved until measured.

---

# 21. Phase Completion Discipline

Before moving to a later phase, the team should confirm that the current phase's stated outcome has actually been achieved.

In particular:

```text
P0 complete
   ↓
P1 foundation complete
   ↓
P2 contracts/domain foundation
   ↓
P3 component construction
   ↓
...
```

The project should not use the existence of documentation or skeleton code as evidence that a later capability is complete.

For example:

```text
AI worker skeleton
        !=
AI diagnosis implemented
```

and:

```text
GitHub integration planned
        !=
Remediation automation implemented
```

---

# 22. Current Position

The project is currently positioned at:

```text
P0 — COMPLETE
        ↓
P1 — COMPLETE / INITIAL FOUNDATION
        ↓
P2 — NEXT
```

The current foundation includes the four application skeletons and their PostgreSQL/Redis connectivity.

The next substantive work is therefore the shared **Contract & Domain Foundation**, not independent implementation of the later AI/remediation workflow.

---

# 23. Final Phase Model

The complete development roadmap is:

```text
P0  Governance & Repository Bootstrap
 ↓
P1  Technical Foundation
 ↓
P2  Contract & Domain Foundation
 ↓
P3  Parallel Component Construction
 ↓
P4  Event & Incident Pipeline
 ↓
P5  AI Diagnosis & RAG
 ↓
P6  Remediation & GitHub Automation
 ↓
P7  Developer Cockpit
 ↓
P8  End-to-End Integration
 ↓
P9  Hardening
 ↓
P10 Staging
 ↓
P11 Release
 ↓
P12 Post-MVP Evolution & Scaling
```

The phase sequence is deliberately conservative: establish governance and technical foundations first, freeze shared contracts before parallel construction, implement the operational and AI workflow incrementally, integrate and validate it end-to-end, then harden, stage, release, and evolve the platform.
