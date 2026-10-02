"""Foundation tests for apps/api HTTP endpoints."""
import os
import sys
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

# Add apps/api to path
api_path = Path(__file__).resolve().parents[2] / "apps" / "api"
sys.path.insert(0, str(api_path))

from src.main import app

client = TestClient(app)


def test_api_root_endpoint():
    """Verify that root endpoint returns service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "aiops-api"
    assert data["status"] == "online"


def test_api_health_endpoint():
    """Verify that API liveness probe returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "api"


@patch("src.main.check_database_connection")
def test_api_ready_endpoint_healthy(mock_db_check):
    """Verify readiness probe returns 200 when database connection succeeds."""
    mock_db_check.return_value = (True, "PostgreSQL connection healthy")
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"]["connected"] is True


@patch("src.main.check_database_connection")
def test_api_ready_endpoint_unhealthy(mock_db_check):
    """Verify readiness probe returns 503 when database connection fails."""
    mock_db_check.return_value = (False, "Connection timeout")
    response = client.get("/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["database"]["connected"] is False
