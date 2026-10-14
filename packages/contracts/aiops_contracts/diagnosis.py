"""Phase P2 Shared Contracts - AI Diagnosis Models."""
from datetime import datetime
from pydantic import Field
from .common import ContractModel, new_id, utc_now


class Diagnosis(ContractModel):
    """AI diagnosis grounded in collected evidence."""
    id: str = Field(default_factory=new_id)
    incident_id: str
    probable_root_cause: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    uncertainty_notes: str | None = None
    recommended_remediation: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
