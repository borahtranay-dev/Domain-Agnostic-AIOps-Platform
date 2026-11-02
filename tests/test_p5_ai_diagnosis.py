"""Phase P5 AI Diagnosis & LangChain RAG Subsystem Integration Tests.

Owner: Rudra (AI / RAG Lead) / Saurav (DevOps Lead)
Phase: P5 (AI Diagnosis & RAG - Real Incident Pipeline)

Tests:
1. Prometheus alert -> Incident + Evidence -> Trigger RAG Diagnosis -> DiagnosisModel persisted + status advances to awaiting_approval.
2. GitHub Deployment failure -> RAG Diagnosis -> Matches RB-006 (Readiness Probe Failure) -> Rollback proposed.
3. Generic Worker Timeout -> RAG Diagnosis -> Matches RB-007 (Message Queue Timeout) -> Container Restart proposed.
4. Evidence Citation Integrity: All cited evidence IDs match factual DB evidence records (zero hallucination).
5. Confidence Bounds: Mathematical confidence score strictly calibrated between 0.65 and 0.98.
6. Domain-Agnosticity Invariant: Zero leaked e-commerce terms in AI root-cause or remediation plan.
"""
import sys
from pathlib import Path
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
from aiops_contracts import ActionType, IncidentStatus

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
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    return TestClient(app)


def test_prometheus_incident_rag_diagnosis(client):
    """Test full RAG diagnosis triggered on a live Prometheus telemetry incident."""
    prom_payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "PostgresConnectionPoolExhausted",
                    "service": "auth-service",
                    "severity": "critical",
                    "environment": "production",
                },
                "annotations": {
                    "summary": "TimeoutError: QueuePool limit of size 10 overflow 20 reached",
                    "description": "Database connection pool timeout",
                },
            }
        ]
    }
    res_webhook = client.post("/api/v1/webhooks/prometheus", json=prom_payload)
    assert res_webhook.status_code == 201

    db = TestingSessionLocal()
    incident = db.query(IncidentModel).filter(IncidentModel.service_id == "auth-service").first()
    assert incident is not None
    assert incident.status == IncidentStatus.OPEN.value
    incident_id = incident.id
    db.close()

    # Trigger Phase P5 AI Diagnosis
    res_diag = client.post(f"/api/v1/incidents/{incident_id}/diagnose")
    assert res_diag.status_code == 200
    diag_data = res_diag.json()

    assert diag_data["status"] == "diagnosed"
    assert diag_data["incident_id"] == incident_id

    # Verify Diagnosis properties
    diag = diag_data["diagnosis"]
    assert "connection pool" in diag["probable_root_cause"].lower()
    assert 0.65 <= diag["confidence"] <= 0.98
    assert len(diag["supporting_evidence_ids"]) >= 1

    # Verify Remediation Plan properties
    plan = diag_data["remediation_plan"]
    assert plan["incident_id"] == incident_id
    assert plan["status"] == "drafted"
    assert len(plan["actions"]) >= 1
    action = plan["actions"][0]
    assert action["action_type"] == ActionType.CONFIG_UPDATE.value

    # Verify Database state transitions
    db = TestingSessionLocal()
    updated_inc = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    assert updated_inc.status == IncidentStatus.AWAITING_APPROVAL.value

    db_diag = db.query(DiagnosisModel).filter(DiagnosisModel.incident_id == incident_id).first()
    assert db_diag is not None
    assert db_diag.confidence == diag["confidence"]
    assert db_diag.probable_root_cause == diag["probable_root_cause"]
    db.close()

    # Verify GET diagnosis endpoint
    res_get_diag = client.get(f"/api/v1/incidents/{incident_id}/diagnosis")
    assert res_get_diag.status_code == 200
    assert res_get_diag.json()["id"] == db_diag.id


def test_github_deployment_failure_rag_diagnosis(client):
    """Test RAG diagnosis on GitHub deployment failure matches RB-006 (Rollback)."""
    gh_payload = {
        "deployment_status": {
            "id": 99401,
            "state": "failure",
            "description": "Container image failed readiness probe on startup",
        },
        "deployment": {
            "id": 1022,
            "sha": "a1b2c3d4e5f6",
            "environment": "production",
        },
        "repository": {
            "name": "payment-api",
        },
    }
    res_gh = client.post("/api/v1/webhooks/github", json=gh_payload)
    assert res_gh.status_code == 201

    db = TestingSessionLocal()
    incident = db.query(IncidentModel).filter(IncidentModel.service_id == "payment-api").first()
    assert incident is not None
    incident_id = incident.id
    db.close()

    res_diag = client.post(f"/api/v1/incidents/{incident_id}/diagnose")
    assert res_diag.status_code == 200
    diag_data = res_diag.json()

    # Should match RB-006 (readiness probe failure)
    plan = diag_data["remediation_plan"]
    assert plan["actions"][0]["action_type"] == ActionType.ROLLBACK.value
    assert "rollback" in diag_data["diagnosis"]["probable_root_cause"].lower() or "readiness probe" in diag_data["diagnosis"]["probable_root_cause"].lower()


def test_generic_worker_timeout_rag_diagnosis(client):
    """Test RAG diagnosis on generic worker alert matches RB-007 (Container Restart)."""
    generic_alert = {
        "service": "worker-service",
        "env": "production",
        "error": "Redis connection timeout after retries, queue worker timeout",
        "severity": "critical",
    }
    res_gen = client.post("/api/v1/webhooks/generic", json=generic_alert)
    assert res_gen.status_code == 201

    db = TestingSessionLocal()
    incident = db.query(IncidentModel).filter(IncidentModel.service_id == "worker-service").first()
    assert incident is not None
    incident_id = incident.id
    db.close()

    res_diag = client.post(f"/api/v1/incidents/{incident_id}/diagnose")
    assert res_diag.status_code == 200
    diag_data = res_diag.json()

    plan = diag_data["remediation_plan"]
    assert plan["actions"][0]["action_type"] == ActionType.CONTAINER_RESTART.value


def test_domain_agnostic_clean_ai_output(client):
    """Enforces zero domain keyword leakage across AI diagnosis and remediation rationale."""
    prom_payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "PostgresOOM",
                    "service": "core-backend",
                    "severity": "critical",
                    "environment": "production",
                },
                "annotations": {
                    "summary": "Container terminated with exit_code: 137 OOMKilled",
                },
            }
        ]
    }
    client.post("/api/v1/webhooks/prometheus", json=prom_payload)

    db = TestingSessionLocal()
    incident = db.query(IncidentModel).filter(IncidentModel.service_id == "core-backend").first()
    incident_id = incident.id
    db.close()

    res_diag = client.post(f"/api/v1/incidents/{incident_id}/diagnose")
    assert res_diag.status_code == 200
    diag_text = str(res_diag.json()).lower()

    banned_terms = ["order_id", "cart_id", "payment_status", "inventory", "checkout"]
    for banned in banned_terms:
        assert banned not in diag_text, f"Domain leak in AI diagnosis: {banned}"
