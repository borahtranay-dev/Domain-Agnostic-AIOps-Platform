"""SQLAlchemy model for Event entity."""
from sqlalchemy import Column, String, DateTime, Text, JSON
from src.database import Base


class EventModel(Base):
    __tablename__ = "events"

    id = Column(String(64), primary_key=True, index=True)
    type = Column(String(64), nullable=False, index=True)
    source = Column(String(128), nullable=False, index=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), nullable=False)
    pipeline_id = Column(String(128), nullable=True, index=True)
    service_id = Column(String(128), nullable=True, index=True)
    environment_id = Column(String(64), nullable=True, index=True)
    summary = Column(Text, nullable=False, default="")
    payload = Column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<EventModel(id='{self.id}', type='{self.type}', source='{self.source}')>"
