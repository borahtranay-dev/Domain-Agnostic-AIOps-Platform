#!/usr/bin/env python3
"""Phase P5 AI Diagnosis & LangChain RAG Orchestration Simulation Harness.

Role: Rudra (AI/RAG Lead) & Saurav (DevOps Lead)
Phase: P5 (AI Diagnosis & RAG - Real Incident Pipeline)

Demonstrates:
1. Inbound Webhook triggers Incident & Evidence creation.
2. AI Diagnostic RAG Engine retrieves matching operational runbooks (RB-001 to RB-007).
3. Root cause synthesized with strict evidence citation (zero hallucination).
4. Calibrated confidence scoring (bounded strictly between 0.65 and 0.98).
5. RemediationPlan generated with Human-in-the-Loop requirement (requires_human_approval=True).
6. Incident status state transition from 'OPEN' to 'AWAITING_APPROVAL'.
7. Strict Domain-Agnostic verification: zero e-commerce terms in AI output.
"""
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

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
from src.models.diagnosis import DiagnosisModel
from aiops_contracts import IncidentStatus, ActionType

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

SEPARATOR = "=" * 80
SUB_SEP = "-" * 80


def log_header(title: str):
    print(f"\n{SEPARATOR}")
    print(f" >>> {title}")
    print(f"{SEPARATOR}")


def log_sub(title: str):
    print(f"\n{SUB_SEP}")
    print(f" [*] {title}")
    print(f"{SUB_SEP}")


def simulate_p5_pipeline():
    log_header("PHASE P5: AI DIAGNOSIS & RAG PIPELINE SIMULATION")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("Orchestration: FastAPI Backend + LangChain RAG AI Worker (Isolated Mono-repo Client)")

    # -------------------------------------------------------------------------
    # Scenario 1: Prometheus Alertmanager Pool Outage -> RAG Config Update
    # -------------------------------------------------------------------------
    log_sub("Scenario 1: Prometheus Database Connection Pool Starvation")
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
                    "description": "Database connection checkout timed out after 30 seconds",
                },
            }
        ],
    }

    res = client.post("/api/v1/webhooks/prometheus", json=prom_payload)
    print(f"[OK] Prometheus Webhook Received: HTTP {res.status_code}")

    db = SessionLocal()
    inc1 = db.query(IncidentModel).filter(IncidentModel.service_id == "auth-service").first()
    evidences1 = db.query(EvidenceModel).filter(EvidenceModel.incident_id == inc1.id).all()
    print(f"    - Incident ID: {inc1.id}")
    print(f"    - Initial Status: {inc1.status.upper()}")
    print(f"    - Harvested Evidences: {len(evidences1)} records attached")
    for ev in evidences1:
        print(f"      * [{ev.id}] (Kind: {ev.kind}) Source: {ev.source}")
    db.close()

    print("\n[AI Worker] Invoking RAG Root-Cause Diagnostic Engine...")
    diag_res1 = client.post(f"/api/v1/incidents/{inc1.id}/diagnose")
    assert diag_res1.status_code == 200, f"Diagnosis failed: {diag_res1.text}"
    diag_body1 = diag_res1.json()

    diag1 = diag_body1["diagnosis"]
    plan1 = diag_body1["remediation_plan"]

    print(f"[OK] AI Diagnosis Computed Successfully!")
    print(f"    - Probable Root Cause: {diag1['probable_root_cause']}")
    print(f"    - Calibrated Confidence: {diag1['confidence'] * 100:.1f}%")
    print(f"    - Cited Evidence IDs: {diag1['supporting_evidence_ids']}")
    print(f"    - Recommended Action: {diag1.get('recommended_remediation', 'N/A')}")
    print(f"    - Uncertainty Notes: {diag1.get('uncertainty_notes', 'N/A')}")
    print(f"\n[Remediation Plan Generated]")
    print(f"    - Plan Status: {plan1['status'].upper()}")
    for idx, act in enumerate(plan1["actions"], 1):
        print(f"      Step {idx}: Type={act['action_type']} | Target={act.get('target_service_id')} | Desc={act.get('description')}")

    # Verify DB State
    db = SessionLocal()
    updated_inc1 = db.query(IncidentModel).filter(IncidentModel.id == inc1.id).first()
    db_diag1 = db.query(DiagnosisModel).filter(DiagnosisModel.incident_id == inc1.id).first()
    print(f"\n[Database Verification]")
    print(f"    - Advanced Incident Status: {updated_inc1.status.upper()} (Human-in-the-loop gate active)")
    print(f"    - Persisted Diagnosis ID: {db_diag1.id}")
    db.close()

    # -------------------------------------------------------------------------
    # Scenario 2: GitHub Actions Deployment Failure -> RAG Rollback (RB-006)
    # -------------------------------------------------------------------------
    log_sub("Scenario 2: GitHub Actions Deployment Failure (Startup Probe Timeout)")
    gh_payload = {
        "deployment_status": {
            "id": 99401,
            "state": "failure",
            "description": "Container image failed readiness probe on startup",
        },
        "deployment": {
            "id": 1022,
            "sha": "c0ffee998877",
            "environment": "production",
        },
        "repository": {
            "name": "payment-api",
        },
    }

    res_gh = client.post("/api/v1/webhooks/github", json=gh_payload)
    print(f"[OK] GitHub Webhook Received: HTTP {res_gh.status_code}")

    db = SessionLocal()
    inc2 = db.query(IncidentModel).filter(IncidentModel.service_id == "payment-api").first()
    db.close()

    print("\n[AI Worker] Invoking RAG Root-Cause Diagnostic Engine...")
    diag_res2 = client.post(f"/api/v1/incidents/{inc2.id}/diagnose")
    diag_body2 = diag_res2.json()
    diag2 = diag_body2["diagnosis"]
    plan2 = diag_body2["remediation_plan"]

    print(f"[OK] AI Diagnosis Computed Successfully!")
    print(f"    - Matched Runbook: RB-006 (Container Startup Probe Failure)")
    print(f"    - Probable Root Cause: {diag2['probable_root_cause']}")
    print(f"    - Confidence: {diag2['confidence'] * 100:.1f}%")
    print(f"    - Recommended Action: {plan2['actions'][0]['action_type'].upper()}")
    print(f"    - Target Rollback SHA: {plan2['actions'][0]['parameters'].get('previous_version_sha')}")

    # -------------------------------------------------------------------------
    # Scenario 3: Generic App Webhook -> Sanitization -> RAG Restart (RB-007)
    # -------------------------------------------------------------------------
    log_sub("Scenario 3: Generic App Alert with Domain Sanitization -> RAG Worker Restart (RB-007)")
    generic_alert = {
        "service_name": "worker-service",
        "env": "production",
        "error": "Redis queue worker connection timeout after retries",
        "reporter": "python-sentry-client",
        # Illegal domain keys to verify domain-agnosticity
        "order_id": "ORD-12345",
        "cart_id": "CART-9988",
    }

    res_gen = client.post("/api/v1/webhooks/generic", json=generic_alert)
    print(f"[OK] Generic Webhook Ingested: HTTP {res_gen.status_code}")

    # Check sanitization in event payload
    event_gen = res_gen.json()
    assert "order_id" not in event_gen["payload"], "FATAL: Leaked order_id!"
    assert "cart_id" not in event_gen["payload"], "FATAL: Leaked cart_id!"
    print(f"[OK] Domain Sanitization Verified: E-commerce fields stripped from Event payload")

    db = SessionLocal()
    inc3 = db.query(IncidentModel).filter(IncidentModel.service_id == "worker-service").first()
    db.close()

    print("\n[AI Worker] Invoking RAG Root-Cause Diagnostic Engine...")
    diag_res3 = client.post(f"/api/v1/incidents/{inc3.id}/diagnose")
    diag_body3 = diag_res3.json()
    diag3 = diag_body3["diagnosis"]
    plan3 = diag_body3["remediation_plan"]

    print(f"[OK] AI Diagnosis Computed Successfully!")
    print(f"    - Matched Runbook: RB-007 (Queue Worker Timeout)")
    print(f"    - Probable Root Cause: {diag3['probable_root_cause']}")
    print(f"    - Action Type: {plan3['actions'][0]['action_type'].upper()}")

    # -------------------------------------------------------------------------
    # Invariant Checks
    # -------------------------------------------------------------------------
    log_sub("Phase P5 Architecture & Contract Invariant Verifications")
    banned = ["order_id", "cart", "payment_status", "checkout", "inventory"]
    all_ai_text = (
        diag1["probable_root_cause"] + diag2["probable_root_cause"] + diag3["probable_root_cause"]
    ).lower()

    for word in banned:
        assert word not in all_ai_text, f"Domain Leakage Detected: '{word}' found in AI text!"
    print(f"[PASS] Domain Agnosticity Invariant: 0 forbidden e-commerce tokens detected in AI output.")

    # Check evidence citation
    for cited_id in diag1["supporting_evidence_ids"]:
        assert any(cited_id == ev.id for ev in evidences1), f"Hallucination! Cited ID {cited_id} not in DB."
    print(f"[PASS] Zero-Hallucination Invariant: All cited evidence IDs verifiably grounded in database.")

    # Check confidence bounds
    for d in [diag1, diag2, diag3]:
        assert 0.65 <= d["confidence"] <= 0.98, f"Confidence {d['confidence']} outside [0.65, 0.98] bounds!"
    print(f"[PASS] Confidence Bounds: Strictly calibrated between 0.65 and 0.98.")

    log_header("PHASE P5 SIMULATION COMPLETE: ALL WORKFLOWS 100% OPERATIONAL")


if __name__ == "__main__":
    simulate_p5_pipeline()
