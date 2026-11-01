"""Phase P4 Webhook Adapters Integration Tests.

Verifies that raw provider payloads (Prometheus Alertmanager, GitHub Actions, Generic App Webhooks)
are correctly normalized into domain-agnostic P2 Event contracts without leaking forbidden terms.
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Mono-repo namespace isolation: Ensure apps/api is prioritized at index 0
API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

# Clear cached src modules
for mod in list(sys.modules.keys()):
    if mod == "src" or mod.startswith("src."):
        del sys.modules[mod]

from src.main import app
from src.database import Base, get_db
from aiops_contracts import EventType

# Setup test in-memory SQLite database
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


# ─────────────────────────────────────────────────────────────────────────────
# 1. Prometheus Alertmanager Adapter Tests
# ─────────────────────────────────────────────────────────────────────────────
def test_prometheus_webhook_ingestion(client):
    """Test raw Prometheus Alertmanager payload normalization into P2 Event."""
    prometheus_payload = {
        "receiver": "aiops-webhook",
        "status": "firing",
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "PostgresConnectionPoolExhausted",
                    "service": "auth-service",
                    "severity": "critical",
                    "environment": "production",
                    "job": "postgres-exporter",
                },
                "annotations": {
                    "summary": "QueuePool limit of size 10 overflow 20 reached",
                    "description": "Database connection checkout timed out after 30 seconds",
                },
                "startsAt": "2026-11-01T12:00:00Z",
                "generatorURL": "http://prometheus:9090/graph?g0.expr=pg_pool_exhausted",
            }
        ],
    }

    response = client.post("/api/v1/webhooks/prometheus", json=prometheus_payload)
    assert response.status_code == 201

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    event = data[0]
    assert event["type"] == EventType.TELEMETRY.value
    assert event["source"] == "prometheus-alertmanager"
    assert event["service_id"] == "auth-service"
    assert event["environment_id"] == "production"
    assert "QueuePool limit of size 10" in event["summary"]
    assert event["payload"]["alertname"] == "PostgresConnectionPoolExhausted"
    assert event["payload"]["status"] == "firing"

    # Verify Incident and Evidence auto-generation
    from src.models.incident import IncidentModel
    from src.models.evidence import EvidenceModel

    db = TestingSessionLocal()
    incidents = db.query(IncidentModel).filter(IncidentModel.service_id == "auth-service").all()
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.status == "open"
    assert inc.severity == "critical"
    assert event["id"] in inc.event_ids

    evidences = db.query(EvidenceModel).filter(EvidenceModel.incident_id == inc.id).all()
    assert len(evidences) == 1
    assert evidences[0].source == "prometheus-alertmanager"
    db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 2. GitHub Deployment / CI-CD Adapter Tests
# ─────────────────────────────────────────────────────────────────────────────
def test_github_deployment_webhook_ingestion(client):
    """Test raw GitHub deployment_status payload normalization into P2 Event."""
    github_payload = {
        "deployment_status": {
            "id": 892341,
            "state": "failure",
            "description": "Container image failed readiness probe on startup",
        },
        "deployment": {
            "id": 4921,
            "sha": "a1b2c3d4e5f6",
            "environment": "production",
        },
        "repository": {
            "name": "payment-api",
        },
        "sender": {
            "login": "github-actions[bot]",
        },
    }

    response = client.post(
        "/api/v1/webhooks/github",
        json=github_payload,
        headers={"X-GitHub-Event": "deployment_status"},
    )
    assert response.status_code == 201

    data = response.json()
    assert data["type"] == EventType.DEPLOYMENT.value
    assert data["source"] == "github-actions"
    assert data["service_id"] == "payment-api"
    assert data["environment_id"] == "production"
    assert "failed readiness probe" in data["summary"]
    assert data["payload"]["state"] == "failure"
    assert data["payload"]["commit"] == "a1b2c3d4e5f6"

    # Verify Incident created
    from src.models.incident import IncidentModel
    from src.models.evidence import EvidenceModel

    db = TestingSessionLocal()
    inc = db.query(IncidentModel).filter(IncidentModel.service_id == "payment-api").first()
    assert inc is not None
    assert inc.status == "open"
    assert data["id"] in inc.event_ids
    db.close()


# ─────────────────────────────────────────────────────────────────────────────
# 3. Generic Custom Application Webhook Tests
# ─────────────────────────────────────────────────────────────────────────────
def test_generic_application_webhook_ingestion(client):
    """Test raw custom application error JSON normalization into P2 Event."""
    custom_app_alert = {
        "service_name": "worker-service",
        "env": "staging",
        "error": "Redis connection timeout after 3 retries",
        "reporter": "python-sentry-client",
        "cpu_usage": 98.4,
        "memory_mb": 2048,
        # Illegal domain leakage field that MUST be sanitized by adapter
        "order_id": "ORD-9999",
        "cart_id": "CART-1234",
    }

    response = client.post("/api/v1/webhooks/generic", json=custom_app_alert)
    assert response.status_code == 201

    data = response.json()
    assert data["type"] == EventType.EXTERNAL.value
    assert data["source"] == "python-sentry-client"
    assert data["service_id"] == "worker-service"
    assert data["environment_id"] == "staging"
    assert "Redis connection timeout" in data["summary"]
    
    # Crucial Domain-Agnostic Check: The adapter must sanitize banned domain keys!
    payload = data["payload"]
    assert "order_id" not in payload
    assert "cart_id" not in payload
    assert payload["cpu_usage"] == 98.4


# ─────────────────────────────────────────────────────────────────────────────
# 4. Multi-Event Correlation & Incident Grouping Tests
# ─────────────────────────────────────────────────────────────────────────────
def test_temporal_event_correlation_and_severity_upgrade(client):
    """Verify that multiple events for the same service within window correlate to 1 incident."""
    from src.models.incident import IncidentModel
    from src.models.evidence import EvidenceModel

    # Event 1: Warning level alert
    event1_payload = {
        "service": "auth-service",
        "env": "production",
        "error": "Elevated latency on login endpoint",
        "severity": "warning",
    }
    res1 = client.post("/api/v1/webhooks/generic", json=event1_payload)
    assert res1.status_code == 201
    ev1_id = res1.json()["id"]

    db = TestingSessionLocal()
    incidents = db.query(IncidentModel).filter(IncidentModel.service_id == "auth-service").all()
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc.severity == "medium"
    assert inc.event_ids == [ev1_id]
    db.close()

    # Event 2: Critical alert for the same service arrives 1 minute later
    event2_payload = {
        "alerts": [
            {
                "status": "firing",
                "labels": {
                    "alertname": "PostgresOOMKilled",
                    "service": "auth-service",
                    "severity": "critical",
                    "environment": "production",
                },
                "annotations": {
                    "summary": "Out of memory fatal error in database process",
                },
            }
        ]
    }
    res2 = client.post("/api/v1/webhooks/prometheus", json=event2_payload)
    assert res2.status_code == 201
    ev2_id = res2.json()[0]["id"]

    # Verify: NO new incident created; original incident updated & upgraded!
    db = TestingSessionLocal()
    incidents = db.query(IncidentModel).filter(IncidentModel.service_id == "auth-service").all()
    assert len(incidents) == 1
    updated_inc = incidents[0]
    assert ev1_id in updated_inc.event_ids
    assert ev2_id in updated_inc.event_ids
    assert updated_inc.severity == "critical"  # Upgraded from medium to critical

    # Check that both evidences are attached to this single incident
    evidences = db.query(EvidenceModel).filter(EvidenceModel.incident_id == updated_inc.id).all()
    assert len(evidences) == 2
    db.close()

