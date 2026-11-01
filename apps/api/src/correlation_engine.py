"""Event Correlation and Incident Generation Engine.

Owner: Taranay (Backend Lead) / Saurav (DevOps & Integration)
Phase: P4 (Event & Incident Pipeline & Webhook Adapters)

Processes normalized telemetry events from Redis/DB, evaluates correlation rules
(temporal window, service grouping, severity classification), and automatically
creates/updates incidents and extracts evidence bundles.
"""
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from aiops_contracts import Event, Incident, Evidence, IncidentStatus, Severity, EvidenceKind
from src.models.event import EventModel
from src.models.incident import IncidentModel
from src.models.evidence import EvidenceModel

logger = logging.getLogger(__name__)

CORRELATION_WINDOW_MINUTES = 10


class EventCorrelationEngine:
    """Engine that correlates incoming events into unified Incident tickets with evidence."""

    @staticmethod
    def classify_severity(event: Event) -> Severity:
        """Classifies incident severity based on event metadata and payload."""
        payload = event.payload or {}
        raw_severity = str(payload.get("severity", "")).lower()
        summary_lower = event.summary.lower()

        if "critical" in raw_severity or "fatal" in summary_lower or "out of memory" in summary_lower or "oom" in summary_lower:
            return Severity.CRITICAL
        elif "high" in raw_severity or "exhausted" in summary_lower or "timeout" in summary_lower:
            return Severity.HIGH
        elif "warning" in raw_severity or "medium" in summary_lower:
            return Severity.MEDIUM
        return Severity.LOW

    @staticmethod
    def derive_incident_title(event: Event) -> str:
        """Derives a concise, professional incident title from the initiating event."""
        service = event.service_id or "Core Services"
        if event.summary:
            return f"Outage on {service}: {event.summary[:80]}"
        return f"Incident on {service}: {event.type.value if hasattr(event.type, 'value') else event.type}"

    @classmethod
    def process_event(cls, event: Event, db: Session) -> Tuple[IncidentModel, Optional[EvidenceModel]]:
        """Processes a normalized event: correlates to an active incident or opens a new one."""
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=CORRELATION_WINDOW_MINUTES)

        # Look for an existing open incident for the same service and environment within correlation window
        existing_incident = (
            db.query(IncidentModel)
            .filter(
                IncidentModel.service_id == event.service_id,
                IncidentModel.environment_id == event.environment_id,
                IncidentModel.status.in_([IncidentStatus.OPEN.value, IncidentStatus.DIAGNOSING.value]),
                IncidentModel.opened_at >= window_start,
            )
            .order_by(IncidentModel.opened_at.desc())
            .first()
        )

        incident_id: str
        incident_db: IncidentModel

        if existing_incident:
            # Correlate into existing incident
            current_event_ids = list(existing_incident.event_ids or [])
            if event.id not in current_event_ids:
                current_event_ids.append(event.id)
                existing_incident.event_ids = current_event_ids

            # Upgrade severity if incoming event is more critical
            incoming_severity = cls.classify_severity(event)
            if incoming_severity == Severity.CRITICAL:
                existing_incident.severity = Severity.CRITICAL.value

            db.commit()
            db.refresh(existing_incident)
            incident_db = existing_incident
            logger.info(f"Correlated Event {event.id} into existing Incident {incident_db.id}")
        else:
            # Open a new Incident
            new_incident_id = str(uuid.uuid4())
            title = cls.derive_incident_title(event)
            severity = cls.classify_severity(event)

            incident_db = IncidentModel(
                id=new_incident_id,
                title=title,
                status=IncidentStatus.OPEN.value,
                severity=severity.value,
                pipeline_id=event.pipeline_id,
                service_id=event.service_id,
                environment_id=event.environment_id or "production",
                event_ids=[event.id],
                opened_at=now,
                resolved_at=None,
            )
            db.add(incident_db)
            db.commit()
            db.refresh(incident_db)
            logger.info(f"Opened new Incident {incident_db.id} from Event {event.id}")

        # Extract telemetry evidence from event payload and attach to incident
        evidence_db: Optional[EvidenceModel] = None
        evidence_kind = EvidenceKind.LOG
        if "metric" in event.source or "prometheus" in event.source or "cpu" in event.summary.lower():
            evidence_kind = EvidenceKind.METRIC

        evidence_content = (
            event.summary
            + (f" | Details: {event.payload}" if event.payload else "")
        )

        evidence_db = EvidenceModel(
            id=str(uuid.uuid4()),
            incident_id=incident_db.id,
            kind=evidence_kind.value,
            source=event.source,
            content=evidence_content,
            captured_at=event.occurred_at or now,
            metadata_payload={"event_id": event.id, "type": str(event.type)},
        )
        db.add(evidence_db)
        db.commit()
        db.refresh(evidence_db)

        return incident_db, evidence_db
