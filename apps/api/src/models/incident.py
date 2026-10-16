"""SQLAlchemy model for Incident entity."""
from sqlalchemy import Column, String, DateTime, JSON
from src.database import Base


class IncidentModel(Base):
    __tablename__ = "incidents"

    id = Column(String(64), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    status = Column(String(64), nullable=False, default="open", index=True)
    severity = Column(String(64), nullable=False, default="medium", index=True)
    pipeline_id = Column(String(128), nullable=True, index=True)
    service_id = Column(String(128), nullable=True, index=True)
    environment_id = Column(String(64), nullable=True, index=True)
    event_ids = Column(JSON, nullable=False, default=list)
    opened_at = Column(DateTime(timezone=True), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<IncidentModel(id='{self.id}', status='{self.status}', severity='{self.severity}')>"
