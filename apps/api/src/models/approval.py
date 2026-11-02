"""SQLAlchemy model for Human-in-the-Loop Approval entity.

Phase: P6 (Remediation & GitHub Automation)
Owner: Taranay (Backend Lead) / Saurav (DevOps Lead)
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from src.database import Base


class ApprovalModel(Base):
    __tablename__ = "approvals"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False, index=True)
    plan_id = Column(String(64), ForeignKey("remediation_plans.id"), nullable=False, index=True)
    decision = Column(String(64), nullable=False, default="pending", index=True)
    approver_id = Column(String(128), nullable=False, index=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=False, default="")

    def __repr__(self) -> str:
        return f"<ApprovalModel(id='{self.id}', decision='{self.decision}', approver='{self.approver_id}')>"
