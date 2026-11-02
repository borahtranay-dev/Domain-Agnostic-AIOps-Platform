"""SQLAlchemy models for RemediationPlan and RemediationAction entities.

Phase: P6 (Remediation & GitHub Automation)
Owner: Taranay (Backend Lead) / Saurav (DevOps Lead)
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, JSON, ForeignKey
from src.database import Base


class RemediationPlanModel(Base):
    __tablename__ = "remediation_plans"

    id = Column(String(64), primary_key=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.id"), nullable=False, index=True)
    diagnosis_id = Column(String(64), nullable=False, index=True)
    status = Column(String(64), nullable=False, default="drafted", index=True)
    rationale = Column(Text, nullable=False)
    risk_level = Column(String(64), nullable=False, default="low")
    created_at = Column(DateTime(timezone=True), nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<RemediationPlanModel(id='{self.id}', incident_id='{self.incident_id}', status='{self.status}')>"


class RemediationActionModel(Base):
    __tablename__ = "remediation_actions"

    id = Column(String(64), primary_key=True, index=True)
    plan_id = Column(String(64), ForeignKey("remediation_plans.id"), nullable=False, index=True)
    action_type = Column(String(64), nullable=False, index=True)
    description = Column(Text, nullable=False)
    target_service_id = Column(String(128), nullable=True, index=True)
    parameters = Column(JSON, nullable=False, default=dict)
    order = Column(Integer, nullable=False, default=1)

    def __repr__(self) -> str:
        return f"<RemediationActionModel(id='{self.id}', plan_id='{self.plan_id}', type='{self.action_type}')>"
