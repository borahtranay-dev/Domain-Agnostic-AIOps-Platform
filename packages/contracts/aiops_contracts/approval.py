"""Phase P2 Shared Contracts - Human-in-the-Loop Approval Models."""
from datetime import datetime
from enum import Enum
from pydantic import Field
from .common import ContractModel, new_id, utc_now


class ApprovalDecision(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Approval(ContractModel):
    id: str = Field(default_factory=new_id)
    incident_id: str
    plan_id: str
    decision: ApprovalDecision = ApprovalDecision.PENDING
    approver_id: str
    decided_at: datetime | None = None
    notes: str = ""
