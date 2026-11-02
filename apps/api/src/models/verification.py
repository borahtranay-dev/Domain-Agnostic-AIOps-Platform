"""SQLAlchemy model for Post-Remediation Verification entity.

Phase: P6 (Remediation & GitHub Automation)
Owner: Taranay (Backend Lead) / Saurav (DevOps Lead)
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from src.database import Base


class VerificationModel(Base):
    __tablename__ = "verifications"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False, index=True)
    plan_id = Column(String(64), ForeignKey("remediation_plans.id"), nullable=False, index=True)
    status = Column(String(64), nullable=False, default="pending", index=True)
    telemetry_summary = Column(Text, nullable=False, default="")
    verified_at = Column(DateTime(timezone=True), nullable=False)
    metrics = Column(JSON, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<VerificationModel(id='{self.id}', status='{self.status}', incident_id='{self.incident_id}')>"
