"""Foundation tests for apps/ai-worker HTTP endpoints."""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add apps/ai-worker to path
ai_worker_path = Path(__file__).resolve().parents[2] / "apps" / "ai-worker"
sys.path.insert(0, str(ai_worker_path))

from src.main import app

client = TestClient(app)


def test_ai_worker_root_endpoint():
    """Verify AI Worker root endpoint returns expected service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ai-worker"
    assert data["status"] == "online"
    assert "langchain_status" in data


def test_ai_worker_health_endpoint():
    """Verify AI Worker health probe returns status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai-worker"
