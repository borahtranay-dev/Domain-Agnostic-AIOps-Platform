"""Integration Tests for AIOps API Event and Incident Endpoints.

Tests:
1. POST /api/v1/events (Valid ingestion -> 201 Created)
2. POST /api/v1/events (Extra domain field 'order_id' -> 422 Unprocessable Entity)
3. GET /api/v1/events (Pagination & filtering)
4. GET /api/v1/events/{id} (Single retrieval & 404 handling)
5. POST /api/v1/incidents & GET /api/v1/incidents
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path

# Add apps/api to path so src.main and src.database import cleanly
api_path = Path(__file__).resolve().parents[1] / "apps" / "api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))

from src.main import app
from src.database import Base, get_db

# Isolated in-memory SQLite database for deterministic unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
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


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_and_health(client):
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["service"] == "aiops-api"

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"


def test_post_event_success(client):
    event_payload = {
        "type": "pipeline_run",
        "source": "github-actions",
        "summary": "CI Job Failed on step: pytest",
        "service_id": "api-service",
        "environment_id": "staging",
        "payload": {"exit_code": 1, "failed_step": "test"},
    }
    response = client.post("/api/v1/events", json=event_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["type"] == "pipeline_run"
    assert data["source"] == "github-actions"
    assert data["summary"] == "CI Job Failed on step: pytest"
    assert data["payload"]["exit_code"] == 1


def test_post_event_domain_agnostic_rejection(client):
    """Enforces that any attempt to pass e-commerce/unauthorized fields like order_id is rejected."""
    forbidden_payload = {
        "type": "pipeline_run",
        "source": "ci",
        "summary": "Leak attempt",
        "order_id": "ord-12345",
        "cart_id": "cart-67890",
    }
    response = client.post("/api/v1/events", json=forbidden_payload)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("Extra inputs are not permitted" in str(e) for e in errors)


def test_get_events_list(client):
    response = client.get("/api/v1/events")
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1


def test_get_event_by_id(client):
    # First create an event
    created = client.post(
        "/api/v1/events",
        json={"type": "telemetry", "source": "aws", "summary": "CPU Spike 98%"},
    ).json()

    event_id = created["id"]
    response = client.get(f"/api/v1/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id
    assert response.json()["type"] == "telemetry"


def test_get_event_not_found(client):
    response = client.get("/api/v1/events/non-existent-id")
    assert response.status_code == 404


def test_post_and_get_incidents(client):
    incident_payload = {
        "title": "Production Microservice Outage",
        "severity": "critical",
        "status": "open",
        "service_id": "payment-api",
        "environment_id": "production",
        "event_ids": ["evt-1", "evt-2"],
    }
    create_res = client.post("/api/v1/incidents", json=incident_payload)
    assert create_res.status_code == 201
    inc_data = create_res.json()
    assert inc_data["id"] is not None
    assert inc_data["severity"] == "critical"

    # List incidents
    list_res = client.get("/api/v1/incidents?severity=critical")
    assert list_res.status_code == 200
    incidents = list_res.json()
    assert len(incidents) >= 1
    assert incidents[0]["title"] == "Production Microservice Outage"

    # Get single incident
    get_res = client.get(f"/api/v1/incidents/{inc_data['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == inc_data["id"]
