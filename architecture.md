# Architecture.md

## AIOps Self-Healing Platform

**Document:** `docs/Architecture.md`  
**Status:** Authoritative architecture baseline for implementation  
**Architecture direction:** Domain-agnostic AIOps core with pluggable domain/pipeline adapters  
**Reference implementation:** E-commerce CI/CD and operational pipeline

---

## 1. Purpose

This document defines the structural architecture and boundaries of the AIOps Self-Healing Platform.

The platform is **not architecturally an e-commerce application**.

The reusable platform core is designed around generic operational concepts:

- pipelines and pipeline runs;
- services, deployments, and environments;
- events;
- incidents;
- evidence;
- diagnosis/root cause;
- remediation plans and actions;
- approvals;
- changes/execution results;
- verification.

E-commerce is the **first reference implementation and evaluation environment**. Its domain-specific behavior, knowledge, telemetry normalization, and execution mechanisms belong behind an adapter boundary rather than inside the reusable core.

The architecture therefore follows:

```text
                 Developer Cockpit
                        |
                        v
              Domain-Agnostic API
                        |
                        v
             Incident / Evidence Core
                        |
          +-------------+-------------+
          |             |             |
          v             v             v
      Detection        RAG        Remediation
          |             |             |
          +-------------+-------------+
                        |
                        v
                Adapter Interface
                        |
             +----------+----------+
             |                     |
             v                     v
      E-Commerce Adapter     Future Adapters
        (MVP/reference)       (future domains)
```

The central architectural requirement is that **core incident, evidence, diagnosis, remediation, approval, and verification concepts must remain independent of the e-commerce domain**.

---

# 2. Architectural Objectives

The architecture must support the following properties:

### 2.1 Domain independence

The core must not require e-commerce concepts such as:

- orders;
- payments;
- inventory;
- carts;
- customers;
- product catalog.

Such concepts may exist inside the e-commerce adapter or its domain-specific knowledge sources.

### 2.2 Pipeline independence

The core should operate on generic pipeline and operational events rather than assuming one particular CI/CD provider or pipeline implementation.

The MVP uses a concrete e-commerce pipeline as the reference environment.

### 2.3 Evidence-grounded diagnosis

AI diagnosis must be grounded in available evidence and relevant project/domain knowledge.

The architecture must preserve the distinction:

```text
Observed Evidence
       !=
AI Diagnosis
```

The AI may produce a probable root cause, supporting evidence references, confidence/uncertainty, and recommended remediation. It is not the authoritative source of operational truth.

### 2.4 Bounded remediation

The system must not treat AI-generated remediation as automatically authorized.

The intended control flow is:

```text
Detect
  |
  v
Diagnose
  |
  v
Evidence-backed Remediation Proposal
  |
  v
Policy / Risk Validation
  |
  v
Human Approval
  |
  v
Execution
  |
  v
Verification
  |
  v
Incident Resolution
```

### 2.5 Extensibility

A future domain/pipeline adapter should be able to reuse the core incident and remediation workflow without requiring a rewrite of the core domain model.

The architecture is therefore intentionally organized around explicit contracts and adapters.

---

# 3. High-Level System Architecture

## 3.1 Logical architecture

```text
+-------------------------------------------------------------------+
|                        Developer Cockpit                          |
|                     Web / Operational UI                          |
+-------------------------------+-----------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
|                    Domain-Agnostic API Layer                      |
|  Incident APIs | Pipeline APIs | Evidence | Diagnosis | Actions  |
+-------------------------------+-----------------------------------+
                                |
                                v
+-------------------------------------------------------------------+
|                    Core Incident / Domain Layer                   |
|                                                                   |
| Pipeline / PipelineRun                                           |
| Service / Deployment / Environment                               |
| Event                                                             |
| Incident                                                          |
| Evidence                                                          |
| Diagnosis / RootCause                                             |
| RemediationPlan / RemediationAction                              |
| Approval                                                          |
| Change / ExecutionResult                                         |
| Verification                                                     |
+-------------------------------+-----------------------------------+
                                |
              +-----------------+-----------------+
              |                 |                 |
              v                 v                 v
+-------------------+ +-------------------+ +----------------------+
| Detection &       | | RAG / Diagnosis   | | Remediation &        |
| Correlation       | | Engine            | | Verification         |
|                   | |                   | |                      |
| event processing  | | retrieval         | | planning             |
| incident creation | | context building  | | policy/risk checks   |
| correlation       | | AI analysis       | | approval             |
|                   | | evidence linkage  | | execution            |
+---------+---------+ +---------+---------+ | verification         |
          |                     |           +----------+-----------+
          +---------------------+----------------------+
                                |
                                v
+-------------------------------------------------------------------+
|                     Adapter Boundary                              |
|                                                                   |
| Domain configuration                                              |
| Event / telemetry normalization                                   |
| Domain knowledge sources                                          |
| Remediation execution                                             |
| Verification                                                     |
| Provider integrations                                             |
+-------------------------------+-----------------------------------+
                                |
              +-----------------+-----------------+
              |                                   |
              v                                   v
+---------------------------+       +-------------------------------+
| E-Commerce Adapter        |       | Future Adapter(s)             |
| MVP/reference             |       | Other pipeline/domain        |
| implementation            |       | implementations              |
+---------------------------+       +-------------------------------+
```

The adapter boundary is the key mechanism preventing the reusable core from becoming coupled to one domain.

---

# 4. Core vs Adapter Responsibility

## 4.1 Core responsibilities

The reusable core owns generic operational behavior:

- event ingestion and processing;
- incident lifecycle;
- evidence representation;
- event/incident correlation;
- diagnosis workflow;
- RAG orchestration;
- remediation planning;
- policy/risk validation;
- human approval workflow;
- remediation workflow orchestration;
- execution-result recording;
- verification workflow;
- auditability;
- generic API contracts;
- generic persistence and state management.

The core must not inspect or interpret domain-specific metadata merely because it exists.

---

## 4.2 Adapter responsibilities

An adapter provides the domain/pipeline-specific implementation required to operate the generic workflow.

The report identifies these responsibilities:

1. domain configuration;
2. knowledge-base configuration;
3. telemetry/event normalization;
4. remediation executor;
5. verification.

An adapter may additionally encapsulate concrete external providers required by that domain/pipeline.

For the MVP:

```text
Core Platform
      |
      v
E-Commerce Adapter
      |
      +--> e-commerce/domain configuration
      +--> e-commerce knowledge base
      +--> pipeline/telemetry normalization
      +--> concrete remediation execution
      +--> verification
```

A future adapter should implement the same architectural boundary without changing the meaning of the core incident/evidence/diagnosis/remediation contracts.

---

# 5. Domain Model

The core domain model is intentionally generic.

## 5.1 Pipeline

Represents a logical software delivery or operational pipeline.

A pipeline may contain multiple runs and may be associated with services, deployments, environments, and external execution systems.

The core must not assume that every pipeline is an e-commerce pipeline.

---

## 5.2 PipelineRun

Represents one execution of a pipeline.

A run may produce events and evidence that contribute to incident detection and diagnosis.

---

## 5.3 Service

Represents a deployable or operational service associated with a pipeline or environment.

The core treats service identity generically.

Domain-specific service meaning belongs to an adapter.

---

## 5.4 Deployment

Represents a deployment-related operational object or execution.

Deployment semantics must remain generic.

Concrete deployment systems belong behind provider/adapter boundaries.

---

## 5.5 Environment

Represents an execution environment such as development, staging, or production-like environments.

Environment identity and policy are part of the core workflow, while concrete environment integration is adapter/infrastructure responsibility.

---

## 5.6 Event

An Event is an incoming operational occurrence.

Examples may include:

- pipeline execution results;
- deployment events;
- telemetry events;
- external operational events.

The exact source and provider-specific payload belong to the adapter/integration boundary.

The core consumes a normalized representation.

---

## 5.7 Incident

An Incident represents an operational failure requiring investigation.

It is the primary correlation object connecting:

```text
Event
  |
  v
Incident
  |
  +--> Evidence
  |
  +--> Diagnosis
  |
  +--> RemediationPlan
  |
  +--> Approval
  |
  +--> Change / ExecutionResult
  |
  +--> Verification
```

An Incident must not be modeled as an e-commerce-specific object.

---

## 5.8 Evidence

Evidence represents an observation or external source relevant to an incident.

Potential evidence includes:

- logs;
- stack traces;
- commits;
- pipeline information;
- configuration;
- metrics;
- documentation;
- knowledge-base material.

Evidence must remain separate from AI conclusions.

The system must preserve traceability between a diagnosis and the evidence supporting it.

---

## 5.9 Diagnosis / RootCause

Diagnosis is an inference produced from incident context and available evidence.

A diagnosis may contain:

- probable root cause;
- supporting evidence references;
- confidence;
- uncertainty;
- contradictory evidence where applicable;
- recommended remediation.

The architecture must not treat AI confidence as proof of correctness.

---

## 5.10 RemediationPlan

A RemediationPlan describes the proposed response to an incident.

It should answer, where applicable:

- what changes;
- why it changes;
- which resources/files are affected;
- what risk exists;
- what validation/tests are required;
- which evidence supports the proposal.

A remediation plan is a proposal until the required policy and human-approval controls are satisfied.

---

## 5.11 RemediationAction

A RemediationAction represents a concrete operation that may be proposed or executed.

Generic categories may include:

- configuration/dependency changes;
- source-code changes;
- rollback;
- restart/redeploy;
- infrastructure configuration changes;
- branch/commit/PR operations;
- verification actions.

Not every adapter supports every action.

The architecture must therefore allow adapter capability/policy checks before execution.

---

## 5.12 Approval

Approval is a governance object representing explicit human authorization for a consequential remediation workflow.

Approval does not imply that the remediation will succeed.

The executor must never interpret an AI recommendation as equivalent to approval.

---

## 5.13 Change / ExecutionResult

These represent the actual consequence of a remediation action.

They must be distinct from the proposed action.

Examples include:

- branch created;
- commit created;
- pull request created;
- CI result;
- deployment result;
- rollback result;
- execution failure.

A proposal is not an execution result.

---

## 5.14 Verification

Verification determines whether the intended operational state was actually achieved.

The architecture must distinguish:

```text
Proposed
    !=
Approved
    !=
Executed
    !=
Verified
    !=
Resolved
```

A merged change is not automatically a verified deployment, and a successful execution call is not automatically proof that the incident is resolved.

---

# 6. Incident-to-Resolution Workflow

The canonical workflow is:

```text
External Event
      |
      v
Normalize Event
      |
      v
Persist Event
      |
      v
Detect / Correlate
      |
      v
Create or Update Incident
      |
      v
Collect / Associate Evidence
      |
      v
Build Diagnostic Context
      |
      v
RAG Retrieval + AI Diagnosis
      |
      v
Evidence-backed Diagnosis
      |
      v
Remediation Plan
      |
      v
Policy / Risk Validation
      |
      v
Human Approval
      |
      v
Adapter Execution
      |
      v
Actual Change / Execution Result
      |
      v
Verification
      |
      +------ failure ------> Investigation / Retry / Escalation
      |
      v
Incident Resolution
```

The architecture must preserve each stage as a distinct responsibility.

---

# 7. Event and Ingestion Architecture

External systems may produce provider-specific events.

The architecture therefore separates:

```text
External Event
     |
     v
Provider / Domain Adapter
     |
     v
Normalized Event
     |
     v
Core Event Processing
```

The core should not be responsible for understanding arbitrary provider-specific payload formats.

The adapter normalizes them into the generic event representation.

The normalized event is then processed by the core incident pipeline.

---

# 8. Detection and Incident Correlation

The detection layer is responsible for:

- processing normalized events;
- identifying failure conditions;
- correlating related operational events;
- creating or updating incidents;
- associating relevant evidence;
- initiating asynchronous diagnosis where appropriate.

The detection layer must not embed e-commerce-specific assumptions.

For example, the core must not contain logic such as:

```text
if payment_service_failed:
    create_payment_incident()
```

Instead, the adapter and normalized event representation provide the necessary domain context.

---

# 9. RAG and Diagnosis Architecture

The RAG subsystem has two conceptually separate responsibilities:

### Runtime incident evidence

Information observed for the current incident:

- logs;
- stack traces;
- pipeline data;
- commits;
- configuration;
- metrics;
- execution results.

### Knowledge sources

Information used to ground diagnosis:

- documentation;
- runbooks;
- historical incidents;
- known failure patterns;
- engineering knowledge;
- domain-specific knowledge.

These must not be treated as the same category.

The conceptual flow is:

```text
Incident
   |
   +--------------------+
   |                    |
   v                    v
Runtime Evidence    Knowledge Sources
   |                    |
   +---------+----------+
             |
             v
      Context Builder
             |
             v
          Retriever
             |
             v
       AI Diagnosis
             |
             v
 Structured Diagnosis
             |
             +--> supporting evidence
             +--> probable root cause
             +--> confidence
             +--> uncertainty
             +--> recommended remediation
```

RAG grounds diagnosis; it does not guarantee a correct root cause.

The system must retain uncertainty where evidence is insufficient or contradictory.

---

# 10. Knowledge Adapter Boundary

Domain-specific knowledge must not be hard-coded into the generic diagnosis engine.

For the MVP:

```text
Generic Diagnosis Engine
          |
          v
E-Commerce Knowledge Configuration
          |
          +--> project documentation
          +--> runbooks
          +--> historical incidents
          +--> relevant code/configuration context
```

Future domains should be able to provide their own knowledge configuration without changing the core diagnosis semantics.

The exact implementation of knowledge ingestion, indexing, retrieval, and storage belongs to the implementation phases and must follow the contracts established during P2.

---

# 11. Remediation Architecture

Remediation is intentionally split into planning and execution.

```text
Diagnosis
    |
    v
RemediationPlan
    |
    v
RemediationAction(s)
    |
    v
Policy / Risk Validation
    |
    v
Human Approval
    |
    v
Adapter / Executor
    |
    v
ExecutionResult
    |
    v
Verification
```

The core orchestrates this workflow.

The adapter provides concrete execution behavior.

---

## 11.1 Git and CI/CD

GitHub is the concrete MVP integration, not the definition of the core architecture.

The architecture should therefore conceptually depend on generic source-control / CI-CD capabilities.

For the MVP, the concrete implementation may use:

```text
Generic Remediation / Source Control Boundary
                  |
                  v
             GitHub Adapter
                  |
                  +--> branch
                  +--> commit
                  +--> pull request
                  +--> CI status
                  +--> merge status
```

The core must not make GitHub-specific concepts part of the generic domain model merely because GitHub is the first implementation.

---

# 12. Adapter Capability Model

Adapters may support different subsets of remediation operations.

For example, one adapter may support:

```text
source change
pull request
CI verification
deployment verification
```

while another may support only:

```text
configuration change
restart
health verification
```

Therefore the architecture must not assume that every `RemediationAction` is executable by every adapter.

Before execution, the system should establish:

```text
Requested Action
      |
      v
Adapter Capability Check
      |
      v
Policy / Risk Check
      |
      v
Approval Requirement
      |
      v
Execution
```

The exact machine-readable capability contract is part of the P2 contract/domain foundation.

---

# 13. Policy, Risk and Human Governance

Policy and risk are first-class architectural concerns because remediation can cause consequential changes.

The minimum governed path is:

```text
AI Proposal
     |
     v
Action Validation
     |
     v
Policy / Capability Check
     |
     v
Risk Evaluation
     |
     v
Human Approval
     |
     v
Execution
```

The system must not permit the AI worker to bypass these boundaries.

Particularly sensitive or high-risk actions may require additional controls.

The MVP requires explicit human approval before consequential remediation execution.

---

# 14. Verification Architecture

Verification is an independent stage after execution.

Examples:

```text
PR created
     !=
deployment verified
```

and:

```text
deployment completed
     !=
incident resolved
```

Verification may use adapter-provided mechanisms appropriate to the pipeline/domain.

The result must be recorded and associated with the incident and remediation execution.

---

# 15. Frontend Architecture

The Developer Cockpit is a consumer of the domain/API contracts.

Its purpose is to allow engineers to understand and control the workflow.

The UI should make the following distinctions visible:

```text
OBSERVED
AI GENERATED
HUMAN APPROVED
SYSTEM VERIFIED
```

The frontend must not independently determine:

- root cause;
- authorization;
- remediation policy;
- deployment truth;
- incident resolution.

The backend/domain layer remains authoritative.

The cockpit should expose, as applicable:

- pipeline and incident status;
- incident timeline;
- evidence;
- diagnosis;
- uncertainty/confidence;
- proposed remediation;
- approval state;
- execution/change status;
- verification state;
- audit history.

---

# 16. API Layer

The API layer exposes domain-neutral operations to the Developer Cockpit and other clients.

The API should be organized around generic concepts rather than e-commerce-specific endpoints.

Conceptually:

```text
/incidents
/pipelines
/pipeline-runs
/events
/evidence
/diagnoses
/remediation-plans
/remediation-actions
/approvals
/verifications
```

Exact paths, schemas, versions, and error envelopes are to be defined and frozen during P2.

The API must not expose an implementation-specific adapter representation as the canonical domain contract.

---

# 17. Asynchronous Processing

Long-running operations should not require indefinitely open HTTP requests.

The architecture supports asynchronous processing for operations such as:

- event processing;
- incident correlation;
- AI/RAG analysis;
- remediation preparation;
- external provider operations;
- verification.

Conceptually:

```text
API Request
    |
    v
Accepted
    |
    v
Job / Event
    |
    v
Worker Processing
    |
    v
Terminal Result
```

The current technology stack uses Redis/RQ for background processing.

---

# 18. Technology Architecture

The current report defines the following implementation stack:

| Layer | Technology |
|---|---|
| Backend API | Python 3.12 + FastAPI |
| Background worker | Python 3.12 + RQ |
| AI diagnosis engine | Python 3.12 + FastAPI + LangChain |
| Frontend | TypeScript + Next.js / React |
| Database | PostgreSQL |
| Queue / cache | Redis |
| Containerization | Docker |
| Local orchestration | Docker Compose |
| CI/CD | GitHub Actions |
| Version control | Git / GitHub |

These technologies implement the architecture; they do not define the architecture.

The system must avoid coupling domain semantics to a particular framework, LLM provider, or external vendor.

---

# 19. Persistence Architecture

PostgreSQL is the current persistent storage technology.

The database must represent the generic core domain and its relationships.

The core schema should not require e-commerce-specific entities simply to function.

Domain-specific metadata may be associated through an explicitly bounded mechanism such as domain metadata/configuration, provided that the core does not interpret domain-specific fields.

Important distinction:

```text
Core-owned data
    +
opaque domain-specific metadata
```

is acceptable.

Embedding e-commerce business logic into core tables or core services is not.

---

# 20. Domain Metadata Rule

Domain-specific metadata must remain opaque to the reusable core unless the metadata is explicitly promoted into a generic contract.

For example, the core must not contain logic equivalent to:

```text
incident.domain_metadata["payment_service"]
```

as a required architectural dependency.

If a concept is required by multiple adapters and is genuinely generic, it may become part of the shared domain contract through an explicit architecture/contract decision.

Otherwise it remains adapter-owned.

This rule is essential for preserving domain independence.

---

# 21. External Provider Boundaries

External providers should be isolated behind adapters/interfaces where practical.

Concrete examples in the MVP include:

- GitHub;
- GitHub Actions;
- LLM provider;
- vector/retrieval infrastructure.

The core should depend on stable abstractions rather than provider-specific SDK behavior.

Conceptually:

```text
Core
 |
 +--> AI Provider Interface
 |        |
 |        +--> Concrete AI Provider
 |
 +--> Source Control / CI Interface
 |        |
 |        +--> GitHub
 |
 +--> Domain Adapter
          |
          +--> E-Commerce Adapter
          +--> Future Adapter
```

Provider replacement must not require redesigning the incident domain.

---

# 22. Observability Architecture

The AIOps platform itself must be observable.

The system should maintain correlation across:

```text
request
  |
  v
event
  |
  v
incident
  |
  v
job
  |
  v
AI analysis
  |
  v
remediation
  |
  v
execution
  |
  v
verification
```

Operational telemetry should include structured logs, metrics, traces, and correlation identifiers where applicable.

AI execution should expose operational metadata such as:

- analysis ID;
- model/provider;
- latency;
- retrieval status;
- validation status;
- result status.

Sensitive prompts, credentials, and secrets must not be exposed through telemetry.

---

# 23. Audit Architecture

Consequential actions require traceable audit records.

Examples include:

- analysis generated;
- remediation proposed;
- remediation approved;
- remediation rejected;
- change created;
- pull request created;
- CI result received;
- deployment started;
- deployment completed;
- verification completed;
- incident resolved.

Audit history should preserve what happened rather than silently overwriting historical actions.

---

# 24. Security Architecture

Security is cross-cutting.

The architecture must enforce:

- server-side authorization;
- secure external webhook handling;
- secret isolation;
- least privilege;
- input validation;
- safe handling of AI-generated output;
- restricted remediation execution;
- environment separation;
- auditable consequential actions.

AI-generated output is untrusted input.

The AI worker must not become an authorization boundary.

---

# 25. AI Security Boundary

Retrieved logs, documentation, tickets, source files, and other external content are data.

They must not gain authority over:

- system policy;
- security rules;
- authorization;
- developer instructions.

For example, a malicious log message containing an instruction to execute a dangerous command remains evidence/data, not an instruction to the system.

AI output must pass through normal validation and governance controls.

---

# 26. Failure and Recovery Architecture

External dependencies are assumed to fail.

The system must account for:

- provider timeout;
- authentication failure;
- rate limits;
- queue failure;
- database failure;
- AI failure;
- invalid AI output;
- remediation execution failure;
- CI failure;
- deployment failure;
- verification failure.

Long-running or consequential operations must consider:

- retries;
- idempotency;
- timeouts;
- terminal states;
- partial completion;
- manual recovery;
- audit records.

A retry must not blindly repeat a dangerous side effect.

---

# 27. Idempotency

Consequential operations should have backend-level protection against duplicate execution where applicable.

Examples:

- remediation approval;
- PR creation;
- deployment;
- rollback.

Frontend button disabling is not sufficient protection.

The exact idempotency contract belongs to the domain/API implementation.

---

# 28. Architecture Dependency Direction

The intended dependency direction is:

```text
Developer Cockpit
       |
       v
API / Application Layer
       |
       v
Core Domain
       |
       v
Adapters / Infrastructure
```

The core domain must not depend directly on:

- React/browser APIs;
- GitHub SDKs;
- LLM SDKs;
- concrete database implementation.

Infrastructure and provider implementations depend inward on stable contracts.

---

# 29. Repository-Level Architectural Boundaries

The current project structure contains four primary application areas:

```text
apps/
├── api/
├── worker/
├── ai-worker/
└── web/
```

Shared architectural concerns should be kept in dedicated packages/directories as established by the repository.

The current project also uses:

```text
PostgreSQL
Redis
Docker
GitHub Actions
Git/GitHub
```

The exact repository structure remains subject to the frozen P2 contracts and existing implementation.

---

# 30. Four-Team Ownership Boundaries

The current project team is organized as:

| Member | Role | Primary architectural ownership |
|---|---|---|
| Rudra | AI / RAG Lead | AI diagnosis, RAG, remediation intelligence |
| Saurav | DevOps Lead | Infrastructure, CI/CD, deployment, release readiness |
| Taranay | Backend Lead | Core API, background worker, database, shared contracts |
| Vivek | Frontend Lead | Developer Cockpit / operational UI |

Ownership is a collaboration boundary, not permission to redesign another domain.

Shared contracts require coordinated review.

---

# 31. AI IDE Architectural Rule

AI IDEs are implementation assistants, not autonomous architects.

An AI agent must not:

- silently change the domain model;
- silently change shared contracts;
- introduce e-commerce assumptions into the generic core;
- bypass adapter boundaries;
- bypass approval/policy controls;
- modify another owner's area without explicit scope;
- replace an accepted architecture merely because an alternative appears simpler.

If a required change crosses an architectural boundary:

```text
STOP
  |
  v
Identify dependency
  |
  v
Request scope / architecture review
  |
  v
Update authoritative contract/document if approved
  |
  v
Implement
```

---

# 32. P2 as the Architectural Freeze Point

The project is currently at the transition into P2.

P0 governance and the initial P1 technical foundation are complete.

The reviewed project state reports that the API, worker, AI-worker, and web application skeletons boot successfully and connect to PostgreSQL and Redis, while business logic has not yet been implemented.

P2 is therefore the critical point at which the domain-neutral architecture becomes machine-enforceable.

P2 must freeze, at minimum:

- core domain model;
- event representation;
- incident representation;
- evidence representation;
- diagnosis representation;
- remediation plan/action representation;
- approval representation;
- execution/change result representation;
- verification representation;
- adapter boundary;
- relevant API/event contracts;
- state semantics;
- capability/policy boundaries.

The exact machine-readable contracts should be established during P2 rather than being invented independently by different components.

---

# 33. E-Commerce Reference Adapter

The MVP uses an e-commerce pipeline as the first concrete implementation.

This adapter is responsible for translating the generic platform into the reference environment.

Conceptually:

```text
                GENERIC CORE
                     |
                     v
             Adapter Interface
                     |
                     v
          +----------------------+
          | E-Commerce Adapter   |
          +----------------------+
             |       |       |
             v       v       v
          Events    RAG    Execution
             |       |       |
             v       v       v
          E-commerce pipeline/environment
```

The e-commerce adapter may contain domain-specific knowledge such as the relationships and operational context relevant to the reference system.

That knowledge must not leak into generic core semantics.

---

# 34. Future Adapter Architecture

The intended extensibility test is:

```text
Existing Core
     |
     +--> E-Commerce Adapter
     |
     +--> Future Adapter
```

The future adapter should be able to reuse:

- Incident;
- Evidence;
- Diagnosis;
- RemediationPlan;
- Approval;
- Verification;
- generic API/application orchestration.

Adding a future adapter should primarily involve implementing/configuring adapter-specific behavior.

A future adapter may still require genuine engineering work and may support only a subset of actions.

The architecture does **not** claim that arbitrary domains can be connected with zero implementation effort.

---

# 35. Domain-Agnosticism Acceptance Test

A key architectural test is:

### Test A — Remove the reference adapter

The generic core should remain structurally valid without e-commerce-specific logic.

### Test B — Add another adapter

A second adapter should be able to integrate without changing the meaning of:

- Incident;
- Evidence;
- Diagnosis;
- RemediationPlan;
- Approval;
- Verification.

### Test C — Inspect core for domain leakage

The core must not require:

- e-commerce entities;
- e-commerce terminology;
- e-commerce-specific branching;
- adapter-specific metadata interpretation.

### Test D — Provider substitution

Concrete integrations such as GitHub must remain replaceable through provider/adapter boundaries where practical.

These tests provide evidence for the domain-agnostic architecture rather than relying only on documentation claims.

---

# 36. Golden Path

The principal end-to-end workflow is:

```text
Controlled Failure
       |
       v
Event Ingestion
       |
       v
Incident Creation
       |
       v
Evidence Collection
       |
       v
RAG Diagnosis
       |
       v
Probable Root Cause
       |
       v
Remediation Proposal
       |
       v
Policy / Risk Validation
       |
       v
Human Approval
       |
       v
Remediation Execution
       |
       v
CI / Deployment
       |
       v
Verification
       |
       v
Incident Resolution
```

For the MVP, the reference implementation uses the e-commerce environment and GitHub-based remediation workflow.

---

# 37. Failure Paths

The architecture must safely handle:

```text
AI unavailable
      |
      v
Incident remains recoverable / escalated

Invalid AI output
      |
      v
Validation rejects output

Human rejects remediation
      |
      v
No consequential execution

CI fails
      |
      v
Incident remains unresolved / recovery path

Deployment fails
      |
      v
Verification fails / recovery path

Evidence insufficient
      |
      v
Uncertainty / further investigation / escalation

External provider unavailable
      |
      v
Retry / failure state / manual recovery
```

The system must not manufacture success merely because a preceding stage completed.

---

# 38. What Is Explicitly Not Core Architecture

The following are **not** allowed to become core domain assumptions merely because they are used in the MVP:

- e-commerce order processing;
- payment processing;
- inventory management;
- shopping cart logic;
- customer management;
- GitHub-specific domain semantics;
- one specific LLM provider;
- one specific retrieval provider;
- one specific deployment provider.

These belong to reference adapters, integrations, or infrastructure.

---

# 39. Architecture Evolution Rules

Architecture changes must be deliberate.

If an implementation appears to require a new cross-cutting abstraction:

```text
Problem identified
      |
      v
Check existing contract
      |
      v
Determine whether the concept is genuinely generic
      |
      v
Architecture / ADR review
      |
      v
Update authoritative documentation
      |
      v
Update contracts
      |
      v
Implement
      |
      v
Test
```

Do not solve architectural uncertainty by adding hidden coupling.

---

# 40. Current Architectural Invariants

The following invariants are foundational:

**ARCH-001**  
The reusable core is domain-agnostic.

**ARCH-002**  
E-commerce is the MVP reference adapter, not the definition of the core domain.

**ARCH-003**  
Incident, Evidence, Diagnosis, Remediation, Approval, Execution, and Verification remain distinct concepts.

**ARCH-004**  
Evidence is not equivalent to AI diagnosis.

**ARCH-005**  
AI output is untrusted and does not authorize consequential action.

**ARCH-006**  
Human approval is required before consequential remediation execution in the MVP.

**ARCH-007**  
Adapter-specific behavior remains behind the adapter boundary.

**ARCH-008**  
GitHub is a concrete MVP integration, not a generic core-domain concept.

**ARCH-009**  
Verification is separate from execution and resolution.

**ARCH-010**  
The backend/domain layer is authoritative over frontend assumptions.

**ARCH-011**  
Shared contracts are the integration boundary between team-owned components.

**ARCH-012**  
Architecture changes require explicit human review.

---

# 41. Architecture and Phase Alignment

The architecture maps to the implementation phases as follows:

| Phase | Architectural purpose |
|---|---|
| P0 | Governance and repository boundaries |
| P1 | Executable technical foundation |
| P2 | Domain-neutral contracts and architecture freeze |
| P3 | Parallel construction against frozen boundaries |
| P4 | Event and incident processing |
| P5 | Generic diagnosis + reference knowledge adapter |
| P6 | Generic remediation + reference execution adapter |
| P7 | Domain-neutral Developer Cockpit |
| P8 | Full end-to-end integration |
| P9 | Reliability, security and performance hardening |
| P10 | Staging and deployment readiness |
| P11 | Final release |
| P12 | Controlled future adapter/evolution evaluation |

The architecture must not be reinterpreted as an instruction to implement every future capability during MVP.

---

# 42. Architectural Success Criteria

The architecture is considered successfully implemented when:

- the core can process generic operational incidents;
- domain-specific behavior is isolated behind an adapter boundary;
- the e-commerce environment works as the reference implementation;
- evidence and AI diagnosis remain distinguishable;
- RAG grounds diagnosis in relevant evidence/knowledge;
- remediation is policy/risk constrained;
- human approval is enforced before consequential MVP remediation;
- execution results and verification are recorded separately;
- GitHub integration is isolated from generic domain semantics;
- the Developer Cockpit consumes backend/domain truth;
- the golden path is observable and auditable;
- a second adapter can be evaluated without redesigning the core domain model.

---

# 43. Final Architectural Mental Model

The project should be understood as:

```text
                    USER / ENGINEER
                           |
                           v
                 +-------------------+
                 | Developer Cockpit |
                 +---------+---------+
                           |
                           v
                 +-------------------+
                 | Domain-Agnostic   |
                 | API / Application  |
                 +---------+---------+
                           |
                           v
        +---------------------------------------------+
        |              REUSABLE CORE                  |
        |                                             |
        | Event → Incident → Evidence → Diagnosis    |
        |                         ↓                   |
        |                Remediation Plan             |
        |                         ↓                   |
        |                 Policy / Risk               |
        |                         ↓                   |
        |                    Approval                  |
        |                         ↓                   |
        |                Execution / Change            |
        |                         ↓                   |
        |                   Verification               |
        +-------------------------+-------------------+
                                  |
                                  v
                       +---------------------+
                       | Adapter Boundary    |
                       +----------+----------+
                                  |
                 +----------------+----------------+
                 |                                 |
                 v                                 v
        E-Commerce Adapter                  Future Adapter(s)
           MVP/reference
                 |
       +---------+----------+
       |                    |
       v                    v
 Domain Knowledge     Concrete Execution /
 Telemetry            Provider Integrations
```

The core architectural idea is therefore:

> **A reusable, evidence-grounded AIOps incident-to-remediation core, with domain-specific knowledge, telemetry normalization, execution, and verification supplied through adapters; e-commerce is the first reference implementation rather than the architectural boundary.**

This is the architectural baseline that subsequent contracts, implementation phases, AI IDE instructions, and collaboration rules must follow.
