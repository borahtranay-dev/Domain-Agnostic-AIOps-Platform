"""P2 DRAFT - pending approval by all leads."""
from datetime import datetime
from enum import Enum
from pydantic import Field
from .common import ContractModel, new_id, utc_now


class EvidenceKind(str, Enum):
    LOG = "log"
    STACK_TRACE = "stack_trace"
    COMMIT = "commit"
    PIPELINE_INFO = "pipeline_info"
    CONFIGURATION = "configuration"
    METRIC = "metric"
    DOCUMENTATION = "documentation"
    KNOWLEDGE_BASE = "knowledge_base"


class Evidence(ContractModel):
    """Raw observation or artifact. Must never contain AI conclusions."""
    id: str = Field(default_factory=new_id)
    incident_id: str
    kind: EvidenceKind
    source: str
    content: str
    reference: str | None = None
    collected_at: datetime = Field(default_factory=utc_now)
