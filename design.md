# Design.md
# AIOps Self-Healing Platform — System Design

> **Design baseline:** This document is derived from the current Project Review Report and is intended to replace the earlier e-commerce-specific design direction. The platform core is domain-agnostic; e-commerce is the first reference implementation/adapter and evaluation environment.

---

## 1. Purpose

The system is designed as a modular AIOps self-healing platform that can:

1. receive operational and CI/CD events,
2. normalize those events into a common model,
3. detect and correlate incidents,
4. collect incident evidence,
5. use Retrieval-Augmented Generation (RAG) to diagnose probable root causes,
6. produce an evidence-backed remediation plan,
7. require human approval before consequential remediation,
8. execute the approved remediation through a domain/integration adapter,
9. verify the resulting state,
10. record the incident, diagnosis, approval, execution, and verification outcome.

The first concrete implementation is an **e-commerce reference implementation**. E-commerce-specific concepts must remain behind the adapter boundary rather than becoming assumptions inside the reusable platform core.

---

# 2. Design Goals

## 2.1 Primary goals

The design must support:

- domain-agnostic incident handling,
- pluggable domain/integration adapters,
- shared contracts between API, worker, AI worker, frontend, and adapters,
- evidence-grounded AI diagnosis,
- human-governed remediation,
- traceability from incident → evidence → diagnosis → remediation → verification,
- GitHub-based remediation for the MVP,
- a clear Developer Cockpit for engineers,
- incremental development through phases P0–P12.

## 2.2 Quality goals

The design should remain:

- modular,
- maintainable,
- understandable,
- testable,
- observable,
- secure,
- suitable for parallel development by four team members and their AI coding assistants.

These qualities support the project's stated objective of reducing incident detection and recovery effort without allowing the AI subsystem to become an uncontrolled execution path.

---

# 3. Design Scope

The design covers:

- API-facing application design,
- background processing,
- AI/RAG diagnosis,
- incident and evidence lifecycle,
- remediation proposal and approval,
- adapter integration,
- verification,
- Developer Cockpit,
- persistence,
- CI/CD integration,
- e-commerce reference implementation.

The design does **not** turn e-commerce concepts such as orders, payments, or inventory into universal platform entities.

---

# 4. Design Mental Model

The platform should be understood as:

```text
Operational Event
      |
      v
Event Normalization
      |
      v
Detection / Correlation
      |
      v
Incident
      |
      v
Evidence Collection
      |
      v
RAG Diagnosis
      |
      v
Remediation Plan
      |
      v
Human Approval
      |
      v
Adapter / Executor
      |
      v
Actual Change
      |
      v
Verification
      |
      v
Recorded Result
```

The key design boundary is:

```text
                 DOMAIN-AGNOSTIC CORE
 ----------------------------------------------------------------
 Event -> Incident -> Evidence -> Diagnosis -> Remediation
                    -> Approval -> Verification
 ----------------------------------------------------------------
                         ADAPTER
          Domain knowledge + telemetry mapping +
          remediation execution + verification
```

---

# 5. Core Design Entities

The report identifies the following generic domain model.

## 5.1 Pipeline

Represents a CI/CD or operational pipeline known to the platform.

Example attributes:

- identifier,
- name,
- associated environment,
- adapter/domain reference,
- status metadata.

The exact implementation schema is frozen during the contract/domain phase.

## 5.2 PipelineRun

Represents one execution of a pipeline.

It provides the execution context in which an event or failure occurred.

## 5.3 Service

Represents an operational service or component.

The core must not assume that a service has any particular business meaning.

## 5.4 Deployment

Represents a deployment of a service or component into an environment.

## 5.5 Environment

Represents an operational execution environment.

Examples may include development, staging, or production, but the core model should treat environment as generic metadata.

## 5.6 Event

Represents an incoming operational or CI/CD occurrence.

Examples for the reference implementation include:

- pipeline events,
- deployment events,
- service failure events.

Incoming provider-specific events should be normalized before they enter the generic incident-processing flow.

## 5.7 Incident

Represents a correlated operational problem requiring investigation.

An incident should retain enough context to connect:

```text
Event(s)
  |
  +-- Evidence
  |
  +-- Diagnosis
  |
  +-- Remediation
  |
  +-- Verification
```

## 5.8 Evidence

Represents information used to understand an incident.

Evidence may include relevant:

- logs,
- code,
- documentation,
- configuration,
- runbooks,
- historical information,
- incident/event context.

The RAG system uses this information to ground diagnosis.

## 5.9 Diagnosis / RootCause

Represents the AI-generated explanation of the probable cause of an incident.

A diagnosis should be tied to the evidence used to produce it rather than being treated as an unsupported free-form AI answer.

## 5.10 RemediationPlan

Represents the proposed response to a diagnosis.

It contains one or more proposed remediation actions.

## 5.11 RemediationAction

Represents an individual proposed change or corrective action.

Actions must remain within the capabilities exposed by the applicable adapter/executor.

## 5.12 Approval

Represents the human governance decision required before consequential remediation.

For the MVP, an AI-suggested fix must not become an actual consequential change without human approval.

## 5.13 Change / ExecutionResult

Represents what actually happened after an approved remediation action was sent to the applicable executor.

The system should distinguish:

```text
Suggested action
       !=
Approved action
       !=
Executed change
```

## 5.14 Verification

Represents the evidence that the attempted remediation produced the expected operational result.

A remediation is not considered successfully completed merely because an execution request was accepted.

---

# 6. Event Design

## 6.1 Event ingestion

The first implementation uses webhook-driven ingestion for pipeline/deployment events.

The design flow is:

```text
External Provider
      |
      v
Webhook / Ingestion Endpoint
      |
      v
Provider Event Parsing
      |
      v
Normalized Event
      |
      v
Incident Processing
```

Provider-specific payload structure should remain outside the generic incident model.

## 6.2 Normalized event

The normalized event should contain only information required by the generic platform workflow.

Conceptually:

```text
Event
├── event identity
├── event type
├── occurrence time
├── source
├── environment/context
├── related pipeline/service/deployment
└── opaque domain/integration metadata
```

The exact schema belongs to the shared contract/domain phase.

## 6.3 Domain metadata

Domain-specific information should not be interpreted by the generic core as if it were a universal field.

For example, an e-commerce adapter may provide information related to:

- orders,
- payments,
- inventory,

but these remain adapter/domain knowledge.

---

# 7. Incident Design

## 7.1 Incident creation

The platform creates an incident from one or more normalized operational events.

The design should support:

```text
single event -> incident
multiple correlated events -> incident
```

The incident becomes the central object through which evidence, diagnosis, remediation, approval, and verification are connected.

## 7.2 Incident lifecycle

Conceptually:

```text
Detected
   |
   v
Investigating
   |
   v
Diagnosed
   |
   v
Remediation Proposed
   |
   v
Awaiting Approval
   |
   +------> Rejected / Cancelled
   |
   v
Approved
   |
   v
Executing
   |
   v
Verifying
   |
   +------> Failed
   |
   v
Resolved
```

The exact persisted status values must be finalized as part of the shared domain contract rather than independently invented by different team members.

---

# 8. Evidence Design

## 8.1 Evidence-first diagnosis

The AI diagnosis flow should be designed around evidence retrieval rather than unrestricted generation.

```text
Incident
   |
   v
Evidence Retrieval
   |
   +-- Logs
   +-- Code
   +-- Documentation
   +-- Configuration
   +-- Runbooks
   +-- Historical information
   |
   v
Retrieved Context
   |
   v
LLM Diagnosis
```

## 8.2 Evidence traceability

The diagnosis should retain references to the evidence used to support it.

Conceptually:

```text
Diagnosis
├── probable root cause
├── supporting evidence references
└── remediation rationale
```

This allows an engineer to inspect why a remediation was proposed.

## 8.3 RAG boundary

RAG is responsible for grounding the diagnosis in project/domain knowledge.

It does not become the owner of:

- incident persistence,
- approval decisions,
- direct consequential execution,
- final verification.

The AI worker proposes; the surrounding platform governs.

---

# 9. AI Diagnosis Design

## 9.1 AI worker responsibility

The AI worker is responsible for:

- retrieving relevant knowledge,
- assembling incident context,
- invoking the LLM/RAG pipeline,
- producing a probable diagnosis,
- producing remediation suggestions,
- associating the output with supporting evidence.

The current report maps this responsibility to the AI diagnosis engine using Python, FastAPI, and LangChain.

## 9.2 Diagnosis output

The conceptual output is:

```text
Diagnosis
├── incident reference
├── probable root cause
├── evidence references
├── explanation
└── remediation proposal
```

The diagnosis is a proposed explanation, not an automatic declaration of absolute causal truth.

## 9.3 Separation from execution

The AI worker should not directly bypass the approval and remediation-control flow to perform a consequential change.

The intended sequence is:

```text
AI diagnosis
    |
    v
Remediation plan
    |
    v
Human approval
    |
    v
Executor / adapter
```

---

# 10. Remediation Design

## 10.1 Remediation planning

The AI diagnosis produces a remediation plan rather than directly modifying the target system.

```text
Diagnosis
   |
   v
RemediationPlan
   |
   +-- Action 1
   +-- Action 2
   +-- ...
```

## 10.2 MVP execution path

The report explicitly identifies GitHub-integrated remediation as a project requirement.

Therefore the reference implementation may use a flow such as:

```text
Approved Remediation
        |
        v
Git / GitHub Adapter
        |
        v
Repository Change
        |
        v
Pull Request
        |
        v
CI/CD Validation
        |
        v
Verification
```

GitHub is the concrete MVP integration; the reusable core should not make GitHub's API model the universal domain model.

## 10.3 Human approval

The Developer Cockpit provides the interface through which engineers review and approve AI-suggested fixes.

The design principle is:

```text
AI proposes
   ↓
Human reviews
   ↓
Human approves
   ↓
System executes
```

This is a core governance requirement of the project.

---

# 11. Adapter Design

## 11.1 Purpose

Adapters isolate domain-specific and integration-specific behavior from the reusable platform core.

The adapter boundary should cover the areas that differ between implementations:

```text
Adapter
├── domain configuration
├── knowledge-base configuration
├── telemetry/event normalization
├── remediation execution
└── verification
```

## 11.2 E-commerce reference adapter

The first adapter provides the e-commerce-specific behavior required for the MVP.

It may understand the e-commerce system's:

- architecture,
- domain model,
- operational conventions,
- codebase,
- logs,
- documentation,
- configuration,
- runbooks.

These details should not leak into generic incident contracts.

## 11.3 Future adapters

A future adapter should be able to provide another supported operational/domain environment without requiring the generic incident, evidence, diagnosis, remediation, approval, and verification concepts to be redesigned.

The adapter may support only the remediation actions that are meaningful and implementable for that environment.

---

# 12. Developer Cockpit Design

The frontend is the engineer-facing Developer Cockpit.

Its primary purpose is to expose the incident and remediation workflow clearly.

## 12.1 Main views

The design should support the following conceptual views:

### Incident view

Displays:

- incident identity,
- incident status,
- affected pipeline/service/deployment/environment context,
- relevant event information,
- collected evidence,
- diagnosis.

### Diagnosis view

Displays:

- probable root cause,
- supporting evidence,
- explanation,
- proposed remediation.

### Approval view

Displays:

- proposed remediation actions,
- relevant evidence/rationale,
- approval state,
- engineer action required.

### Remediation view

Displays:

- approved action,
- execution state,
- resulting change,
- relevant GitHub/CI information for the MVP.

### Verification view

Displays:

- verification state,
- observed result,
- final incident state.

The frontend should make the complete chain visible rather than presenting the AI recommendation as an isolated answer.

---

# 13. API Design

The API is the main synchronous application boundary.

Its design responsibilities include:

- receiving events,
- exposing incidents,
- exposing evidence and diagnosis information,
- exposing remediation proposals,
- receiving approval decisions,
- exposing execution and verification state.

The API should coordinate with the background worker and AI worker rather than placing long-running diagnosis/remediation work directly inside request handlers.

The exact endpoint names and request/response schemas belong to the shared contract phase.

---

# 14. Background Worker Design

The background worker uses Python 3.12 and RQ.

Its role is to handle asynchronous processing so that the API remains focused on request/response operations.

Conceptually:

```text
API
 |
 +---- enqueue event processing ----> Worker
 |
 +---- enqueue diagnosis -----------> AI Worker
 |
 +---- enqueue remediation ---------> Worker / Adapter
 |
 +---- request verification ---------> Worker / Adapter
```

The precise job contracts must be shared across the relevant components.

---

# 15. Persistence Design

PostgreSQL is the project's database.

The persistence design should represent the generic workflow entities rather than embedding the e-commerce business model into the platform database.

At minimum, the domain design must account for the report's generic concepts:

```text
Pipeline
PipelineRun
Service
Deployment
Environment
Event
Incident
Evidence
Diagnosis
RemediationPlan
RemediationAction
Approval
Change / ExecutionResult
Verification
```

The exact relational schema is a P2 responsibility.

---

# 16. Redis Design

Redis is part of the project technology stack and supports asynchronous/background processing through RQ.

The design should keep Redis-related processing concerns separate from the PostgreSQL system of record.

Redis should not become the authoritative source for the persistent incident lifecycle.

---

# 17. CI/CD Design

GitHub Actions is the concrete CI/CD technology in the MVP.

The current project uses automated checks on pull requests, including:

- build checks,
- type checks,
- import checks.

The remediation workflow may create a GitHub pull request containing an AI-suggested and human-approved change.

The design therefore connects:

```text
Incident
   ↓
Diagnosis
   ↓
Remediation Proposal
   ↓
Human Approval
   ↓
Git/GitHub Change
   ↓
Pull Request / CI
   ↓
Verification
```

---

# 18. Technology Mapping

The design maps to the project's current technology stack as follows:

| Concern | Technology |
|---|---|
| Backend API | Python 3.12 + FastAPI |
| Background worker | Python 3.12 + RQ |
| AI diagnosis engine | Python 3.12 + FastAPI + LangChain |
| Frontend | TypeScript + Next.js / React |
| Database | PostgreSQL |
| Cache / queue | Redis |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Version control | Git / GitHub |

These are the technologies identified in the current Project Review Report.

---

# 19. Design Ownership

The four application areas map to the project team as follows:

| Member | Design responsibility |
|---|---|
| Rudra — AI/RAG Lead | AI diagnosis engine, RAG pipeline, LLM integration, remediation suggestion generation |
| Saurav — DevOps Lead | Infrastructure, containerization, CI/CD, deployment, later staging/release readiness |
| Taranay — Backend Lead | Core API, background worker, database, shared API/event contracts |
| Vivek — Frontend Lead | Developer Cockpit dashboard and incident/approval workflow |

Shared contracts are not owned independently by each component. They must be agreed at the project level during the contract/domain phase.

---

# 20. Phase-Aligned Design

The design must follow the project's sequential development plan.

## P0 — Governance & Repository Bootstrap

Design outcome:

- ownership,
- repository structure,
- team conventions,
- collaboration rules.

**Status:** Complete.

## P1 — Technical Foundation

Design outcome:

- application skeletons,
- local development environment,
- API,
- worker,
- AI worker,
- web application,
- PostgreSQL,
- Redis.

**Status:** Initial foundation complete.

## P2 — Contract & Domain Foundation

This is the critical design-freeze phase.

Finalize:

- shared API contracts,
- event schemas,
- generic domain model,
- database schema.

The domain-neutral design must be frozen here before parallel component construction.

**Status:** Not started.

## P3 — Parallel Component Construction

Each member builds the assigned component against the shared contracts.

**Status:** Not started.

## P4 — Event & Incident Pipeline

Implement:

- real webhook ingestion,
- normalized event processing,
- incident lifecycle.

**Status:** Not started.

## P5 — AI Diagnosis & RAG

Implement:

- real RAG pipeline,
- incident analysis,
- evidence-grounded diagnosis.

**Status:** Not started.

## P6 — Remediation & GitHub Automation

Implement:

- remediation actions,
- human approval,
- GitHub-integrated changes,
- pull-request workflow.

**Status:** Not started.

## P7 — Developer Cockpit

Implement the complete frontend workflow.

**Status:** Not started.

## P8 — End-to-End Integration

Connect the complete golden path and test it across all components.

**Status:** Not started.

## P9 — Hardening

Address:

- security,
- performance,
- reliability.

**Status:** Not started.

## P10 — Staging

Implement staging environment, deployment pipeline, and rollback demonstration.

**Status:** Not started.

## P11 — Release

Prepare production release.

**Status:** Not started.

## P12 — Post-MVP

Continue evolution and scaling of the platform.

This is the phase in which the broader adapter/domain expansion can be evaluated.

**Status:** Not started.

---

# 21. Golden-Path Design

The primary end-to-end design path is:

```text
1. Pipeline / deployment event occurs
                 |
                 v
2. Webhook ingestion
                 |
                 v
3. Event normalization
                 |
                 v
4. Incident created / correlated
                 |
                 v
5. Evidence collected
                 |
                 v
6. RAG retrieves relevant project/domain knowledge
                 |
                 v
7. AI generates probable diagnosis
                 |
                 v
8. AI generates remediation proposal
                 |
                 v
9. Engineer reviews proposal
                 |
                 v
10. Engineer approves
                 |
                 v
11. Adapter executes approved change
                 |
                 v
12. GitHub/CI workflow processes change
                 |
                 v
13. Platform verifies result
                 |
                 v
14. Incident is recorded as resolved or failed
```

This is the primary design path for the e-commerce reference implementation.

---

# 22. Failure-Oriented Design

The system must also represent the possibility that a step fails.

Examples:

```text
Event ingestion fails
        -> event is not treated as successfully processed

Diagnosis fails
        -> incident remains unresolved / requires further handling

Human rejects remediation
        -> no consequential remediation is executed

Execution fails
        -> execution result records failure

Verification fails
        -> remediation is not considered successfully resolved
```

The platform should not equate "AI generated a response" or "executor accepted a request" with successful incident resolution.

---

# 23. Design Separation Rules

The following separation is fundamental.

## 23.1 Domain vs platform

```text
Generic:
Incident
Evidence
Diagnosis
Remediation
Approval
Verification

Domain-specific:
Orders
Payments
Inventory
E-commerce-specific conventions
```

Domain-specific concepts belong behind the adapter.

## 23.2 Diagnosis vs execution

```text
Diagnosis != Execution
```

The AI subsystem proposes; the controlled remediation path executes.

## 23.3 Proposal vs approved action

```text
AI proposal != approved remediation
```

Human approval is an explicit state transition.

## 23.4 Execution vs verification

```text
Execution != successful resolution
```

The resulting state must be verified.

---

# 24. Design for the Current Project State

At the time of the current review:

- P0 is complete.
- P1 foundation is complete.
- all four application skeletons boot successfully,
- PostgreSQL and Redis connectivity is working,
- automated CI checks and manual end-to-end foundation checks have been performed,
- business logic has not yet been implemented.

Therefore this design must **not** describe incident detection, RAG diagnosis, or automated remediation as already implemented.

Those capabilities belong to P2 onward.

---

# 25. Design Constraints

The following constraints are derived from the current project direction:

1. The reusable core must remain domain-agnostic.
2. E-commerce is the first reference implementation, not the universal core model.
3. Shared contracts must be established before parallel component implementation.
4. RAG must be grounded in project/domain evidence.
5. AI diagnosis must remain separated from consequential execution.
6. Human approval is required before consequential remediation in the MVP.
7. GitHub is the concrete remediation integration for the MVP.
8. The architecture must leave room for future adapters.
9. Current technology choices remain those specified in the Project Review Report.
10. Current implementation status must not be confused with planned functionality.

---

# 26. Design Acceptance Criteria

The design is aligned with the current project direction when:

- a generic incident can be represented without requiring an e-commerce business concept;
- evidence can be attached to an incident and used by diagnosis;
- diagnosis can produce a remediation proposal without directly executing it;
- human approval is represented explicitly;
- approved remediation can be handed to an appropriate adapter/executor;
- execution and verification are separately represented;
- the e-commerce implementation can provide domain-specific behavior through an adapter;
- the shared contracts can be frozen before P3;
- the Developer Cockpit can expose the incident → diagnosis → approval → remediation → verification workflow;
- the current technology stack remains consistent with the report.

---

# 27. Final Design Principle

The platform should be designed around one central separation:

```text
              REUSABLE PLATFORM CORE
   Incident / Evidence / Diagnosis / Remediation
          Approval / Execution / Verification
                         |
                         v
                DOMAIN / INTEGRATION
                     ADAPTER
                         |
                         v
             E-Commerce Reference MVP
```

The e-commerce system demonstrates the platform. It should not define the platform's generic concepts.

The intended result is a system in which operational incidents can move through a controlled, evidence-grounded lifecycle from detection to diagnosis to human-approved remediation and verification, while domain-specific knowledge and execution remain isolated behind an adapter boundary.
