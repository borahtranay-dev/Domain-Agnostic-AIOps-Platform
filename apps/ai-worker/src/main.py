"""FastAPI Application Entrypoint for AI / RAG Subsystem.

Owner: Rudra (AI / RAG Lead)
Phase: P3 (Component Construction - AI Diagnosis & RAG)
"""
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import langchain_core
from aiops_contracts import Incident, Evidence, Diagnosis, RemediationPlan
from src.config import settings
from src.runbook_store import runbook_store
from src.diagnosis_service import diagnosis_engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Domain-Agnostic AIOps AI Diagnosis and LangChain RAG Subsystem",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiagnoseRequest(BaseModel):
    """Payload to trigger AI root cause diagnosis."""
    incident: Incident = Field(..., description="The open incident to diagnose")
    evidence: List[Evidence] = Field(default_factory=list, description="List of factual runtime evidence records")


class DiagnoseResponse(BaseModel):
    """Diagnosed incident result with generated P2 contract models."""
    status: str = "diagnosed"
    incident_id: str
    diagnosis: Diagnosis
    remediation_plan: RemediationPlan
    retrieved_runbooks: List[str]


@app.get("/")
def root():
    """Service metadata endpoint."""
    return {
        "service": "ai-worker",
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "langchain_core_version": langchain_core.__version__,
        "phase": "P3 Component Construction - AI Diagnosis & RAG",
        "indexed_runbooks": len(runbook_store.runbooks),
    }


@app.get("/health")
def health_check():
    """Health check endpoint confirming service and AI library availability."""
    return {
        "status": "ok",
        "service": "ai-worker",
        "version": settings.VERSION,
        "langchain_available": True,
        "indexed_runbooks": len(runbook_store.runbooks),
    }


@app.get("/api/v1/runbooks", summary="List operational engineering runbooks")
def list_runbooks():
    """Returns all pre-indexed failure playbooks available for RAG vector search."""
    return [
        {
            "id": rb.id,
            "title": rb.title,
            "root_cause": rb.root_cause_explanation,
            "recommended_action": rb.recommended_action,
            "action_type": rb.recommended_action_type,
        }
        for rb in runbook_store.runbooks
    ]


@app.post(
    "/api/v1/diagnose",
    response_model=DiagnoseResponse,
    status_code=status.HTTP_200_OK,
    summary="Diagnose an incident using RAG and LangChain",
    description="Analyzes incident telemetry, retrieves grounded operational runbooks, and returns P2 Diagnosis and RemediationPlan contracts.",
)
def diagnose_incident(request: DiagnoseRequest):
    """Autonomous AI Diagnosis endpoint."""
    try:
        result = diagnosis_engine.diagnose_incident(
            incident=request.incident,
            evidence_list=request.evidence,
        )
        return DiagnoseResponse(
            incident_id=request.incident.id,
            diagnosis=result["diagnosis"],
            remediation_plan=result["remediation_plan"],
            retrieved_runbooks=result["retrieved_runbooks"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnosis pipeline error: {str(e)}",
        )
