"""P2 DRAFT - pending approval by all leads."""
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import Field
from .common import ContractModel, new_id, utc_now


class EventType(str, Enum):
    PIPELINE_RUN = "pipeline_run"
    DEPLOYMENT = "deployment"
    TELEMETRY = "telemetry"
    EXTERNAL = "external"


class Event(ContractModel):
    id: str = Field(default_factory=new_id)
    type: EventType
    source: str
    occurred_at: datetime = Field(default_factory=utc_now)
    received_at: datetime = Field(default_factory=utc_now)
    pipeline_id: str | None = None
    service_id: str | None = None
    environment_id: str | None = None
    summary: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
