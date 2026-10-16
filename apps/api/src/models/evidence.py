"""SQLAlchemy model for Evidence entity."""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from src.database import Base


class EvidenceModel(Base):
    __tablename__ = "evidence"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False, index=True)
    kind = Column(String(64), nullable=False, index=True)
    source = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=False)
    metadata_payload = Column("metadata", JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<EvidenceModel(id='{self.id}', incident_id='{self.incident_id}', kind='{self.kind}')>"
