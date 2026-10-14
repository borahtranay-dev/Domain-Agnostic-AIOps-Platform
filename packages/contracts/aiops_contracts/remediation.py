"""Phase P2 Shared Contracts - Remediation Models."""
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import Field
from .common import ContractModel, new_id, utc_now
from .incident import Severity


class ActionType(str, Enum):
    PULL_REQUEST = "pull_request"
    ROLLBACK = "rollback"
    CONTAINER_RESTART = "container_restart"
    CONFIG_UPDATE = "config_update"
    SCALE_SERVICE = "scale_service"


class PlanStatus(str, Enum):
    DRAFTED = "drafted"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class RemediationAction(ContractModel):
    id: str = Field(default_factory=new_id)
    plan_id: str
    action_type: ActionType
    description: str
    target_service_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    order: int = 1


class RemediationPlan(ContractModel):
    id: str = Field(default_factory=new_id)
    incident_id: str
    diagnosis_id: str
    status: PlanStatus = PlanStatus.DRAFTED
    rationale: str
    risk_level: Severity = Severity.LOW
    actions: list[RemediationAction] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    executed_at: datetime | None = None
