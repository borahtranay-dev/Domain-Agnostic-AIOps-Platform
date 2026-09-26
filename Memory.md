# Memory.md
# AIOps Self-Healing Platform — Project Memory

> **Source of truth:** Current Project Review Report (2026).  
> This file records stable project facts, decisions, boundaries, and current state for use by the development team and AI coding assistants. It must not reintroduce assumptions from the earlier e-commerce-only version.

---

## 1. Project Identity

### Current project direction

The project is an **AIOps self-healing platform** whose first concrete implementation/evaluation environment is an **e-commerce operational pipeline**.

The platform is intended to:

- detect operational/CI-CD failures,
- diagnose probable root causes using AI and RAG,
- propose remediation,
- require human approval before consequential remediation,
- apply approved remediation through the project's GitHub workflow,
- verify the result.

### Critical architectural interpretation

**E-commerce is the first reference implementation, not the definition of the reusable platform core.**

The reusable platform concepts must remain generic enough to support future domain/integration adapters.

---

# 2. Core Problem

The project addresses two primary operational problems:

1. **Detection lag** — incidents such as build failures or service errors may be discovered late.
2. **Slow recovery** — manual diagnosis and fixing require engineering time and manually applied fixes can introduce additional problems.

The project therefore focuses on reducing:

- Mean Time to Detect (MTTD)
- Mean Time to Resolve (MTTR)
- manual engineering toil during incident response

The current requirements specify target improvements of:

- MTTD: 50% reduction versus a manual baseline
- MTTR: 30–50% reduction versus a manual baseline
- automated resolution: 70% or more of eligible incidents via AI-suggested, human-approved fixes
- service availability: 99.9% uptime or better

These are **targets**, not measurements already achieved.

---

# 3. Domain Context

The project sits at the intersection of:

- DevOps / Site Reliability Engineering
- AIOps
- e-commerce systems engineering

The e-commerce reference environment is characterized by:

- distributed services,
- CI/CD pipelines,
- frequent deployments,
- high availability requirements,
- operational consequences of downtime.

The platform architecture, however, should not make e-commerce concepts universal.

---

# 4. Generic Core Concepts

The report establishes a generic domain model containing:

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

These concepts form the conceptual basis of the reusable platform.

---

# 5. Domain-Specific Concepts

The e-commerce reference implementation may contain concepts such as:

```text
Orders
Payments
Inventory
E-commerce-specific architecture
E-commerce-specific operational conventions
```

These are **reference-domain concepts**.

They must not be silently promoted into universal platform entities.

Domain-specific behavior belongs behind the adapter/interface boundary.

---

# 6. Adapter Principle

The platform uses an adapter-oriented design.

The adapter is responsible for project/domain-specific behavior including:

- domain configuration,
- knowledge-base configuration,
- telemetry/event normalization,
- remediation execution,
- verification.

Conceptually:

```text
                 REUSABLE CORE
    Event → Incident → Evidence → Diagnosis
              → Remediation → Approval
              → Execution → Verification
                         |
                         v
                      Adapter
                         |
                         v
             E-Commerce Reference MVP
```

Future adapters may provide equivalent domain/integration-specific behavior for other environments.

---

# 7. Event and Incident Flow

The intended lifecycle is:

```text
Pipeline / Deployment Event
          ↓
Event Ingestion
          ↓
Event Normalization
          ↓
Incident Detection / Correlation
          ↓
Evidence Collection
          ↓
RAG-Based Diagnosis
          ↓
Remediation Proposal
          ↓
Human Approval
          ↓
Approved Execution
          ↓
Verification
          ↓
Recorded Result
```

This is the project's central operational flow.

---

# 8. RAG / AI Boundary

RAG is used to ground diagnosis in project/domain information.

Relevant knowledge may include:

- logs,
- code,
- documentation,
- configuration,
- runbooks,
- historical information,
- incident/event context.

The AI diagnosis engine should:

1. receive incident context,
2. retrieve relevant project/domain knowledge,
3. reason over the retrieved evidence,
4. produce a probable root-cause diagnosis,
5. propose remediation.

RAG **grounds** the diagnosis; it does not guarantee that the diagnosis is correct.

---

# 9. Evidence Requirement

AI output should be associated with the evidence used to support it.

The intended relationship is:

```text
Incident
   ↓
Evidence
   ↓
Diagnosis
   ↓
Remediation Proposal
```

The system should preserve enough traceability for an engineer to understand the basis of a proposed diagnosis/remediation.

---

# 10. Governance Principle

The project explicitly adopts a bounded, human-governed remediation model.

The intended sequence is:

```text
AI proposes
     ↓
Human reviews
     ↓
Human approves
     ↓
System executes
     ↓
System verifies
```

For the MVP:

**An AI-suggested consequential fix must not be applied without human approval.**

This requirement is directly motivated by the project's literature review and its emphasis on evidence-grounded, bounded autonomy.

---

# 11. Remediation Principle

The following distinctions must remain explicit:

```text
AI diagnosis        != actual change
AI proposal         != approved action
Approved action     != successful execution
Successful execution != verified resolution
```

A remediation is not considered successful merely because an execution request was accepted.

Verification is a separate part of the workflow.

---

# 12. GitHub in the MVP

GitHub is the concrete remediation integration for the MVP.

The intended remediation path includes:

```text
Diagnosis
   ↓
Remediation Proposal
   ↓
Human Approval
   ↓
Git / GitHub Change
   ↓
Pull Request
   ↓
CI/CD Validation
   ↓
Verification
```

GitHub is an MVP implementation choice and must not become the universal conceptual model of the platform.

---

# 13. Developer Cockpit

The frontend is the **Developer Cockpit**.

Its purpose is to allow engineers to:

- view incidents,
- inspect evidence,
- inspect AI diagnosis,
- review remediation proposals,
- approve/reject proposed fixes,
- inspect remediation execution,
- inspect verification/results.

The cockpit is therefore part of the human-governed remediation loop.

---

# 14. Technology Stack

The current report specifies:

| Area | Technology |
|---|---|
| Backend API | Python 3.12 + FastAPI |
| Background worker | Python 3.12 + RQ |
| AI diagnosis engine | Python 3.12 + FastAPI + LangChain |
| Frontend | TypeScript + Next.js / React |
| Database | PostgreSQL |
| Cache / message queue | Redis |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Version control | Git / GitHub |

Do not replace these technologies in project documentation without an explicit project decision.

---

# 15. Application Responsibilities

The current four-member structure is:

### Rudra — AI / RAG Lead

Primary responsibility:

- `apps/ai-worker`
- RAG pipeline
- LLM integration
- remediation-suggestion generation

### Saurav — DevOps Lead

Primary responsibility:

- infrastructure,
- containerization,
- CI/CD,
- deployment,
- staging and release readiness from P10 onward.

### Taranay — Backend Lead

Primary responsibility:

- `apps/api`
- `apps/worker`
- database design,
- shared API/event contracts.

### Vivek — Frontend Lead

Primary responsibility:

- `apps/web`
- Developer Cockpit
- incident workflow
- remediation approval UI.

Shared contracts remain a project-wide concern.

---

# 16. Phase Memory

The project follows sequential phases P0–P12.

## P0 — Governance & Repository Bootstrap

Purpose:

- rules,
- ownership,
- repository structure,
- team conventions.

**Status: COMPLETE**

## P1 — Technical Foundation

Purpose:

- working local environment,
- application skeletons,
- API,
- worker,
- AI worker,
- web,
- PostgreSQL,
- Redis.

**Status: COMPLETE / INITIAL FOUNDATION**

## P2 — Contract & Domain Foundation

Purpose:

- shared API schemas,
- shared event schemas,
- generic domain model,
- database schema.

**Status: NOT STARTED**

P2 is the critical contract/domain foundation phase.

## P3 — Parallel Component Construction

Each member implements their component against the shared contracts.

**Status: NOT STARTED**

## P4 — Event & Incident Pipeline

Implement:

- real webhook ingestion,
- incident lifecycle.

**Status: NOT STARTED**

## P5 — AI Diagnosis & RAG

Implement:

- real RAG,
- diagnosis against real incidents.

**Status: NOT STARTED**

## P6 — Remediation & GitHub Automation

Implement:

- remediation,
- human approval,
- GitHub pull-request workflow.

**Status: NOT STARTED**

## P7 — Developer Cockpit

Implement the full dashboard and incident/approval workflow.

**Status: NOT STARTED**

## P8 — End-to-End Integration

Connect and test the complete system.

**Status: NOT STARTED**

## P9 — Hardening

Address:

- security,
- performance,
- reliability.

**Status: NOT STARTED**

## P10 — Staging

Implement:

- staging environment,
- deployment pipeline,
- rollback demonstration.

**Status: NOT STARTED**

## P11 — Release

Prepare production release.

**Status: NOT STARTED**

## P12 — Post-MVP

Continue evolution and scaling.

**Status: NOT STARTED**

---

# 17. Current Implementation State

At the time represented by the current Project Review Report:

- P0 is complete.
- The initial P1 technical foundation is complete.
- The repository has defined ownership and contribution rules.
- The technology stack is finalized.
- All four application skeletons boot successfully.
- The applications connect to PostgreSQL and Redis.
- Application communication has been verified through automated CI checks and manual end-to-end foundation testing.

Importantly:

**No business logic has yet been implemented.**

Specifically, the report states that the following are not yet implemented:

- order handling,
- real incident detection,
- AI diagnosis.

Those capabilities begin in P2 onward.

---

# 18. What Must Not Be Assumed as Already Implemented

AI coding assistants and team members must not describe the following as complete merely because the architecture or design documents describe them:

- real incident detection,
- production webhook processing,
- production-quality RAG,
- root-cause diagnosis,
- automated remediation,
- GitHub remediation,
- full Developer Cockpit,
- end-to-end self-healing,
- staging,
- release,
- measured MTTD improvement,
- measured MTTR improvement,
- 70% automated resolution,
- 99.9% availability.

They are planned capabilities, targets, or later phases unless implementation evidence says otherwise.

---

# 19. Project Differentiation

The report positions the project around:

- a lightweight, purpose-built implementation,
- deep integration with its own codebase and CI/CD,
- RAG grounded in actual logs and documentation,
- GitHub-integrated remediation,
- human approval before consequential automated fixes.

The broader architectural direction additionally requires that the reusable core remain separate from the e-commerce reference adapter.

Do not describe the project as automatically novel or industry-first. Its distinctiveness must be demonstrated through the implemented architecture and evaluation.

---

# 20. Literature-Informed Governance

The project review identifies research themes including:

- end-to-end evaluation,
- cross-environment generalization,
- explainability,
- governance of autonomous interventions.

The report states that these considerations informed the project's decision to use:

**evidence-grounded, bounded autonomy with human approval before AI-suggested fixes are applied.**

This is a project design decision, not a claim that the platform has already solved these research problems.

---

# 21. Existing-System Context

The project review discusses existing systems including:

- Datadog Watchdog,
- Dynatrace Davis AI,
- PagerDuty,
- BigPanda,
- Moogsoft,
- emerging AI incident/SRE tools.

The project should therefore not claim that AIOps detection, AI diagnosis, RAG, incident management, or remediation are individually new ideas.

The intended contribution is the particular combination and implementation of the project's architecture and workflow.

---

# 22. Success Metrics

The current requirements specify:

```text
MTTD reduction          → 50% target
MTTR reduction          → 30–50% target
Automated resolution    → ≥70% target
Availability             → ≥99.9% target
```

These require proper baselines and measurement during evaluation.

Until measured, they are **requirements/targets only**.

---

# 23. Documentation Consistency Rules

All project documentation should preserve these facts:

1. The platform core is domain-agnostic.
2. E-commerce is the first reference implementation.
3. Domain-specific behavior belongs behind adapters.
4. Incident/evidence/diagnosis/remediation/approval/verification are generic platform concepts.
5. RAG grounds diagnosis in project/domain knowledge.
6. AI proposes; human approval controls consequential remediation.
7. GitHub is the concrete MVP remediation integration.
8. Verification follows execution.
9. P2 establishes the shared contracts and domain foundation.
10. P0 and the initial P1 foundation are complete; later phases are not yet complete.
11. Targets must not be presented as measured results.
12. Planned architecture must not be presented as implemented functionality.

---

# 24. AI Coding Assistant Memory

Every AI coding assistant working on this project should treat the following as persistent context:

```text
CURRENT DIRECTION
-----------------
AIOps self-healing platform
        +
E-commerce reference implementation


CORE
----
Generic incident/evidence/diagnosis/remediation workflow


ADAPTER
-------
Domain/integration-specific knowledge and execution


AI
--
Evidence-grounded diagnosis and remediation proposal


GOVERNANCE
----------
Human approval before consequential remediation


MVP EXECUTION
-------------
GitHub-integrated remediation


VERIFICATION
------------
Execution is not resolution; verify the result


CURRENT STATE
-------------
P0 complete
P1 foundation complete
P2 next
Business logic not yet implemented
```

---

# 25. Final Memory Rule

When any future project document, implementation plan, code-generation instruction, or AI coding prompt conflicts with this memory, the current **Project Review Report** is the authoritative project-level source.

In particular, never revert the project to an architecture where:

```text
E-commerce business concepts
        ↓
define the entire platform
```

The intended direction is:

```text
Reusable AIOps Core
        ↓
Adapter Boundary
        ↓
E-Commerce Reference Implementation
        ↓
Future Domain/Integration Adapters
```
