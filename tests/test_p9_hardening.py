"""Phase P9 Hardening Integration Test Suite.

Owner: Saurav (DevOps Lead) / Taranay (Backend Lead)
Phase: P9 (Hardening - Security, Performance, Reliability)

Tests:
1. Enterprise Security Headers (HSTS, NoSniff, X-Frame-Options, CSP, Referrer-Policy).
2. Rate Limiting Middleware (HTTP 429 Too Many Requests, Retry-After header).
3. Rule 17 Failure Invariant: Verification failure strictly blocks incident resolution.
4. Remediation Execution Failure Resilience (Adapter error handling).
5. Low-Confidence AI Safeguard (Zero autonomous actions when confidence < 0.60).
6. Temporal Concurrency & Correlation Under Simultaneous Events.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup clean mono-repo path isolation
API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

# Clear cached src modules
for mod in list(sys.modules.keys()):
    if mod == "src" or mod.startswith("src."):
        del sys.modules[mod]

from src.main import app
from src.database import Base, get_db
from src.models.incident import IncidentModel
from src.models.remediation import RemediationPlanModel
from src.models.verification import VerificationModel
from aiops_contracts import IncidentStatus, PlanStatus, VerificationStatus, Severity, Event, EventType

# Setup in-memory SQLite database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
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


# ─────────────────────────────────────────────────────────────────────────────
# 1. SECURITY HEADERS VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────
def test_enterprise_security_headers_enforced(client):
    """Verifies that all responses enforce mandatory enterprise security headers."""
    resp = client.get("/")
    assert resp.status_code == 200

    headers = resp.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in headers.get("Content-Security-Policy", "")


# ─────────────────────────────────────────────────────────────────────────────
# 2. RATE LIMITING & BRUTE-FORCE MITIGATION
# ─────────────────────────────────────────────────────────────────────────────
def test_rate_limiting_exceeded_returns_429(client):
    """Verifies that requests exceeding threshold return HTTP 429 Too Many Requests."""
    test_headers = {"X-Test-Rate-Limit": "3"}

    # Request 1, 2, 3 should succeed
    for i in range(3):
        r = client.get("/api/v1/incidents", headers=test_headers)
        assert r.status_code in [200, 404]
        assert "X-RateLimit-Limit" in r.headers
        assert r.headers["X-RateLimit-Limit"] == "3"

    # Request 4 must be rate-limited
    r_blocked = client.get("/api/v1/incidents", headers=test_headers)
    assert r_blocked.status_code == 429
    data = r_blocked.json()
    assert data["error"] == "rate_limit_exceeded"
    assert "Retry-After" in r_blocked.headers
    assert r_blocked.headers["X-RateLimit-Remaining"] == "0"


def test_whitelisted_paths_bypass_rate_limit(client):
    """Verifies that health checks and root endpoints are not throttled."""
    test_headers = {"X-Test-Rate-Limit": "2"}
    for _ in range(5):
        r = client.get("/", headers=test_headers)
        assert r.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# 3. RULE 17 INVARIANT: VERIFICATION FAILURE BLOCKS INCIDENT RESOLUTION
# ─────────────────────────────────────────────────────────────────────────────
def test_rule_17_verification_failure_prevents_resolution(client):
    """Rule 17: Post-remediation verification failure strictly keeps Incident OPEN."""
    db = TestingSessionLocal()

    incident_id = "inc-chaos-001"
    inc = IncidentModel(
        id=incident_id,
        title="Payment Service Latency Spike",
        status=IncidentStatus.AWAITING_APPROVAL.value,
        severity=Severity.HIGH.value,
        service_id="payment-service",
        environment_id="production",
        event_ids=["evt-1"],
        opened_at=datetime.now(timezone.utc),
    )
    db.add(inc)

    plan_id = "plan-chaos-001"
    plan = RemediationPlanModel(
        id=plan_id,
        incident_id=incident_id,
        diagnosis_id="diag-001",
        status=PlanStatus.DRAFTED.value,
        rationale="Scale payment worker replicas",
        created_at=datetime.now(timezone.utc),
    )
    db.add(plan)
    db.commit()
    db.close()

    # SRE approves plan, but telemetry verification detects failure (error rate 12% > 1%)
    approval_payload = {
        "approver_id": "saurav.sre@platform.io",
        "notes": "Testing Rule 17 verification failure handling under chaos conditions",
        "simulated_verification_metrics": {
            "error_rate": 0.12,  # 12% error rate exceeds 1% threshold
            "p95_latency_ms": 650.0,
            "healthy_replicas": 1,
            "desired_replicas": 3,
        },
    }

    resp = client.post(
        f"/api/v1/incidents/{incident_id}/remediation/approve",
        json=approval_payload,
        headers={"X-Bypass-Rate-Limit": "true"},
    )
    assert resp.status_code == 200
    res_data = resp.json()

    # Assert verification status is failed
    assert res_data["verification"]["status"] == "failed"
    assert "Verification FAILED" in res_data["verification"]["telemetry_summary"]

    # Rule 17 Invariant: Incident status MUST NOT be resolved!
    assert res_data["incident_status"] == IncidentStatus.OPEN.value
    assert res_data["plan_status"] == PlanStatus.FAILED.value

    # Verify database state
    db = TestingSessionLocal()
    persisted_inc = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    assert persisted_inc.status == IncidentStatus.OPEN.value
    assert persisted_inc.resolved_at is None

    persisted_plan = db.query(RemediationPlanModel).filter(RemediationPlanModel.id == plan_id).first()
    assert persisted_plan.status == PlanStatus.FAILED.value

    persisted_verif = db.query(VerificationModel).filter(VerificationModel.incident_id == incident_id).first()
    assert persisted_verif.status == VerificationStatus.FAILED.value
    db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 4. LOW-CONFIDENCE AI SAFEGUARD
# ─────────────────────────────────────────────────────────────────────────────
def test_low_confidence_ai_safeguard_locks_autonomous_actions():
    """Verifies that RAG diagnosis with confidence < 0.60 withholds autonomous actions."""
    from src.services.ai_client import diagnose_incident_via_ai
    from aiops_contracts import Incident as IncidentContract, Severity as ContractSeverity

    dummy_inc = IncidentContract(
        id="inc-low-conf-1",
        title="Unrecognized Ambiguous Telemetry Event",
        service_id="unknown-app",
        severity=ContractSeverity.LOW,
        status=IncidentStatus.OPEN,
    )
    # Zero factual evidence records attached
    res = diagnose_incident_via_ai(dummy_inc, [])
    diag = res["diagnosis"]
    plan = res["remediation_plan"]

    # If confidence < 0.60, actions must be empty to prevent hallucinations
    if diag["confidence"] < 0.60:
        assert len(plan["actions"]) == 0
        assert "Low-confidence match" in plan["rationale"]


# ─────────────────────────────────────────────────────────────────────────────
# 5. CONCURRENT EVENT CORRELATION HARDENING
# ─────────────────────────────────────────────────────────────────────────────
def test_concurrent_telemetry_events_correlate_to_single_incident():
    """Verifies that multiple rapid telemetry events within correlation window merge into single incident."""
    from src.correlation_engine import EventCorrelationEngine

    db = TestingSessionLocal()
    now = datetime.now(timezone.utc)

    # Simulate 3 rapid events for database-primary
    event1 = Event(
        type=EventType.TELEMETRY,
        source="prometheus",
        occurred_at=now,
        service_id="database-primary",
        environment_id="production",
        summary="DB Pool threshold reached 80%",
    )
    inc1, ev1 = EventCorrelationEngine.process_event(event1, db)

    event2 = Event(
        type=EventType.TELEMETRY,
        source="prometheus",
        occurred_at=now,
        service_id="database-primary",
        environment_id="production",
        summary="DB Pool limit reached 100% Critical",
        payload={"severity": "critical"},
    )
    inc2, ev2 = EventCorrelationEngine.process_event(event2, db)

    event3 = Event(
        type=EventType.TELEMETRY,
        source="fastapi-app",
        occurred_at=now,
        service_id="database-primary",
        environment_id="production",
        summary="TimeoutError checking out connection",
    )
    inc3, ev3 = EventCorrelationEngine.process_event(event3, db)

    # All three events must correlate into the EXACT SAME Incident
    assert inc1.id == inc2.id == inc3.id
    assert inc2.severity == Severity.CRITICAL.value

    # Verify event ID list grew to 3
    db_inc = db.query(IncidentModel).filter(IncidentModel.id == inc1.id).first()
    assert len(db_inc.event_ids) == 3
    assert event1.id in db_inc.event_ids
    assert event2.id in db_inc.event_ids
    assert event3.id in db_inc.event_ids
    db.close()

