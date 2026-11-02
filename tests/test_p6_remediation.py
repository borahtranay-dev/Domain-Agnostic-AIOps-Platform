"""Phase P6 Automated Remediation Engine & Human Approval Integration Tests.

Owner: Taranay (Backend Lead) / Saurav (DevOps Lead)
Phase: P6 (Remediation & GitHub Automation)

Tests:
1. Retrieval of proposed remediation plan and actions from API.
2. Rule 15 Compliance: Human-in-the-Loop approval triggers GitHub remediation adapter and marks incident remediating.
3. Rule 17 Compliance: Post-remediation verification evaluates telemetry and transitions incident to RESOLVED.
4. Human rejection workflow: Rejection records audit notes and marks plan as REJECTED.
5. Double-execution prevention: Attempting to re-approve a completed remediation plan returns HTTP 409 Conflict.
6. Domain-Agnosticity Invariant: Zero leaked e-commerce domain concepts across all remediation models.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup clean path isolation for apps/api
API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

for mod in list(sys.modules.keys()):
    if mod == "src" or mod.startswith("src."):
        del sys.modules[mod]

from src.main import app
from src.database import Base, get_db
from src.models.incident import IncidentModel
from src.models.evidence import EvidenceModel
from src.models.diagnosis import DiagnosisModel
from src.models.remediation import RemediationPlanModel, RemediationActionModel
from src.models.approval import ApprovalModel
from src.models.verification import VerificationModel
from aiops_contracts import IncidentStatus, PlanStatus, VerificationStatus, ActionType

# Setup in-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_remediation_plan_not_found(client):
    """Assert 404 is returned when querying remediation for a non-existent incident."""
    resp = client.get("/api/v1/incidents/inc-nonexistent/remediation")
    assert resp.status_code == 404
    assert "No remediation plan found" in resp.json()["detail"]


def test_end_to_end_remediation_approval_execution_and_verification(client):
    """Full P6 Golden Path:
    1. Incident diagnosed -> Drafted Remediation Plan generated.
    2. SRE approves drafted plan -> Approval recorded, GitHub PR created.
    3. Verification engine verifies healthy metrics -> Incident transitions to RESOLVED.
    """
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)

    # Setup incident in awaiting_approval state
    inc = IncidentModel(
        id="inc-p6-test-001",
        title="High Memory Saturation & Pod OOMKilled",
        status=IncidentStatus.AWAITING_APPROVAL.value,
        severity="critical",
        service_id="payment-gateway",
        pipeline_id="pipe-prod-01",
        event_ids=["evt-001", "evt-002"],
        opened_at=now,
    )
    db.add(inc)

    # Setup drafted remediation plan with a GitHub PR action
    plan = RemediationPlanModel(
        id="plan-p6-test-001",
        incident_id="inc-p6-test-001",
        diagnosis_id="diag-001",
        status=PlanStatus.DRAFTED.value,
        rationale="Memory leak in worker pool requires heap limit patch and container rollout",
        risk_level="low",
        created_at=now,
    )
    db.add(plan)

    action = RemediationActionModel(
        id="act-p6-test-001",
        plan_id="plan-p6-test-001",
        action_type=ActionType.PULL_REQUEST.value,
        description="Apply memory limit increase to 2048Mi in Helm values",
        target_service_id="payment-gateway",
        parameters={"heap_limit_mb": 2048, "target_file": "deploy/values.yaml"},
        order=1,
    )
    db.add(action)
    db.commit()

    # 1. Fetch Drafted Plan via GET
    get_resp = client.get("/api/v1/incidents/inc-p6-test-001/remediation")
    assert get_resp.status_code == 200
    plan_data = get_resp.json()
    assert plan_data["id"] == "plan-p6-test-001"
    assert plan_data["status"] == "drafted"
    assert len(plan_data["actions"]) == 1
    assert plan_data["actions"][0]["action_type"] == "pull_request"

    # 2. Human-in-the-Loop Approval via POST
    approval_payload = {
        "approver_id": "sre-lead-saurav",
        "notes": "Verified telemetry and root cause; authorized automated hotfix PR",
    }
    approve_resp = client.post("/api/v1/incidents/inc-p6-test-001/remediation/approve", json=approval_payload)
    assert approve_resp.status_code == 200
    result = approve_resp.json()

    # Assert approval record created
    assert result["approval"]["decision"] == "approved"
    assert result["approval"]["approver_id"] == "sre-lead-saurav"

    # Assert GitHub adapter execution
    assert result["execution"]["status"] == "executed"
    exec_results = result["execution"]["results"]
    assert len(exec_results) == 1
    assert exec_results[0]["adapter"] == "github"
    assert exec_results[0]["pull_request_url"].startswith("https://github.com/")
    assert "remediation/hotfix" in exec_results[0]["branch"]

    # Assert Rule 17 Post-Remediation Verification
    assert result["verification"]["status"] == "passed"
    assert "Verification PASSED" in result["verification"]["telemetry_summary"]

    # Assert Incident lifecycle transition to RESOLVED
    assert result["incident_status"] == IncidentStatus.RESOLVED.value

    # Verify directly from Database
    db.expire_all()
    updated_inc = db.query(IncidentModel).filter(IncidentModel.id == "inc-p6-test-001").first()
    assert updated_inc.status == IncidentStatus.RESOLVED.value
    assert updated_inc.resolved_at is not None

    updated_plan = db.query(RemediationPlanModel).filter(RemediationPlanModel.id == "plan-p6-test-001").first()
    assert updated_plan.status == PlanStatus.COMPLETED.value
    assert updated_plan.executed_at is not None

    verification_rec = db.query(VerificationModel).filter(VerificationModel.incident_id == "inc-p6-test-001").first()
    assert verification_rec is not None
    assert verification_rec.status == "passed"
    db.close()


def test_remediation_rejection_workflow(client):
    """Assert human rejection records rejection notes and keeps incident open for manual triage."""
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)

    inc = IncidentModel(
        id="inc-p6-reject-001",
        title="High Latency Anomaly",
        status=IncidentStatus.AWAITING_APPROVAL.value,
        severity="medium",
        service_id="auth-service",
        pipeline_id="pipe-prod-02",
        event_ids=["evt-003"],
        opened_at=now,
    )
    db.add(inc)

    plan = RemediationPlanModel(
        id="plan-p6-reject-001",
        incident_id="inc-p6-reject-001",
        diagnosis_id="diag-002",
        status=PlanStatus.DRAFTED.value,
        rationale="Restart pod cluster",
        risk_level="medium",
        created_at=now,
    )
    db.add(plan)
    db.commit()

    reject_payload = {
        "approver_id": "oncall-sre",
        "notes": "Rejected: Upstream provider is currently in scheduled maintenance window",
    }
    resp = client.post("/api/v1/incidents/inc-p6-reject-001/remediation/reject", json=reject_payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "rejected"
    assert data["plan_status"] == "rejected"
    assert data["incident_status"] == "open"

    db.expire_all()
    saved_approval = db.query(ApprovalModel).filter(ApprovalModel.plan_id == "plan-p6-reject-001").first()
    assert saved_approval is not None
    assert saved_approval.decision == "rejected"
    assert saved_approval.approver_id == "oncall-sre"
    assert "scheduled maintenance window" in saved_approval.notes
    db.close()


def test_cannot_re_execute_already_resolved_remediation(client):
    """Assert HTTP 409 Conflict when attempting to approve an already completed remediation."""
    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)

    inc = IncidentModel(
        id="inc-p6-conflict-001",
        title="Database Deadlock",
        status=IncidentStatus.RESOLVED.value,
        severity="low",
        service_id="database",
        pipeline_id="pipe-prod-03",
        event_ids=[],
        opened_at=now,
        resolved_at=now,
    )
    db.add(inc)

    plan = RemediationPlanModel(
        id="plan-p6-conflict-001",
        incident_id="inc-p6-conflict-001",
        diagnosis_id="diag-003",
        status=PlanStatus.APPROVED.value,
        rationale="Already executed",
        risk_level="low",
        created_at=now,
        executed_at=now,
    )
    db.add(plan)
    db.commit()

    resp = client.post(
        "/api/v1/incidents/inc-p6-conflict-001/remediation/approve",
        json={"approver_id": "sre", "notes": "duplicate approve"},
    )
    assert resp.status_code == 409
    assert "already been approved" in resp.json()["detail"]
    db.close()


def test_domain_agnostic_rules_in_remediation_and_verification(client):
    """Enforces Core Platform Invariant: Zero business domain terms leak into remediation or verification."""
    FORBIDDEN_DOMAIN_TERMS = ["order_id", "cart_id", "payment_status", "checkout_total", "inventory_count"]

    remediation_file = Path(__file__).resolve().parent.parent / "apps" / "api" / "src" / "routers" / "remediation.py"
    adapter_file = Path(__file__).resolve().parent.parent / "apps" / "worker" / "src" / "remediation_adapter.py"
    verif_file = Path(__file__).resolve().parent.parent / "apps" / "worker" / "src" / "verification_engine.py"

    for file_path in [remediation_file, adapter_file, verif_file]:
        content = file_path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN_DOMAIN_TERMS:
            assert term not in content, f"Domain Agnosticity Violation: Forbidden term '{term}' leaked into {file_path.name}"
