"""Incident Remediation and Human-in-the-Loop Approval Router.

Owner: Taranay (Backend Lead) / Saurav (DevOps Lead)
Phase: P6 (Remediation & GitHub Automation)
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from aiops_contracts import IncidentStatus, PlanStatus, VerificationStatus, Severity
from src.database import get_db
from src.models.incident import IncidentModel
from src.models.remediation import RemediationPlanModel, RemediationActionModel
from src.models.approval import ApprovalModel
from src.models.verification import VerificationModel

router = APIRouter(prefix="/incidents", tags=["Remediation & Governance"])


class ApprovalRequest(BaseModel):
    approver_id: str = Field(..., description="SRE or Admin user ID authorizing the action")
    notes: Optional[str] = Field("Approved via Developer Cockpit", description="Audit trail notes for approval")


class RejectionRequest(BaseModel):
    approver_id: str = Field(..., description="SRE or Admin user ID rejecting the plan")
    notes: str = Field(..., description="Mandatory rationale for rejecting the remediation plan")


@router.get(
    "/{incident_id}/remediation",
    response_model=Dict[str, Any],
    summary="Get proposed remediation plan for incident",
    description="Retrieves drafted or approved remediation plan and child actions for the given incident.",
)
def get_incident_remediation(incident_id: str, db: Session = Depends(get_db)):
    plan = db.query(RemediationPlanModel).filter(RemediationPlanModel.incident_id == incident_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No remediation plan found for incident '{incident_id}'",
        )

    actions = db.query(RemediationActionModel).filter(RemediationActionModel.plan_id == plan.id).order_by(RemediationActionModel.order).all()

    return {
        "id": plan.id,
        "incident_id": plan.incident_id,
        "diagnosis_id": plan.diagnosis_id,
        "status": plan.status,
        "rationale": plan.rationale,
        "risk_level": plan.risk_level,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "executed_at": plan.executed_at.isoformat() if plan.executed_at else None,
        "actions": [
            {
                "id": a.id,
                "plan_id": a.plan_id,
                "action_type": a.action_type,
                "description": a.description,
                "target_service_id": a.target_service_id,
                "parameters": a.parameters,
                "order": a.order,
            }
            for a in actions
        ],
    }


@router.post(
    "/{incident_id}/remediation/approve",
    response_model=Dict[str, Any],
    summary="Human-in-the-Loop approve and execute remediation",
    description="Enforces Rule 15: Authorized engineer approves drafted remediation plan, triggering execution & verification.",
)
def approve_and_execute_remediation(
    incident_id: str,
    payload: ApprovalRequest,
    db: Session = Depends(get_db),
):
    incident = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    plan = db.query(RemediationPlanModel).filter(RemediationPlanModel.incident_id == incident_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No remediation plan exists to approve for incident '{incident_id}'",
        )

    if plan.status == PlanStatus.APPROVED.value and incident.status == IncidentStatus.RESOLVED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Remediation plan has already been approved and executed.",
        )

    actions = db.query(RemediationActionModel).filter(RemediationActionModel.plan_id == plan.id).order_by(RemediationActionModel.order).all()

    now = datetime.now(timezone.utc)

    # 1. Record Human Approval in Database
    approval = ApprovalModel(
        id=f"appr-{now.strftime('%Y%m%d%H%M%S')}-{incident_id[:6]}",
        incident_id=incident_id,
        plan_id=plan.id,
        decision="approved",
        approver_id=payload.approver_id,
        decided_at=now,
        notes=payload.notes or "",
    )
    db.add(approval)

    # 2. Transition Plan Status to APPROVED
    plan.status = PlanStatus.APPROVED.value

    # 3. Transition Incident Status to EXECUTING
    incident.status = IncidentStatus.EXECUTING.value
    db.commit()

    # 4. Execute Remediation through Execution Adapter (Rule 15: Executed ONLY after approval)
    from aiops_contracts import Incident as IncidentContract, RemediationPlan as PlanContract, RemediationAction as ActionContract, ActionType

    contract_incident = IncidentContract(
        id=incident.id,
        title=incident.title,
        status=IncidentStatus(incident.status),
        severity=Severity(incident.severity),
        pipeline_id=incident.pipeline_id,
        service_id=incident.service_id,
        environment_id=incident.environment_id,
        event_ids=incident.event_ids or [],
        opened_at=incident.opened_at,
    )

    contract_actions = [
        ActionContract(
            id=a.id,
            plan_id=a.plan_id,
            action_type=ActionType(a.action_type),
            description=a.description,
            target_service_id=a.target_service_id,
            parameters=a.parameters or {},
            order=a.order,
        )
        for a in actions
    ]

    contract_plan = PlanContract(
        id=plan.id,
        incident_id=plan.incident_id,
        diagnosis_id=plan.diagnosis_id,
        status=PlanStatus.APPROVED,
        rationale=plan.rationale,
        actions=contract_actions,
    )

    # Isolated import for mono-repo safety
    import sys
    from pathlib import Path
    import importlib.util

    worker_src = Path(__file__).resolve().parents[3] / "worker" / "src"
    adapter_path = worker_src / "remediation_adapter.py"
    verif_path = worker_src / "verification_engine.py"

    if "worker_remediation_adapter" not in sys.modules:
        spec = importlib.util.spec_from_file_location("worker_remediation_adapter", adapter_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["worker_remediation_adapter"] = mod
        spec.loader.exec_module(mod)

    if "worker_verification_engine" not in sys.modules:
        spec_v = importlib.util.spec_from_file_location("worker_verification_engine", verif_path)
        mod_v = importlib.util.module_from_spec(spec_v)
        sys.modules["worker_verification_engine"] = mod_v
        spec_v.loader.exec_module(mod_v)

    orchestrator = sys.modules["worker_remediation_adapter"].RemediationOrchestrator()
    execution_result = orchestrator.execute_plan(contract_plan, contract_incident)

    # 5. Mark Plan Executed
    plan.status = PlanStatus.COMPLETED.value
    plan.executed_at = now

    # 6. Post-Remediation Verification (Rule 17)
    verifier = sys.modules["worker_verification_engine"].TelemetryVerificationEngine()
    verification_contract = verifier.verify_remediation(contract_incident, contract_plan)

    db_verification = VerificationModel(
        id=verification_contract.id,
        incident_id=incident_id,
        plan_id=plan.id,
        status=verification_contract.status.value,
        telemetry_summary=verification_contract.telemetry_summary,
        verified_at=verification_contract.verified_at,
        metrics=verification_contract.metrics,
    )
    db.add(db_verification)

    # 7. Advance Incident State to RESOLVED upon verified remediation
    if verification_contract.status == VerificationStatus.PASSED:
        incident.status = IncidentStatus.RESOLVED.value
        incident.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(incident)
    db.refresh(plan)

    return {
        "status": "success",
        "incident_id": incident_id,
        "incident_status": incident.status,
        "plan_status": plan.status,
        "approval": {
            "id": approval.id,
            "decision": approval.decision,
            "approver_id": approval.approver_id,
            "decided_at": approval.decided_at.isoformat(),
            "notes": approval.notes,
        },
        "execution": execution_result,
        "verification": {
            "id": db_verification.id,
            "status": db_verification.status,
            "telemetry_summary": db_verification.telemetry_summary,
            "verified_at": db_verification.verified_at.isoformat(),
            "metrics": db_verification.metrics,
        },
    }


@router.post(
    "/{incident_id}/remediation/reject",
    response_model=Dict[str, Any],
    summary="Human-in-the-Loop reject remediation plan",
    description="Records human rejection of the drafted remediation plan.",
)
def reject_remediation(
    incident_id: str,
    payload: RejectionRequest,
    db: Session = Depends(get_db),
):
    incident = db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident '{incident_id}' not found")

    plan = db.query(RemediationPlanModel).filter(RemediationPlanModel.incident_id == incident_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No remediation plan found to reject for incident '{incident_id}'",
        )

    now = datetime.now(timezone.utc)
    approval = ApprovalModel(
        id=f"appr-{now.strftime('%Y%m%d%H%M%S')}-{incident_id[:6]}",
        incident_id=incident_id,
        plan_id=plan.id,
        decision="rejected",
        approver_id=payload.approver_id,
        decided_at=now,
        notes=payload.notes,
    )
    db.add(approval)

    plan.status = PlanStatus.REJECTED.value
    # Incident returns to OPEN for manual SRE intervention
    incident.status = IncidentStatus.OPEN.value

    db.commit()

    return {
        "status": "rejected",
        "incident_id": incident_id,
        "plan_id": plan.id,
        "plan_status": plan.status,
        "incident_status": incident.status,
        "notes": payload.notes,
    }


@router.get(
    "/{incident_id}/verification",
    response_model=Dict[str, Any],
    summary="Get post-remediation verification status",
    description="Retrieves the verification audit and telemetry status for an incident.",
)
def get_incident_verification(incident_id: str, db: Session = Depends(get_db)):
    verification = db.query(VerificationModel).filter(VerificationModel.incident_id == incident_id).first()
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verification record found for incident '{incident_id}'",
        )

    return {
        "id": verification.id,
        "incident_id": verification.incident_id,
        "plan_id": verification.plan_id,
        "status": verification.status,
        "telemetry_summary": verification.telemetry_summary,
        "verified_at": verification.verified_at.isoformat() if verification.verified_at else None,
        "metrics": verification.metrics,
    }
