# Shared Contracts & Domain Foundation

> **Phase Boundary:** Phase P2 (Contract & Domain Foundation)  
> **Status:** COMPLETE — Formally agreed and approved by all leads (Saurav, Taranay, Rudra, Vivek).

## Purpose
Phase P2 establishes the shared, domain-agnostic Pydantic v2 data models used across all platform subsystems (`apps/api`, `apps/worker`, `apps/ai-worker`, `apps/web`):

1. **Common Foundation (`common.py`):**
   - `ContractModel` (configured with `extra="forbid"` to strictly prevent domain leakage)
   - `new_id()` (UUID4 generator)
   - `utc_now()` (timezone-aware UTC timestamps)

2. **Event Ingestion (`event.py`):**
   - `EventType` enum (`pipeline_run`, `deployment`, `telemetry`, `external`)
   - `Event` model (captures raw failure signals)

3. **Incident Correlation (`incident.py`):**
   - `Severity` enum (`low`, `medium`, `high`, `critical`)
   - `IncidentStatus` enum (`open`, `diagnosing`, `awaiting_approval`, `executing`, `verifying`, `resolved`, `closed`)
   - `Incident` model (central correlation record)

4. **Evidence Collection (`evidence.py`):**
   - `EvidenceKind` enum (`log`, `stack_trace`, `commit`, `pipeline_info`, `configuration`, `metric`, `documentation`, `knowledge_base`)
   - `Evidence` model (immutable factual observations)

5. **AI Root-Cause Diagnosis (`diagnosis.py`):**
   - `Diagnosis` model (AI inference with root cause, confidence score `0.0` to `1.0`, and supporting/contradicting evidence links)

6. **Remediation Actions & Plans (`remediation.py`):**
   - `ActionType` enum (`pull_request`, `rollback`, `container_restart`, `config_update`, `scale_service`)
   - `PlanStatus` enum (`drafted`, `approved`, `rejected`, `executing`, `completed`, `failed`)
   - `RemediationAction` and `RemediationPlan` models

7. **Human-in-the-Loop Governance (`approval.py`):**
   - `ApprovalDecision` enum (`pending`, `approved`, `rejected`)
   - `Approval` model (immutable sign-off log)

8. **Post-Remediation Verification (`verification.py`):**
   - `VerificationStatus` enum (`pending`, `passed`, `failed`)
   - `Verification` model (health check telemetry confirmation)

## Inviolable Rules
- **Domain Agnosticity:** Business-specific terms (e.g., `order_id`, `cart`, `payment_status`, `inventory`) are strictly forbidden in this directory.
- **Strict Extensibility:** Any attempt to inject unmodeled fields will trigger a `ValidationError` due to `extra="forbid"`.
- **Cross-Subsystem Immutability:** No subsystem lead may unilaterally redefine these shared models without 4-lead agreement.
