# Rules.md
# AIOps Self-Healing Platform — Engineering Rules & Conventions

> **Authoritative project direction:** This ruleset is aligned with the current Project Review Report.  
> It replaces the earlier e-commerce-only development rules. The platform is now designed as a **domain-agnostic AIOps self-healing core**, with the **e-commerce system as the first reference implementation/adapter**.
>
> These rules govern both human developers and AI coding assistants working in the repository.

---

# 1. Non-Negotiable Project Rules

## Rule 1 — Preserve the current project direction

The project is:

```text
Domain-Agnostic AIOps Self-Healing Platform
                    +
       E-Commerce Reference Implementation
```

Do not redesign the platform so that e-commerce becomes the universal domain model.

E-commerce-specific concepts must remain behind the appropriate adapter/domain boundary.

---

## Rule 2 — The Project Review Report is the project-level source of truth

When project documents conflict, the current Project Review Report takes precedence for:

- project direction,
- architecture,
- scope,
- technology stack,
- team responsibilities,
- phase status,
- success metrics,
- current implementation status.

Do not silently resolve a contradiction by inventing a new project requirement.

---

## Rule 3 — Do not confuse planned architecture with implemented functionality

Documentation may describe future capabilities.

Code, comments, status reports, and AI-generated summaries must not claim that a capability is implemented unless it actually exists and has been verified.

At the current project state:

```text
P0                    COMPLETE
Initial P1 foundation COMPLETE
P2                    NEXT
Business logic        NOT YET IMPLEMENTED
```

In particular, do not claim that the following are already complete:

- real incident detection,
- production webhook processing,
- AI diagnosis,
- production RAG,
- automated remediation,
- GitHub remediation,
- full Developer Cockpit,
- end-to-end self-healing,
- staging,
- production release.

---

# 2. Development Methodology

## Rule 4 — Follow the sequential phase plan

The project uses phases P0 through P12.

The intended methodology is strict and sequential:

```text
P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10 → P11 → P12
```

No team member should begin later-phase implementation before the current phase is formally complete.

This governance model exists because four people and four AI coding assistants are working concurrently in the same codebase.

---

## Rule 5 — P2 is the contract/domain foundation

P2 establishes:

- shared API schemas,
- shared event schemas,
- generic domain model,
- database schema.

These shared contracts must be agreed before P3 parallel component construction begins.

Do not allow individual components to independently invent incompatible representations of shared entities.

---

## Rule 6 — Shared contracts are project-wide

The following concepts require coordinated definitions:

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

A member may implement their owned component, but must not unilaterally redefine a shared contract.

---

# 3. Domain-Agnostic Design Rules

## Rule 7 — Generic concepts remain generic

The core platform should reason in terms of:

```text
Event
Incident
Evidence
Diagnosis
Remediation
Approval
Execution
Verification
```

It should not require e-commerce business concepts to perform its generic workflow.

---

## Rule 8 — E-commerce concepts stay in the reference adapter

Concepts such as:

```text
Orders
Payments
Inventory
```

are examples of e-commerce domain knowledge.

They must not become mandatory fields or assumptions in the generic incident/remediation model.

---

## Rule 9 — Use adapters for domain-specific behavior

The adapter boundary is responsible for project/domain-specific behavior such as:

- domain configuration,
- knowledge-base configuration,
- telemetry/event normalization,
- remediation execution,
- verification.

When behavior is specific to the e-commerce reference system, prefer the adapter boundary instead of adding e-commerce-specific conditionals to the generic core.

---

## Rule 10 — Do not hard-code the reference implementation into the core

Avoid patterns such as:

```python
if domain == "ecommerce":
    ...
```

inside generic incident, diagnosis, remediation, or verification logic when the behavior belongs in the adapter.

The core should communicate through stable generic interfaces/contracts.

---

# 4. AI / RAG Rules

## Rule 11 — AI diagnosis must be evidence-grounded

The AI diagnosis engine should reason using relevant project/domain knowledge, including where applicable:

- logs,
- code,
- documentation,
- configuration,
- runbooks,
- historical information,
- incident/event context.

Do not design the AI worker as an unrestricted free-form chatbot that invents incident context.

---

## Rule 12 — Preserve evidence-to-diagnosis traceability

Where the AI produces a diagnosis, the system should preserve references to the evidence used to support it.

Conceptually:

```text
Incident
   ↓
Evidence
   ↓
Diagnosis
   ↓
Remediation Proposal
```

A diagnosis should be treated as a probable explanation grounded in retrieved evidence, not as guaranteed causal truth.

---

## Rule 13 — RAG does not control consequential execution

The AI/RAG subsystem may:

- retrieve knowledge,
- analyze evidence,
- produce a probable diagnosis,
- suggest remediation.

It must not bypass the governed remediation path to directly apply a consequential fix.

---

## Rule 14 — Separate proposal from execution

Always preserve these boundaries:

```text
AI diagnosis        != remediation execution
AI proposal         != approved action
Approved action     != successful execution
Execution           != verified resolution
```

---

# 5. Remediation and Governance Rules

## Rule 15 — Human approval is mandatory for consequential MVP remediation

The required MVP flow is:

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

An AI-suggested consequential fix must not be applied without the required human approval.

---

## Rule 16 — Approval must be explicit

Do not infer approval merely because:

- a diagnosis exists,
- a remediation plan was generated,
- an engineer viewed an incident,
- a worker received a job,
- an AI model expressed high confidence.

Approval must be an explicit part of the workflow.

---

## Rule 17 — Verification is mandatory for claiming successful remediation

The system must distinguish:

```text
execution accepted
```

from:

```text
incident successfully resolved
```

A remediation should only be considered successfully resolved after the resulting state has been verified.

---

## Rule 18 — GitHub is the MVP execution integration

The MVP uses Git/GitHub as the concrete remediation workflow.

The intended path is:

```text
Approved Remediation
        ↓
Git / GitHub
        ↓
Pull Request
        ↓
CI/CD validation
        ↓
Verification
```

Do not make GitHub's provider-specific data model the generic platform model.

---

# 6. Component Ownership Rules

The four primary responsibilities are:

| Member | Role | Primary responsibility |
|---|---|---|
| Rudra | AI / RAG Lead | `apps/ai-worker`, RAG, LLM integration, remediation suggestions |
| Saurav | DevOps Lead | Infrastructure, containers, CI/CD, deployment, staging/release readiness from P10 |
| Taranay | Backend Lead | `apps/api`, `apps/worker`, database, shared API/event contracts |
| Vivek | Frontend Lead | `apps/web`, Developer Cockpit, incident and approval workflow |

Ownership means primary responsibility, not permission to change shared contracts without coordination.

---

## Rule 19 — Respect ownership boundaries

Do not modify another member's primary subsystem unnecessarily.

If a change crosses subsystem boundaries:

1. identify the affected owner,
2. agree on the contract/change,
3. implement the minimum required cross-boundary change,
4. run the relevant checks.

---

## Rule 20 — Shared-contract changes require coordination

Any change to:

- API schemas,
- event schemas,
- database/domain entities,
- inter-service message contracts,

must be communicated to all affected owners.

After P2 is frozen, such changes require explicit agreement rather than unilateral modification.

---

# 7. Repository and Git Rules

## Rule 21 — Use pull requests

Changes should move through the repository's pull-request workflow.

The current stack uses:

- Git,
- GitHub,
- GitHub Actions,
- CODEOWNERS-based review routing.

Do not treat direct unreviewed changes to shared branches as the normal collaboration model.

---

## Rule 22 — Keep commits focused

A commit should represent a coherent change.

Avoid combining unrelated:

- frontend changes,
- backend changes,
- AI changes,
- infrastructure changes,
- formatting-only changes.

Focused commits make AI-assisted collaboration easier to review and debug.

---

## Rule 23 — Do not overwrite another member's work

Before making broad changes:

- inspect the current branch/worktree state,
- inspect the affected files,
- preserve existing work,
- coordinate when ownership overlaps.

AI coding assistants must not replace a file wholesale merely because doing so is easier unless the owner has explicitly requested a replacement.

---

## Rule 24 — Do not commit generated or secret material

Never commit:

- API keys,
- access tokens,
- passwords,
- private credentials,
- `.env` secrets,
- generated secrets,
- unnecessary build artifacts.

Use the repository's intended configuration mechanism.

---

# 8. AI Coding Assistant Rules

## Rule 25 — AI assistants are implementation tools, not project authorities

An AI coding assistant may:

- inspect the repository,
- implement assigned work,
- write tests,
- refactor within scope,
- explain code,
- propose changes.

It must not independently redefine:

- project scope,
- shared domain contracts,
- architectural boundaries,
- phase order,
- ownership,
- security policy.

---

## Rule 26 — AI assistants must read before changing

Before modifying a significant subsystem, the AI assistant should inspect:

1. relevant project instructions,
2. architecture/design documentation,
3. current implementation,
4. existing contracts,
5. tests,
6. the current phase status.

Do not generate a replacement architecture from assumptions.

---

## Rule 27 — Do not blindly rewrite the repository

AI-assisted development must be incremental.

Prefer:

```text
Inspect → Plan → Modify → Test → Review
```

over:

```text
Generate entire subsystem → overwrite existing implementation
```

---

## Rule 28 — AI assistants must stay within assigned scope

A member's AI assistant should not silently implement another member's subsystem.

For example:

- Backend AI should not redesign the frontend.
- Frontend AI should not redefine database contracts.
- AI/RAG AI should not bypass remediation governance.
- DevOps AI should not alter application domain semantics without coordination.

Cross-team changes require collaboration.

---

## Rule 29 — Do not use AI output as proof of correctness

Generated code, generated diagnosis logic, and generated configuration must be tested.

The fact that an AI assistant states that code is:

- correct,
- secure,
- production-ready,
- compatible,

is not evidence by itself.

---

# 9. API and Contract Rules

## Rule 30 — Contracts before implementation

For P2/P3 work, define the shared contract before implementing dependent logic.

A contract should specify, as applicable:

- request shape,
- response shape,
- event shape,
- entity fields,
- lifecycle/status values,
- error behavior,
- ownership,
- producer,
- consumer.

---

## Rule 31 — Do not duplicate domain models

There must not be multiple incompatible definitions of the same shared entity across:

- API,
- worker,
- AI worker,
- frontend,
- database.

Shared entities should originate from the agreed contract/domain definition.

---

## Rule 32 — Provider payloads must be normalized

External provider-specific payloads should not leak directly into the generic incident model.

Conceptually:

```text
Provider Event
      ↓
Provider Parsing
      ↓
Normalized Event
      ↓
Generic Core
```

---

# 10. Backend and Worker Rules

## Rule 33 — Keep synchronous API work bounded

Long-running work such as:

- extensive evidence retrieval,
- RAG processing,
- AI analysis,
- remediation processing,
- verification,

should be handled through the appropriate asynchronous worker flow rather than blocking API requests unnecessarily.

---

## Rule 34 — Keep PostgreSQL as the persistent system of record

PostgreSQL is the project's database.

Redis supports the asynchronous processing architecture and RQ but should not silently become the authoritative persistent incident store.

---

# 11. Frontend Rules

## Rule 35 — The Developer Cockpit should expose the governed workflow

The frontend should allow engineers to inspect:

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

Do not present an AI suggestion as if it were already an executed remediation.

---

## Rule 36 — Approval UI must be explicit

The interface should clearly distinguish:

- proposed,
- approved,
- rejected/cancelled,
- executing,
- verified,
- failed/resolved states as defined by the shared contract.

The frontend must use the agreed backend contract rather than inventing independent status semantics.

---

# 12. Infrastructure and CI/CD Rules

## Rule 37 — Preserve the specified technology stack unless formally changed

Current project stack:

```text
Backend API          Python 3.12 + FastAPI
Worker               Python 3.12 + RQ
AI Worker            Python 3.12 + FastAPI + LangChain
Frontend             TypeScript + Next.js / React
Database             PostgreSQL
Queue/Cache          Redis
Containers           Docker + Docker Compose
CI/CD                GitHub Actions
Version Control      Git / GitHub
```

Do not introduce major replacement technologies merely because an AI assistant prefers them.

---

## Rule 38 — CI checks are part of normal development

The project uses GitHub Actions for automated:

- build checks,
- type checks,
- import checks.

Relevant checks must pass before a change is considered ready for integration.

---

# 13. Testing Rules

## Rule 39 — Test the contract before the feature

When implementing a new cross-component capability:

1. validate the contract,
2. test the producer,
3. test the consumer,
4. test the integrated flow.

---

## Rule 40 — Test the failure path

Do not test only the successful path.

At minimum, implementation should account for failures in:

```text
Event ingestion
Diagnosis
Approval
Execution
Verification
```

The system must not report successful self-healing when execution or verification has failed.

---

## Rule 41 — End-to-end validation matters

The project ultimately requires a complete golden path from event ingestion through verified remediation.

The P8 end-to-end phase is responsible for connecting and testing the complete flow.

---

# 14. Security Rules

## Rule 42 — Protect credentials and external integrations

Secrets and credentials must never be embedded directly into source code.

External integrations should use appropriate configuration/secrets mechanisms.

---

## Rule 43 — Treat AI-generated actions as untrusted proposals

The AI's output is not automatically trusted merely because it came from the project's RAG pipeline.

Before consequential execution, the system must apply the project's human-approval requirement.

---

# 15. Documentation Rules

## Rule 44 — Documentation must distinguish facts from plans

Use wording such as:

```text
Implemented
Planned
Target
Proposed
Not started
```

Do not describe a proposed architecture as an implemented capability.

---

## Rule 45 — Keep documentation domain-neutral where the core is domain-neutral

Use generic terms in core architecture/design documentation.

E-commerce-specific examples are acceptable when explicitly identified as the reference implementation.

---

## Rule 46 — Update documentation when an architectural decision changes

When a shared architectural decision changes, update the relevant source documents rather than allowing contradictory instructions to accumulate.

---

# 16. Phase-Specific Rules

## P0 — Governance & Repository Bootstrap

Must establish:

- ownership,
- repository structure,
- contribution rules,
- AI-assistant collaboration conventions.

**Current status: COMPLETE.**

## P1 — Technical Foundation

Must establish the working technical foundation.

**Current status: COMPLETE / INITIAL FOUNDATION.**

## P2 — Contract & Domain Foundation

Must finalize:

- shared API schemas,
- shared event schemas,
- generic domain model,
- database schema.

**Current status: NEXT.**

## P3 — Parallel Component Construction

Members implement their components against the frozen shared contracts.

Do not use P3 to redesign the core domain model independently.

## P4 — Event & Incident Pipeline

Implement real webhook ingestion and incident lifecycle.

## P5 — AI Diagnosis & RAG

Implement real RAG-based incident diagnosis.

## P6 — Remediation & GitHub Automation

Implement AI-suggested, human-approved GitHub remediation.

## P7 — Developer Cockpit

Implement the full incident/approval dashboard.

## P8 — End-to-End Integration

Test the complete golden path.

## P9 — Hardening

Address:

- security,
- performance,
- reliability.

## P10 — Staging

Implement staging, deployment pipeline, and rollback demonstration.

## P11 — Release

Prepare production release.

## P12 — Post-MVP

Continue evolution and scaling.

---

# 17. Metrics Rules

The project's current target metrics are:

| Metric | Target |
|---|---|
| MTTD | 50% reduction vs manual baseline |
| MTTR | 30–50% reduction vs manual baseline |
| Automated resolution | ≥70% of incidents via AI-suggested, human-approved fixes |
| Availability | ≥99.9% |

These are **targets**.

Do not report them as achieved without measured evidence.

When evaluation begins, define the relevant baseline and measurement method before claiming improvement.

---

# 18. Anti-Patterns

The following are explicitly discouraged.

### Anti-pattern 1 — E-commerce leakage

```text
Generic Incident
    ↓
if order/payment/inventory ...
```

Prefer adapter/domain-specific handling.

### Anti-pattern 2 — AI bypass

```text
LLM → GitHub directly
```

Do not bypass approval and governed execution.

### Anti-pattern 3 — Fake resolution

```text
PR created → Incident resolved
```

A resulting state must be verified.

### Anti-pattern 4 — Contract drift

```text
Backend Incident
    !=
AI Incident
    !=
Frontend Incident
```

Use the shared contract.

### Anti-pattern 5 — Premature implementation

Building P5/P6 behavior before P2 contracts are established creates avoidable integration conflicts.

### Anti-pattern 6 — AI-driven mass rewrite

Do not allow an AI coding assistant to rewrite unrelated parts of the repository in order to implement a local task.

---

# 19. Final Engineering Principle

The project should always preserve this chain:

```text
                 GENERIC PLATFORM CORE

Event
  ↓
Incident
  ↓
Evidence
  ↓
Diagnosis
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
Recorded Result

                 DOMAIN BOUNDARY
                        ↓
              E-Commerce Adapter
```

The system is intended to demonstrate self-healing behavior while maintaining:

- domain separation,
- evidence-grounded AI,
- human governance,
- controlled remediation,
- explicit verification,
- shared contracts,
- disciplined multi-member/AI-agent collaboration.

No future implementation decision should weaken these boundaries merely for convenience.
