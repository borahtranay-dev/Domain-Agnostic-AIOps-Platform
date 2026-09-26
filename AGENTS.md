# AGENTS.md — AI Coding Assistant Directives

These guidelines are binding on Antigravity and any other AI coding assistant operating in this repository.

## 1. Core Operating Principles

1. **Inspect Before Modifying**:
   - Always inspect the actual file tree, existing code, and current phase status before making any assumptions or modifying files.
   - Do NOT assume documented future capabilities are already implemented.

2. **Strict Phase Discipline**:
   - Work strictly within the current active phase (`P0` -> `P1` -> `P2` ...).
   - NEVER jump ahead to later-phase features (e.g., jumping to RAG diagnosis or automated remediation before foundational phases are verified).

3. **Subsystem Scope & Ownership**:
   - Stay within the assigned subsystem scope:
     - `apps/ai-worker`: Rudra (AI / RAG)
     - `infrastructure/`, `.github/`: Saurav (DevOps)
     - `apps/api`, `apps/worker`: Taranay (Backend)
     - `apps/web`: Vivek (Frontend)
   - Do NOT unilaterally modify another subsystem without cross-boundary alignment.

4. **Shared Contracts Are Inviolable**:
   - Shared entities, database models, and API schemas (`packages/contracts`) require explicit coordination across all four owners.
   - Never introduce ad-hoc, divergent schema models.

5. **Avoid Blind Rewrites**:
   - Do not replace entire files or wipe existing implementations simply because generation is easier.
   - Inspect, classify, make minimal surgical changes, and preserve working code.

6. **Domain-Agnosticity Test**:
   - The core platform is domain-agnostic.
   - Never leak e-commerce-specific attributes (`order_id`, `cart`, `payment_status`, `inventory`) into the generic platform core (`Incident`, `Evidence`, `Diagnosis`, `RemediationAction`, `Verification`).
   - Domain-specific logic belongs exclusively behind the adapter boundary.

7. **Verification After Changes**:
   - Always run linting, type-checking, tests, and startup verification after modifying code.
   - Do not claim completion without empirical proof of successful execution.
