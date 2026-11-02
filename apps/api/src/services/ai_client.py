"""AI Worker Client for RAG Diagnosis Integration.

Owner: Saurav (DevOps) / Taranay (Backend)
Phase: P5 (AI Diagnosis & RAG - Real Incident Pipeline)

Connects apps/api to the AI diagnostic worker. In containerized environments,
issues an HTTP POST to ai-worker:8001. In local/test environments where the container
is not active, falls back to direct execution of the DiagnosisEngine using
isolated module loading to avoid namespace collisions.
"""
import logging
from typing import Dict, Any, List
from pathlib import Path
import httpx
import importlib.util
import sys

from aiops_contracts import Incident, Evidence
from src.config import settings

logger = logging.getLogger(__name__)


def diagnose_incident_via_ai(incident: Incident, evidence_list: List[Evidence]) -> Dict[str, Any]:
    """Diagnoses an incident using the AI Worker RAG pipeline."""
    # 1. Attempt HTTP invocation to AI worker microservice
    try:
        url = f"{settings.AI_WORKER_URL}/api/v1/diagnose"
        payload = {
            "incident": incident.model_dump(mode="json"),
            "evidence": [ev.model_dump(mode="json") for ev in evidence_list],
        }
        with httpx.Client(timeout=httpx.Timeout(3.0, connect=0.25)) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                logger.info(f"Successfully diagnosed incident {incident.id} via HTTP ai-worker")
                return resp.json()
    except Exception as e:
        logger.debug(f"HTTP connection to ai-worker failed ({e}); utilizing local RAG diagnostic engine fallback.")

    # 2. Local fallback using isolated module execution (prevents mono-repo 'src' namespace collision)
    ai_worker_root = Path(__file__).resolve().parents[3] / "ai-worker" / "src"
    rb_path = ai_worker_root / "runbook_store.py"
    diag_path = ai_worker_root / "diagnosis_service.py"

    if "src.runbook_store" not in sys.modules:
        spec_rb = importlib.util.spec_from_file_location("src.runbook_store", rb_path)
        mod_rb = importlib.util.module_from_spec(spec_rb)
        sys.modules["src.runbook_store"] = mod_rb
        spec_rb.loader.exec_module(mod_rb)

    if "src.diagnosis_service" not in sys.modules:
        spec_diag = importlib.util.spec_from_file_location("src.diagnosis_service", diag_path)
        mod_diag = importlib.util.module_from_spec(spec_diag)
        sys.modules["src.diagnosis_service"] = mod_diag
        spec_diag.loader.exec_module(mod_diag)

    engine = sys.modules["src.diagnosis_service"].diagnosis_engine
    result = engine.diagnose_incident(incident, evidence_list)

    return {
        "status": "diagnosed",
        "incident_id": incident.id,
        "diagnosis": result["diagnosis"].model_dump(mode="json"),
        "remediation_plan": result["remediation_plan"].model_dump(mode="json"),
        "retrieved_runbooks": result["retrieved_runbooks"],
    }
