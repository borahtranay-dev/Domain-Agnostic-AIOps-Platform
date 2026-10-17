"""Integration and Unit Tests for apps/ai-worker (LangChain RAG Diagnosis Subsystem).

Owner: Rudra (AI / RAG Lead)
Phase: P3 (Component Construction - AI Diagnosis & RAG)

Tests:
1. GET / & GET /health (Verify service status and LangChain availability)
2. GET /api/v1/runbooks (Verify operational runbooks indexed in vector store)
3. RunbookVectorStore retrieval accuracy (Unit test matching symptoms to runbooks)
4. POST /api/v1/diagnose with DB Pool Outage (Full RAG inference, contract validity, confidence bounds)
5. POST /api/v1/diagnose with OOM Crash (Exit code 137, restart_service recommendation)
6. Domain-Agnostic Rejection (Injecting e-commerce attributes like order_id must fail with 422)
"""
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add apps/ai-worker to path and ensure clean namespace isolation
for mod in list(sys.modules.keys()):
    if mod == "src" or mod.startswith("src."):
        del sys.modules[mod]

ai_worker_path = Path(__file__).resolve().parents[1] / "apps" / "ai-worker"
if str(ai_worker_path) in sys.path:
    sys.path.remove(str(ai_worker_path))
sys.path.insert(0, str(ai_worker_path))

from src.main import app
from src.runbook_store import RunbookVectorStore, SYSTEM_RUNBOOKS
from aiops_contracts import Incident, Evidence
from aiops_contracts.evidence import EvidenceKind


@pytest.fixture
def client():
    return TestClient(app)


def test_ai_worker_root_and_health(client):
    """Verify AI Worker boots and exposes health probes."""
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.json()["service"] == "ai-worker"
    assert "langchain_core_version" in res_root.json()

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"
    assert res_health.json()["langchain_available"] is True


def test_list_runbooks(client):
    """Verify pre-indexed engineering runbooks endpoint."""
    res = client.get("/api/v1/runbooks")
    assert res.status_code == 200
    runbooks = res.json()
    assert isinstance(runbooks, list)
    assert len(runbooks) >= 5
    ids = [r["id"] for r in runbooks]
    assert "RB-001" in ids  # DB Pool
    assert "RB-002" in ids  # OOM Kill


def test_runbook_vector_retrieval():
    """Unit test: Verify vector retrieval matches error symptoms accurately."""
    store = RunbookVectorStore()
    
    # Query 1: Database timeout symptom
    results_db = store.retrieve("OperationalError: QueuePool limit of size 10 exceeded", top_k=1)
    assert len(results_db) == 1
    assert results_db[0]["runbook"].id == "RB-001"
    assert results_db[0]["score"] > 0.0

    # Query 2: OOM Killed symptom
    results_oom = store.retrieve("Container failed with exit_code: 137 OOMKilled", top_k=1)
    assert len(results_oom) == 1
    assert results_oom[0]["runbook"].id == "RB-002"
    assert results_oom[0]["score"] > 0.0


def test_diagnose_database_incident(client):
    """Integration test: Diagnose database connection exhaustion incident."""
    incident = Incident(
        title="High Severity Outage: Database Pool Exhaustion - QueuePool timeout errors under peak traffic",
        severity="critical",
        status="open",
        service_id="payment-service",  # Note: service name, not domain concept
        environment_id="production",
    )

    evidence = Evidence(
        incident_id=incident.id,
        kind=EvidenceKind.STACK_TRACE,
        source="fastapi-logger",
        content="TimeoutError: QueuePool limit of size 10 exceeded while acquiring connection",
    )

    payload = {
        "incident": incident.model_dump(mode="json"),
        "evidence": [evidence.model_dump(mode="json")],
    }

    res = client.post("/api/v1/diagnose", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["status"] == "diagnosed"
    assert data["incident_id"] == incident.id
    
    # Check Diagnosis Contract Model properties
    diag = data["diagnosis"]
    assert diag["incident_id"] == incident.id
    assert "Database connection pool exhausted" in diag["probable_root_cause"]
    assert 0.0 <= diag["confidence"] <= 1.0
    assert evidence.id in diag["supporting_evidence_ids"]

    # Check RemediationPlan Contract Model properties
    plan = data["remediation_plan"]
    assert plan["incident_id"] == incident.id
    assert plan["status"] == "drafted"  # Non-executable draft until human approval!
    assert len(plan["actions"]) >= 1
    action = plan["actions"][0]
    assert action["action_type"] == "config_update"
    assert action["plan_id"] == plan["id"]


def test_diagnose_oom_incident(client):
    """Integration test: Diagnose Out-Of-Memory crash."""
    incident = Incident(
        title="Worker Container Crashing Continuously - Background tasks stopped due to unexpected termination",
        severity="high",
        status="open",
        service_id="worker",
        environment_id="production",
    )

    evidence = Evidence(
        incident_id=incident.id,
        kind=EvidenceKind.LOG,
        source="docker-daemon",
        content="Container terminated with exit_code: 137 OOMKilled memory limit exceeded",
    )

    payload = {
        "incident": incident.model_dump(mode="json"),
        "evidence": [evidence.model_dump(mode="json")],
    }

    res = client.post("/api/v1/diagnose", json=payload)
    assert res.status_code == 200
    data = res.json()

    diag = data["diagnosis"]
    assert "memory" in diag["probable_root_cause"].lower()
    
    plan = data["remediation_plan"]
    assert plan["status"] == "drafted"
    action = plan["actions"][0]
    assert action["action_type"] == "container_restart"
    assert action["plan_id"] == plan["id"]


def test_domain_agnostic_rejection(client):
    """Enforces that any attempt to pass e-commerce/unauthorized fields like order_id is rejected."""
    forbidden_payload = {
        "incident": {
            "title": "Leak attempt",
            "summary": "Should be rejected",
            "order_id": "ord-12345",  # Banned domain attribute!
        },
        "evidence": [],
    }

    res = client.post("/api/v1/diagnose", json=forbidden_payload)
    assert res.status_code == 422
    assert "Extra inputs are not permitted" in str(res.json())
