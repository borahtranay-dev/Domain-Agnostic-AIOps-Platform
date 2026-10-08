"""P2 DRAFT - pending approval by all leads."""
from datetime import datetime
from enum import Enum
from pydantic import Field
from .common import ContractModel, new_id, utc_now


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    DIAGNOSING = "diagnosing"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Incident(ContractModel):
    id: str = Field(default_factory=new_id)
    title: str
    status: IncidentStatus = IncidentStatus.OPEN
    severity: Severity = Severity.MEDIUM
    pipeline_id: str | None = None
    service_id: str | None = None
    environment_id: str | None = None
    event_ids: list[str] = Field(default_factory=list)
    opened_at: datetime = Field(default_factory=utc_now)
    resolved_at: datetime | None = None
