#!/usr/bin/env python3
"""Phase P4 Inbound Webhook Adapters & Correlation Engine Simulation Harness.

Role: Saurav (DevOps Lead) / Taranay (Backend Lead)
Phase: P4 (Event & Incident Pipeline & Webhook Adapters)

Demonstrates:
1. Ingestion of Prometheus Alertmanager alerts -> Normalized Event -> Incident creation.
2. Ingestion of GitHub Actions deployment failure webhooks.
3. Ingestion of Generic Application webhooks with domain leakage sanitization.
4. Real-time temporal event correlation: grouping multiple alerts into a unified incident.
5. Automatic telemetry evidence extraction and linking.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure project contracts and apps are available
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "packages" / "contracts"))
sys.path.insert(0, str(REPO_ROOT / "apps" / "api"))

# Clean src module cache
for mod in list(sys.modules.keys()):
    if mod == "src" or mod.startswith("src."):
        del sys.modules[mod]

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src.models.incident import IncidentModel
from src.models.evidence import EvidenceModel
from aiops_contracts import EventType

# Setup in-memory test database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
Base.metadata.create_all(bind=test_engine)


def override_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)

# Configure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Terminal Styling
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_banner():
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}  Phase P4: Webhook Adapters & Incident Correlation Simulation Harness{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")


def simulate_p4():
    print_banner()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1: Prometheus Alertmanager Ingestion
    # ─────────────────────────────────────────────────────────────────────────
    print(f"{BOLD}{YELLOW}[STEP 1] Ingesting Prometheus Alertmanager Webhook...{RESET}")
    prom_payload = {
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
                },
                "annotations": {
                    "summary": "QueuePool limit of size 10 overflow 20 reached",
                    "description": "Database connection pool saturated under peak traffic",
                },
                "startsAt": datetime.now(timezone.utc).isoformat(),
            }
        ],
    }

    res = client.post("/api/v1/webhooks/prometheus", json=prom_payload)
    assert res.status_code == 201, f"Prometheus webhook failed: {res.text}"
    prom_events = res.json()
    print(f"  {GREEN}[OK] Ingested {len(prom_events)} event(s) from Prometheus{RESET}")
    print(f"    - Event ID: {DIM}{prom_events[0]['id']}{RESET}")
    print(f"    - Type: {prom_events[0]['type']} | Source: {prom_events[0]['source']}")
    print(f"    - Summary: {prom_events[0]['summary']}")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 2: Verify Correlated Incident & Evidence
    # ─────────────────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{YELLOW}[STEP 2] Verifying Correlated Incident & Evidence Records...{RESET}")
    db = SessionLocal()
    incidents = db.query(IncidentModel).filter(IncidentModel.service_id == "auth-service").all()
    assert len(incidents) == 1
    inc1 = incidents[0]
    print(f"  {GREEN}[OK] Incident auto-opened in Cockpit:{RESET}")
    print(f"    - Incident ID: {BOLD}{inc1.id}{RESET}")
    print(f"    - Title: {inc1.title}")
    print(f"    - Severity: {RED if inc1.severity == 'critical' else YELLOW}{inc1.severity.upper()}{RESET}")
    print(f"    - Status: {inc1.status}")

    evidences = db.query(EvidenceModel).filter(EvidenceModel.incident_id == inc1.id).all()
    assert len(evidences) == 1
    print(f"  {GREEN}[OK] Extracted Telemetry Evidence:{RESET}")
    print(f"    - Evidence ID: {evidences[0].id}")
    print(f"    - Kind: {evidences[0].kind} | Source: {evidences[0].source}")
    db.close()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 3: Multi-Event Temporal Correlation (Deduplication & Severity Upgrade)
    # ─────────────────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{YELLOW}[STEP 3] Testing Temporal Correlation (Second Alert for Same Service)...{RESET}")
    second_alert = {
        "service": "auth-service",
        "env": "production",
        "error": "Fatal: remaining connection slots are reserved for superuser",
        "severity": "critical",
        "source": "database-logger",
    }
    res_generic = client.post("/api/v1/webhooks/generic", json=second_alert)
    assert res_generic.status_code == 201
    second_event_id = res_generic.json()["id"]

    db = SessionLocal()
    incidents = db.query(IncidentModel).filter(IncidentModel.service_id == "auth-service").all()
    assert len(incidents) == 1, "Duplicate incident created instead of correlating!"
    updated_inc = incidents[0]
    assert second_event_id in updated_inc.event_ids
    print(f"  {GREEN}[OK] Successfully correlated into existing Incident {updated_inc.id}!{RESET}")
    print(f"    - Total Correlated Events: {len(updated_inc.event_ids)}")
    print(f"    - Event IDs: {updated_inc.event_ids}")

    ev_count = db.query(EvidenceModel).filter(EvidenceModel.incident_id == updated_inc.id).count()
    assert ev_count == 2
    print(f"    - Attached Evidence Artifacts: {ev_count}")
    db.close()

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 4: GitHub Deployment Webhook Ingestion
    # ─────────────────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{YELLOW}[STEP 4] Ingesting GitHub Actions Deployment Webhook...{RESET}")
    gh_payload = {
        "deployment_status": {
            "id": 99401,
            "state": "failure",
            "description": "Health probe failed for payment-service container",
        },
        "deployment": {
            "id": 1022,
            "sha": "c0ffee123456",
            "environment": "staging",
        },
        "repository": {
            "name": "payment-service",
        },
    }
    res_gh = client.post(
        "/api/v1/webhooks/github",
        json=gh_payload,
        headers={"X-GitHub-Event": "deployment_status"},
    )
    assert res_gh.status_code == 201
    gh_event = res_gh.json()
    print(f"  {GREEN}[OK] Ingested GitHub Deployment Event:{RESET}")
    print(f"    - Service: {gh_event['service_id']} | Env: {gh_event['environment_id']}")
    print(f"    - Commit SHA: {gh_event['payload']['commit']}")

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 5: Domain-Agnostic Leakage Sanitization Verification
    # ─────────────────────────────────────────────────────────────────────────
    print(f"\n{BOLD}{YELLOW}[STEP 5] Domain-Agnostic Sanitization Verification...{RESET}")
    dirty_payload = {
        "service": "notification-worker",
        "env": "production",
        "error": "Kafka consumer rebalance timeout",
        "cpu_usage": 94.2,
        # Illegal leaked domain terms that adapter MUST strip
        "order_id": "ORD-ILLEGAL-999",
        "cart_id": "CART-ILLEGAL-123",
        "payment_status": "FAILED",
    }
    res_dirty = client.post("/api/v1/webhooks/generic", json=dirty_payload)
    assert res_dirty.status_code == 201
    cleaned_event = res_dirty.json()
    clean_payload = cleaned_event["payload"]

    assert "order_id" not in clean_payload, "Leak: order_id was not sanitized!"
    assert "cart_id" not in clean_payload, "Leak: cart_id was not sanitized!"
    assert "payment_status" not in clean_payload, "Leak: payment_status was not sanitized!"
    assert clean_payload["cpu_usage"] == 94.2

    print(f"  {GREEN}[OK] Invariant Passed: All forbidden domain terms stripped cleanly!{RESET}")
    print(f"    - Allowed Operational Keys retained: {list(clean_payload.keys())}")

    print(f"\n{BOLD}{GREEN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}  Phase P4 Webhook Adapters & Correlation Engine: 100% OPERATIONAL!{RESET}")
    print(f"{BOLD}{GREEN}{'='*80}{RESET}\n")


if __name__ == "__main__":
    simulate_p4()
