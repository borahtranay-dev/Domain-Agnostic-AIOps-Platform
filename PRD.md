# PRD.md
# AIOps Self-Healing Platform — Product Requirements Document

> **Product baseline:** This PRD is aligned with the current Project Review Report.  
> The product is a **domain-agnostic AIOps self-healing platform**, with an **e-commerce system as the first reference implementation and evaluation environment**.
>
> This document defines what the product is intended to do, who it serves, its scope, requirements, workflow, success measures, and phased delivery. It does not treat planned capabilities as already implemented.

---

# 1. Product Overview

## 1.1 Product name

**A Domain-Agnostic AIOps Self-Healing Platform: E-Commerce Reference Implementation**

## 1.2 Product purpose

The platform is intended to reduce the time and manual effort required to detect, diagnose, and recover from operational/CI-CD incidents.

The core product workflow is:

```text
Detect
  ↓
Collect Evidence
  ↓
Diagnose
  ↓
Propose Remediation
  ↓
Human Approval
  ↓
Execute
  ↓
Verify
```

The first implementation demonstrates this workflow against an e-commerce operational environment.

---

# 2. Problem Statement

Modern software systems can experience operational failures such as:

- pipeline failures,
- deployment failures,
- service errors,
- configuration-related failures,
- other operational incidents represented by the platform's event model.

Two problems are central to the project:

### 2.1 Detection lag

Operational incidents may not be identified immediately.

### 2.2 Slow recovery

Engineers may need to manually:

- inspect logs,
- inspect code,
- search documentation,
- investigate configuration,
- identify probable root causes,
- determine a suitable fix,
- apply the fix,
- verify the result.

This consumes engineering time and can introduce additional manual error.

The platform is intended to reduce this operational burden through automated detection/analysis and controlled remediation.

---

# 3. Product Vision

The intended product vision is:

> A reusable AIOps platform that turns operational signals into evidence-grounded diagnoses and controlled remediation, while keeping domain-specific knowledge and execution behind adapters.

The e-commerce implementation demonstrates the platform's capabilities without defining the generic platform model.

---

# 4. Product Goals

## 4.1 Primary goals

The product should:

1. ingest operational/CI-CD events,
2. normalize incoming events into a generic representation,
3. detect and correlate incidents,
4. collect relevant evidence,
5. retrieve project/domain knowledge using RAG,
6. produce a probable root-cause diagnosis,
7. propose remediation actions,
8. present the proposal for human review and approval,
9. execute approved remediation through the appropriate adapter,
10. verify whether the remediation achieved the expected result,
11. preserve the incident lifecycle and supporting evidence.

## 4.2 Architectural goal

The product must separate:

```text
Reusable AIOps Core
        ↓
Adapter Boundary
        ↓
Domain / Integration-Specific Behavior
```

The first domain-specific implementation is e-commerce.

---

# 5. Target Users

## 5.1 Primary user — Software/DevOps Engineer

The engineer uses the Developer Cockpit to:

- inspect incidents,
- understand the evidence,
- review AI diagnosis,
- review remediation proposals,
- approve or reject proposed fixes,
- inspect execution,
- inspect verification results.

## 5.2 Project development team

The four-member development team is also a product stakeholder because the platform is being built as a collaborative engineering system.

The product must therefore support clear contracts between:

- backend,
- worker,
- AI/RAG subsystem,
- frontend,
- infrastructure.

---

# 6. Product Scope

## 6.1 In scope

The MVP scope includes:

- event ingestion,
- generic event normalization,
- incident representation,
- incident/evidence lifecycle,
- RAG-based diagnosis,
- remediation proposal generation,
- human approval,
- GitHub-integrated remediation,
- verification,
- Developer Cockpit,
- e-commerce reference adapter,
- Docker-based local environment,
- PostgreSQL persistence,
- Redis-backed asynchronous processing,
- GitHub Actions CI/CD.

## 6.2 Out of scope for the generic core

The generic platform core must not depend on:

- orders,
- payments,
- inventory,
- other e-commerce-only business concepts.

These belong to the e-commerce reference implementation/adapter.

## 6.3 Later-stage scope

The broader project roadmap includes:

- hardening,
- staging,
- release,
- post-MVP evolution and scaling,
- future adapter/domain expansion.

---

# 7. Core Product Concepts

The product's generic conceptual model includes:

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

These concepts are intended to remain reusable across supported implementations.

---

# 8. Product Workflow

## 8.1 Event ingestion

The system receives an operational or CI/CD event.

For the reference implementation, this includes webhook-driven events.

```text
External Event
      ↓
Webhook / Ingestion
      ↓
Normalization
```

Provider-specific payload structures must be normalized before entering the generic incident workflow.

---

## 8.2 Incident detection and correlation

Normalized events are evaluated to identify or update an incident.

The incident becomes the central product object connecting:

```text
Events
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
```

---

## 8.3 Evidence collection

The system collects information relevant to the incident.

Potential evidence sources include:

- logs,
- code,
- documentation,
- configuration,
- runbooks,
- historical information,
- event/incident context.

The purpose is to give the diagnosis engine relevant project/domain context.

---

## 8.4 AI diagnosis

The AI/RAG subsystem retrieves relevant information and generates a probable diagnosis.

The diagnosis should be associated with the evidence used to support it.

Conceptually:

```text
Incident
   ↓
Retrieval
   ↓
Relevant Evidence
   ↓
AI Reasoning
   ↓
Probable Root Cause
```

RAG is intended to ground the diagnosis; it does not guarantee correctness.

---

## 8.5 Remediation proposal

The AI diagnosis can produce a proposed remediation plan.

The system should distinguish:

```text
Diagnosis
   ↓
RemediationPlan
   ↓
RemediationAction(s)
```

A proposal is not automatically an executed change.

---

## 8.6 Human approval

Before consequential remediation is applied in the MVP:

```text
AI proposal
    ↓
Engineer review
    ↓
Explicit approval
```

A rejected proposal must not be executed.

---

## 8.7 Remediation execution

After approval, the appropriate adapter/executor performs the approved action.

For the MVP, Git/GitHub is the concrete remediation integration.

A representative flow is:

```text
Approved Action
      ↓
Git / GitHub
      ↓
Pull Request
      ↓
CI/CD Validation
```

---

## 8.8 Verification

The platform must verify the resulting state.

The product must distinguish:

```text
Execution completed
```

from:

```text
Incident resolved
```

Resolution requires successful verification.

---

# 9. Functional Requirements

## FR-01 — Event ingestion

The system shall accept supported operational/CI-CD events.

## FR-02 — Event normalization

The system shall transform provider-specific event information into the platform's normalized event representation.

## FR-03 — Incident creation/correlation

The system shall create or update an incident based on relevant normalized events.

## FR-04 — Evidence association

The system shall associate relevant evidence with an incident.

## FR-05 — Evidence-grounded diagnosis

The system shall use the AI/RAG subsystem to generate a probable diagnosis based on retrieved project/domain evidence.

## FR-06 — Diagnosis traceability

The system shall preserve references to evidence used to support the diagnosis.

## FR-07 — Remediation planning

The system shall represent one or more proposed remediation actions associated with a diagnosis.

## FR-08 — Human approval

The system shall require explicit human approval before consequential MVP remediation is executed.

## FR-09 — Approval enforcement

The system shall prevent an unapproved consequential remediation from being executed through the governed workflow.

## FR-10 — Remediation execution

The system shall execute an approved remediation through the appropriate adapter/executor.

## FR-11 — GitHub integration

The MVP shall support Git/GitHub as the concrete remediation workflow.

## FR-12 — Verification

The system shall verify the result of an executed remediation.

## FR-13 — Incident lifecycle

The system shall maintain the lifecycle state of an incident across detection, diagnosis, remediation, approval, execution, and verification.

## FR-14 — Developer Cockpit

The system shall provide an engineer-facing interface for incident inspection and remediation approval.

## FR-15 — Auditability/traceability

The system shall preserve enough lifecycle information to connect:

```text
Event
→ Incident
→ Evidence
→ Diagnosis
→ Remediation
→ Approval
→ Execution
→ Verification
```

---

# 10. Non-Functional Requirements

## NFR-01 — Modularity

The platform should separate:

- API,
- asynchronous worker,
- AI worker,
- frontend,
- persistence,
- adapters.

## NFR-02 — Maintainability

Generic platform logic should not contain unnecessary domain-specific branching.

## NFR-03 — Extensibility

The architecture should allow future domain/integration adapters without redesigning the generic incident workflow.

## NFR-04 — Security

Secrets and external credentials must be protected.

AI-generated remediation must not bypass the governance boundary.

## NFR-05 — Reliability

The system should distinguish failed execution and failed verification from successful resolution.

## NFR-06 — Observability

The platform should provide sufficient operational visibility to evaluate incident processing and later hardening requirements.

## NFR-07 — Testability

Shared contracts and component boundaries must be testable independently and as an integrated flow.

## NFR-08 — Performance

The platform should support the project's goal of reducing operational detection and recovery time. Performance must be evaluated against appropriate baselines during later testing.

---

# 11. Developer Cockpit Requirements

The Developer Cockpit should provide an engineer with visibility into:

### Incident

- identity,
- status,
- related event/context,
- affected service/deployment/pipeline/environment information.

### Evidence

- evidence associated with the incident,
- sources relevant to diagnosis.

### Diagnosis

- probable root cause,
- supporting evidence,
- explanation,
- remediation proposal.

### Approval

- proposed actions,
- approval/rejection controls,
- approval state.

### Execution

- approved action,
- execution state,
- resulting change,
- GitHub/CI information for the MVP.

### Verification

- verification state,
- resulting incident state,
- resolution/failure information.

The UI must not represent an AI proposal as an already-executed fix.

---

# 12. AI/RAG Requirements

The AI subsystem should support:

1. incident context ingestion,
2. relevant knowledge retrieval,
3. evidence-grounded reasoning,
4. probable root-cause generation,
5. remediation proposal generation.

Knowledge sources may include:

```text
Logs
Code
Documentation
Configuration
Runbooks
Historical information
Incident context
```

The AI subsystem does not own:

- final approval,
- direct consequential execution,
- final verification.

---

# 13. Adapter Requirements

The adapter layer should isolate domain/integration-specific behavior.

An adapter may provide:

- domain configuration,
- knowledge-base configuration,
- telemetry/event normalization,
- remediation execution,
- verification.

### E-commerce reference adapter

The first adapter must support the operational requirements of the e-commerce reference environment.

### Future adapters

Future adapters should be able to implement the corresponding domain/integration behavior while the generic incident/evidence/diagnosis/remediation workflow remains reusable.

A future adapter does not imply that every possible remediation action is automatically supported.

---

# 14. Technology Requirements

The current project technology stack is:

| Product area | Technology |
|---|---|
| API | Python 3.12 + FastAPI |
| Worker | Python 3.12 + RQ |
| AI worker | Python 3.12 + FastAPI + LangChain |
| Web | TypeScript + Next.js / React |
| Database | PostgreSQL |
| Queue/cache | Redis |
| Containers | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Version control | Git / GitHub |

These technologies are part of the current project baseline.

---

# 15. System Architecture Requirements

At the product level, the system should follow:

```text
Developer Cockpit
        ↓
Domain-Agnostic API
        ↓
Incident / Evidence Core
        ↓
Detection / RAG / Remediation
        ↓
Adapter Interface
        ↓
E-Commerce Reference Adapter
```

The adapter boundary is the main separation between reusable platform behavior and reference-domain behavior.

---

# 16. Product Safety and Governance

The MVP uses bounded autonomy.

The product must not silently transition from:

```text
AI-generated recommendation
```

to:

```text
consequential system change
```

without the required approval.

The intended governance sequence is:

```text
Detect
  ↓
Diagnose
  ↓
Evidence-backed remediation
  ↓
Policy / risk validation
  ↓
Human approval
  ↓
Execute
  ↓
Verify
  ↓
Record
```

---

# 17. Product Metrics

The current requirements define these targets:

| Metric | Target |
|---|---:|
| Mean Time to Detect (MTTD) | 50% reduction vs manual baseline |
| Mean Time to Resolve (MTTR) | 30–50% reduction vs manual baseline |
| Automated resolution | ≥70% of incidents via AI-suggested, human-approved fixes |
| Availability | ≥99.9% |

These are **success targets, not current measurements**.

Evaluation must establish the baseline and measurement methodology before claiming achievement.

---

# 18. Delivery Plan

The product roadmap follows P0–P12.

| Phase | Product outcome | Current status |
|---|---|---|
| P0 | Governance and repository bootstrap | Complete |
| P1 | Technical foundation | Complete / initial foundation |
| P2 | Contracts and domain foundation | Next |
| P3 | Parallel component construction | Not started |
| P4 | Event and incident pipeline | Not started |
| P5 | AI diagnosis and RAG | Not started |
| P6 | Remediation and GitHub automation | Not started |
| P7 | Developer Cockpit | Not started |
| P8 | End-to-end integration | Not started |
| P9 | Security/performance/reliability hardening | Not started |
| P10 | Staging and rollback demonstration | Not started |
| P11 | Production release | Not started |
| P12 | Post-MVP evolution/scaling | Not started |

---

# 19. Current Product State

The current project has completed the initial foundation.

The report identifies:

- P0 complete,
- P1 foundation complete,
- all four application skeletons booting,
- PostgreSQL and Redis connectivity working,
- automated CI checks performed,
- manual end-to-end foundation checks performed.

The following remain future work:

- business logic,
- real incident detection,
- AI diagnosis,
- RAG,
- remediation,
- full frontend workflow,
- complete end-to-end self-healing.

The next major product milestone is **P2 — Contract & Domain Foundation**.

---

# 20. Product Acceptance Criteria

The MVP should ultimately demonstrate that:

1. an operational event can enter the platform;
2. the event can be normalized;
3. an incident can be created/correlated;
4. relevant evidence can be associated;
5. RAG can retrieve project/domain knowledge;
6. an AI diagnosis can be produced;
7. the diagnosis can be linked to supporting evidence;
8. a remediation proposal can be generated;
9. an engineer can review it;
10. an engineer can explicitly approve it;
11. the approved action can be executed through the appropriate adapter;
12. the e-commerce MVP can use Git/GitHub in the remediation workflow;
13. the resulting state can be verified;
14. the complete lifecycle is visible in the Developer Cockpit;
15. the lifecycle information remains traceable from event through verification.

---

# 21. Explicit Product Boundaries

The following are not product requirements:

### Not required

- making e-commerce concepts universal,
- allowing unrestricted autonomous production changes,
- treating an LLM response as proof of root cause,
- treating a created pull request as proof of resolution,
- claiming universal support for every CI/CD provider,
- claiming every future domain can be integrated without any engineering work,
- claiming the project is inherently novel merely because it uses AI/RAG.

The project should demonstrate its architectural and operational claims through implementation and evaluation.

---

# 22. Product Principles

The product should consistently follow these principles:

### Principle 1 — Generic core

Build the reusable operational workflow around generic concepts.

### Principle 2 — Adapter isolation

Keep domain/integration-specific behavior behind adapters.

### Principle 3 — Evidence before action

Ground diagnosis and remediation proposals in relevant evidence.

### Principle 4 — Human-governed remediation

Require human approval before consequential MVP remediation.

### Principle 5 — Verification before resolution

Do not call an incident resolved until the resulting state is verified.

### Principle 6 — Contracts before parallel implementation

Freeze shared contracts before independent component implementation.

### Principle 7 — Measured claims

Treat metrics as targets until measured.

### Principle 8 — Implementation honesty

Never describe planned functionality as implemented.

---

# 23. Final Product Model

The product can be summarized as:

```text
                DOMAIN-AGNOSTIC AIOps PLATFORM

Operational Event
       ↓
Detection / Correlation
       ↓
Incident
       ↓
Evidence
       ↓
RAG Diagnosis
       ↓
Remediation Proposal
       ↓
Human Approval
       ↓
Adapter / Executor
       ↓
Actual Change
       ↓
Verification
       ↓
Recorded Outcome


             FIRST REFERENCE IMPLEMENTATION
                         ↓
                 E-Commerce Adapter
```

The product's central purpose is not merely to generate an AI answer to an incident. It is to establish a controlled lifecycle connecting **operational signal, evidence, diagnosis, remediation, human approval, execution, and verification** within a reusable AIOps architecture.
