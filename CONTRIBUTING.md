# Contributing to AIOps Self-Healing Platform

## 1. Governance & Ownership Model

The project is developed under a four-member engineering ownership model:

| Member | Role | Primary Responsibility |
|---|---|---|
| **Rudra** | AI / RAG Lead | `apps/ai-worker`, RAG pipeline, LLM integration, diagnosis, remediation proposal generation |
| **Saurav** | DevOps Lead | Infrastructure, containers, Docker Compose, CI/CD, deployment, staging/release |
| **Taranay** | Backend Lead | `apps/api`, `apps/worker`, database schema, shared API/event contracts |
| **Vivek** | Frontend Lead | `apps/web`, Developer Cockpit, incident and approval workflows |

### Ownership Boundaries
- No member (or AI assistant) may unilaterally modify another member's subsystem without explicit coordination.
- Shared contracts (`packages/contracts`, database models, shared event schemas, core documents) require unanimous agreement across all four leads.

---

## 2. Sequential Phase Execution

All work strictly follows the sequential roadmap defined in [Phases.md](Phases.md):
```text
P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10 → P11 → P12
```
- No phase may begin until the preceding phase is formally verified and signed off.
- Do NOT jump directly to AI/RAG, remediation, or UI features ahead of phase progression.

---

## 3. Git Workflow & Branch Strategy

- **Default Branch**: `main` (protected; no direct pushes permitted).
- **Branch Naming**:
  - `feat/<owner>-<feature-description>` (e.g., `feat/taranay-api-foundation`)
  - `fix/<owner>-<bug-description>` (e.g., `fix/saurav-docker-networking`)
  - `docs/<owner>-<doc-update>` (e.g., `docs/rudra-rag-adr`)
  - `chore/<owner>-<task>` (e.g., `chore/vivek-ts-lint`)

### Pull Request (PR) Requirements
1. Open a PR against `main` using the PR template (`.github/pull_request_template.md`).
2. Required CI checks must pass completely.
3. Review and approval from relevant CODEOWNERS is mandatory.
4. For cross-boundary or shared-contract changes, approval from affected leads is required.

---

## 4. Commit Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat(<scope>): <description>` — New foundational or phase feature
- `fix(<scope>): <description>` — Bug fix
- `docs(<scope>): <description>` — Documentation changes
- `test(<scope>): <description>` — Adding or refactoring tests
- `chore(<scope>): <description>` — Dependency, build, or tooling updates
- `refactor(<scope>): <description>` — Code change neither fixing a bug nor adding a feature

**Scopes**: `api`, `worker`, `ai-worker`, `web`, `infra`, `contracts`, `docs`, `ci`.

---

## 5. Architectural Non-Negotiables

1. **Domain Agnosticity**: The core platform is domain-agnostic. E-commerce is the first reference implementation, NOT the platform definition. No e-commerce domain terms (`order_id`, `cart`, `payment_status`, `inventory`) in the generic core.
2. **Evidence Grounding**: AI diagnosis is evidence-grounded, not speculative.
3. **Governed Remediation**: AI proposes; human approves; system executes; system verifies. No autonomous fixes without human approval in MVP.
4. **Execution != Resolution**: Successful execution does not equal resolution; explicit verification is mandatory.
