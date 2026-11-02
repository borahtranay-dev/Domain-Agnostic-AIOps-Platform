"""Incident Management and Query Router for AIOps API.

Owner: Taranay (Backend Lead)
Phase: P3 (Component Construction)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from aiops_contracts import Incident, IncidentStatus, Severity
from src.database import get_db
from src.models.incident import IncidentModel

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post(
    "",
    response_model=Incident,
    status_code=status.HTTP_201_CREATED,
    summary="Create or correlate an incident",
    description="Registers an incident correlated from failure events, validated against P2 Incident contract.",
)
def create_incident(incident_in: Incident, db: Session = Depends(get_db)):
    db_incident = IncidentModel(
        id=incident_in.id,
        title=incident_in.title,
        status=incident_in.status.value if isinstance(incident_in.status, IncidentStatus) else str(incident_in.status),
        severity=incident_in.severity.value if isinstance(incident_in.severity, Severity) else str(incident_in.severity),
        pipeline_id=incident_in.pipeline_id,
        service_id=incident_in.service_id,
        environment_id=incident_in.environment_id,
        event_ids=incident_in.event_ids,
        opened_at=incident_in.opened_at,
        resolved_at=incident_in.resolved_at,
    )

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return incident_in


@router.get(
    "",
    response_model=List[Incident],
    summary="List incidents",
    description="Returns a paginated list of incidents with optional status and severity filters.",
)
def list_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status_filter: Optional[IncidentStatus] = Query(None, alias="status", description="Filter by status"),
    severity_filter: Optional[Severity] = Query(None, alias="severity", description="Filter by severity"),
    db: Session = Depends(get_db),
):
    query = db.query(IncidentModel)
    if status_filter:
        query = query.filter(IncidentModel.status == status_filter.value)
    if severity_filter:
        query = query.filter(IncidentModel.severity == severity_filter.value)

    db_incidents = query.order_by(IncidentModel.opened_at.desc()).offset(skip).limit(limit).all()

    return [
        Incident(
            id=inc.id,
            title=inc.title,
            status=IncidentStatus(inc.status),
            severity=Severity(inc.severity),
            pipeline_id=inc.pipeline_id,
            service_id=inc.service_id,
            environment_id=inc.environment_id,
            event_ids=inc.event_ids or [],
            opened_at=inc.opened_at,
            resolved_at=inc.resolved_at,
        )
        for inc in db_incidents
    ]


@router.get(
    "/{incident_id}",
    response_model=Incident,
    summary="Get single incident by ID",
    description="Retrieves a specific incident record by its unique ID.",
)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    db_incident = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    return Incident(
        id=db_incident.id,
        title=db_incident.title,
        status=IncidentStatus(db_incident.status),
        severity=Severity(db_incident.severity),
        pipeline_id=db_incident.pipeline_id,
        service_id=db_incident.service_id,
        environment_id=db_incident.environment_id,
        event_ids=db_incident.event_ids or [],
        opened_at=db_incident.opened_at,
        resolved_at=db_incident.resolved_at,
    )


@router.patch(
    "/{incident_id}/status",
    response_model=Incident,
    summary="Update incident status",
    description="Updates the lifecycle state of an incident (e.g., awaiting_approval, resolved). Sets resolved_at automatically when resolved.",
)
def update_incident_status(
    incident_id: str,
    new_status: IncidentStatus = Query(..., alias="status", description="New lifecycle status"),
    db: Session = Depends(get_db),
):
    from aiops_contracts.common import utc_now

    db_incident = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not db_incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    db_incident.status = new_status.value
    if new_status == IncidentStatus.RESOLVED and db_incident.resolved_at is None:
        db_incident.resolved_at = utc_now()

    db.commit()
    db.refresh(db_incident)

    return Incident(
        id=db_incident.id,
        title=db_incident.title,
        status=IncidentStatus(db_incident.status),
        severity=Severity(db_incident.severity),
        pipeline_id=db_incident.pipeline_id,
        service_id=db_incident.service_id,
        environment_id=db_incident.environment_id,
        event_ids=db_incident.event_ids or [],
        opened_at=db_incident.opened_at,
        resolved_at=db_incident.resolved_at,
    )


@router.post(
    "/{incident_id}/diagnose",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Trigger RAG root-cause diagnosis on an incident",
    description="Harvests all attached evidence for the incident, invokes the RAG AI diagnosis engine, persists DiagnosisModel, and advances status to awaiting_approval.",
)
def trigger_incident_diagnosis(
    incident_id: str,
    db: Session = Depends(get_db),
):
    """Harvests attached evidence, invokes AI RAG diagnosis, and persists DiagnosisModel."""
    from datetime import datetime, timezone
    from src.models.evidence import EvidenceModel
    from src.models.diagnosis import DiagnosisModel
    from aiops_contracts import Evidence, EvidenceKind

    db_incident = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not db_incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found",
        )

    db_evidences = db.query(EvidenceModel).filter(EvidenceModel.incident_id == incident_id).all()
    evidence_objs = [
        Evidence(
            id=ev.id,
            incident_id=ev.incident_id,
            kind=EvidenceKind(ev.kind) if hasattr(EvidenceKind, ev.kind.upper()) else EvidenceKind.LOG,
            source=ev.source,
            content=ev.content,
            collected_at=ev.captured_at,
        )
        for ev in db_evidences
    ]

    incident_obj = Incident(
        id=db_incident.id,
        title=db_incident.title,
        status=IncidentStatus(db_incident.status),
        severity=Severity(db_incident.severity),
        pipeline_id=db_incident.pipeline_id,
        service_id=db_incident.service_id,
        environment_id=db_incident.environment_id,
        event_ids=db_incident.event_ids or [],
        opened_at=db_incident.opened_at,
        resolved_at=db_incident.resolved_at,
    )

    from src.services.ai_client import diagnose_incident_via_ai
    diag_result = diagnose_incident_via_ai(incident_obj, evidence_objs)
    diag_data = diag_result["diagnosis"]

    existing_diag = db.query(DiagnosisModel).filter(DiagnosisModel.incident_id == incident_id).first()
    if existing_diag:
        existing_diag.probable_root_cause = diag_data["probable_root_cause"]
        existing_diag.supporting_evidence_ids = diag_data.get("supporting_evidence_ids", [])
        existing_diag.confidence = diag_data.get("confidence", 0.0)
        existing_diag.uncertainty_notes = diag_data.get("uncertainty_notes")
        existing_diag.recommended_remediation = diag_data.get("recommended_remediation")
    else:
        new_diag = DiagnosisModel(
            id=diag_data["id"],
            incident_id=incident_id,
            probable_root_cause=diag_data["probable_root_cause"],
            supporting_evidence_ids=diag_data.get("supporting_evidence_ids", []),
            contradicting_evidence_ids=diag_data.get("contradicting_evidence_ids", []),
            confidence=diag_data.get("confidence", 0.0),
            uncertainty_notes=diag_data.get("uncertainty_notes"),
            recommended_remediation=diag_data.get("recommended_remediation"),
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_diag)

    # Advance incident lifecycle to awaiting_approval
    db_incident.status = IncidentStatus.AWAITING_APPROVAL.value
    db.commit()
    db.refresh(db_incident)

    return diag_result


@router.get(
    "/{incident_id}/diagnosis",
    response_model=dict,
    summary="Get incident diagnosis",
    description="Retrieves the persisted AI diagnosis record for the specified incident.",
)
def get_incident_diagnosis(
    incident_id: str,
    db: Session = Depends(get_db),
):
    """Retrieves persisted DiagnosisModel record for an incident."""
    from src.models.diagnosis import DiagnosisModel
    db_diag = db.query(DiagnosisModel).filter(DiagnosisModel.incident_id == incident_id).first()
    if not db_diag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No diagnosis found for incident '{incident_id}'",
        )
    return {
        "id": db_diag.id,
        "incident_id": db_diag.incident_id,
        "probable_root_cause": db_diag.probable_root_cause,
        "supporting_evidence_ids": db_diag.supporting_evidence_ids,
        "contradicting_evidence_ids": db_diag.contradicting_evidence_ids,
        "confidence": db_diag.confidence,
        "uncertainty_notes": db_diag.uncertainty_notes,
        "recommended_remediation": db_diag.recommended_remediation,
        "created_at": db_diag.created_at.isoformat() if db_diag.created_at else None,
    }
