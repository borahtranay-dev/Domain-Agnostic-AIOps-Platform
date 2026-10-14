"""Phase P2 Shared Contracts - Post-Remediation Verification Models."""
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import Field
from .common import ContractModel, new_id, utc_now


class VerificationStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"


class Verification(ContractModel):
    id: str = Field(default_factory=new_id)
    incident_id: str
    plan_id: str
    status: VerificationStatus = VerificationStatus.PENDING
    telemetry_summary: str = ""
    verified_at: datetime = Field(default_factory=utc_now)
    metrics: dict[str, Any] = Field(default_factory=dict)
