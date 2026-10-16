"""SQLAlchemy model for Diagnosis entity."""
from sqlalchemy import Column, String, DateTime, Text, Float, JSON, ForeignKey
from src.database import Base


class DiagnosisModel(Base):
    __tablename__ = "diagnoses"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False, index=True)
    probable_root_cause = Column(Text, nullable=False)
    supporting_evidence_ids = Column(JSON, nullable=False, default=list)
    contradicting_evidence_ids = Column(JSON, nullable=False, default=list)
    confidence = Column(Float, nullable=False, default=0.0)
    uncertainty_notes = Column(Text, nullable=True)
    recommended_remediation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"<DiagnosisModel(id='{self.id}', incident_id='{self.incident_id}', confidence={self.confidence})>"
