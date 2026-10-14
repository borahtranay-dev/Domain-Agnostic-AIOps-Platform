"""Automated Tests for Phase P2 Shared Contracts.

Verifies:
1. Valid instantiation of all models (Event, Incident, Evidence, Diagnosis, Remediation, Approval, Verification).
2. Boundary constraint validations (e.g. confidence <= 1.0).
3. Domain-agnosticity constraint (ConfigDict extra="forbid" rejects any domain terms like order_id).
4. Timezone-aware UTC timestamps and unique UUIDs.
"""
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from aiops_contracts import (
    ContractModel,
    Event,
    EventType,
    Incident,
    IncidentStatus,
    Severity,
    Evidence,
    EvidenceKind,
    Diagnosis,
    ActionType,
    PlanStatus,
    RemediationAction,
    RemediationPlan,
    Approval,
    ApprovalDecision,
    Verification,
    VerificationStatus,
)


def test_event_contract():
    event = Event(
        type=EventType.PIPELINE_RUN,
        source="github-actions",
        summary="Build failed",
        payload={"commit": "abc1234"},
    )
    assert event.id is not None
    assert event.type == EventType.PIPELINE_RUN
    assert event.occurred_at.tzinfo == timezone.utc
    assert event.payload["commit"] == "abc1234"


def test_incident_contract():
    incident = Incident(
        title="CI Pipeline Failure",
        severity=Severity.HIGH,
        status=IncidentStatus.OPEN,
    )
    assert incident.id is not None
    assert incident.severity == Severity.HIGH
    assert incident.status == IncidentStatus.OPEN
    assert incident.opened_at.tzinfo == timezone.utc


def test_evidence_contract():
    evidence = Evidence(
        incident_id="inc-123",
        kind=EvidenceKind.STACK_TRACE,
        source="ci",
        content="NullPointerException at line 42",
    )
    assert evidence.id is not None
    assert evidence.kind == EvidenceKind.STACK_TRACE
    assert evidence.incident_id == "inc-123"


def test_diagnosis_contract_and_boundary():
    # Valid diagnosis
    d = Diagnosis(
        incident_id="inc-123",
        probable_root_cause="Database port mismatch",
        confidence=0.88,
        supporting_evidence_ids=["ev-1", "ev-2"],
    )
    assert d.confidence == 0.88
    assert len(d.supporting_evidence_ids) == 2

    # Invalid diagnosis: confidence > 1.0
    with pytest.raises(ValidationError):
        Diagnosis(
            incident_id="inc-123",
            probable_root_cause="Test",
            confidence=1.5,
        )

    # Invalid diagnosis: confidence < 0.0
    with pytest.raises(ValidationError):
        Diagnosis(
            incident_id="inc-123",
            probable_root_cause="Test",
            confidence=-0.1,
        )


def test_remediation_contracts():
    action = RemediationAction(
        plan_id="plan-1",
        action_type=ActionType.PULL_REQUEST,
        description="Fix database port in config.py",
        parameters={"branch": "fix/db-port", "pr_number": 42},
    )
    assert action.action_type == ActionType.PULL_REQUEST
    assert action.parameters["pr_number"] == 42

    plan = RemediationPlan(
        incident_id="inc-123",
        diagnosis_id="diag-1",
        rationale="Reverting broken port configuration",
        risk_level=Severity.LOW,
        actions=[action],
    )
    assert plan.status == PlanStatus.DRAFTED
    assert len(plan.actions) == 1


def test_approval_contract():
    approval = Approval(
        incident_id="inc-123",
        plan_id="plan-1",
        approver_id="saurav@devops.lead",
        decision=ApprovalDecision.APPROVED,
        notes="Safe to apply immediately",
    )
    assert approval.decision == ApprovalDecision.APPROVED
    assert approval.approver_id == "saurav@devops.lead"


def test_verification_contract():
    verification = Verification(
        incident_id="inc-123",
        plan_id="plan-1",
        status=VerificationStatus.PASSED,
        telemetry_summary="All health endpoints returning HTTP 200 OK",
        metrics={"latency_ms": 12.4, "error_rate": 0.0},
    )
    assert verification.status == VerificationStatus.PASSED
    assert verification.metrics["error_rate"] == 0.0


@pytest.mark.parametrize(
    "model_cls,valid_kwargs",
    [
        (Event, {"type": EventType.TELEMETRY, "source": "aws"}),
        (Incident, {"title": "Test Incident"}),
        (Evidence, {"incident_id": "i1", "kind": EvidenceKind.LOG, "source": "s", "content": "c"}),
        (Diagnosis, {"incident_id": "i1", "probable_root_cause": "cause", "confidence": 0.9}),
        (RemediationAction, {"plan_id": "p1", "action_type": ActionType.ROLLBACK, "description": "d"}),
        (RemediationPlan, {"incident_id": "i1", "diagnosis_id": "d1", "rationale": "r"}),
        (Approval, {"incident_id": "i1", "plan_id": "p1", "approver_id": "dev"}),
        (Verification, {"incident_id": "i1", "plan_id": "p1"}),
    ],
)
def test_domain_agnostic_extra_fields_rejection(model_cls, valid_kwargs):
    """Enforces that extra='forbid' rejects all unauthorized/domain fields."""
    forbidden_kwargs = {**valid_kwargs, "order_id": "12345", "cart_id": "67890"}
    with pytest.raises(ValidationError) as exc_info:
        model_cls(**forbidden_kwargs)
    assert "Extra inputs are not permitted" in str(exc_info.value)
