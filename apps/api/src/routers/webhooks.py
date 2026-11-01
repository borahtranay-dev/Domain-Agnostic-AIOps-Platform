"""Webhook Ingestion Adapters for AIOps Platform.

Owner: Saurav (DevOps & Integration) / Taranay (Backend)
Phase: P4 (Event & Incident Pipeline & Webhook Adapters)

Normalizes raw provider-specific webhook payloads into generic, domain-agnostic P2 Event contracts.
Supported Providers:
1. Prometheus Alertmanager (telemetry / metric anomalies)
2. GitHub Deployment / CI-CD Actions (deployment / pipeline failures)
3. Generic Custom Application Webhook (generic HTTP error reports)
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from aiops_contracts import Event, EventType
from src.database import get_db
from src.models.event import EventModel
from src.routers.events import push_to_redis_queue
from src.correlation_engine import EventCorrelationEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhook Adapters"])


# ─────────────────────────────────────────────────────────────────────────────
# 1. Prometheus Alertmanager Adapter
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/prometheus",
    response_model=List[Event],
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Prometheus Alertmanager Webhook",
    description="Transforms Prometheus alerts into standardized, domain-agnostic telemetry events.",
)
async def ingest_prometheus_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """Parses Prometheus Alertmanager JSON payload and converts alerts to normalized Events."""
    try:
        raw_body = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {e}",
        )

    alerts = raw_body.get("alerts", [])
    if not alerts:
        # If payload is a single alert rather than array
        if "labels" in raw_body or "annotations" in raw_body:
            alerts = [raw_body]

    created_events: List[Event] = []

    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        service_id = (
            labels.get("service")
            or labels.get("job")
            or labels.get("app")
            or "unknown-service"
        )
        environment_id = (
            labels.get("environment")
            or labels.get("env")
            or raw_body.get("commonLabels", {}).get("environment")
            or "production"
        )
        alert_name = labels.get("alertname", "PrometheusAlert")
        summary_text = (
            annotations.get("summary")
            or annotations.get("description")
            or f"{alert_name}: {labels.get('severity', 'warning')} threshold breached"
        )

        # Parse timestamp if available
        starts_at_raw = alert.get("startsAt")
        occurred_at = datetime.now(timezone.utc)
        if starts_at_raw:
            try:
                occurred_at = datetime.fromisoformat(starts_at_raw.replace("Z", "+00:00"))
            except Exception:
                pass

        # Generic systems metric filter: exclude unauthorized non-telemetry tags
        sanitized_payload = {
            "alertname": alert_name,
            "status": alert.get("status", "firing"),
            "severity": labels.get("severity", "warning"),
            "generatorURL": alert.get("generatorURL", ""),
            "metrics": {
                k: v for k, v in labels.items()
                if not any(token in k.lower() for token in ["_id", "status", "cart", "order", "inventory"])
                or k in ["alertname", "severity", "instance", "job"]
            },
        }

        # Instantiate P2 Event Contract
        event_obj = Event(
            type=EventType.TELEMETRY,
            source="prometheus-alertmanager",
            occurred_at=occurred_at,
            received_at=datetime.now(timezone.utc),
            service_id=service_id,
            environment_id=environment_id,
            summary=summary_text,
            payload=sanitized_payload,
        )

        # Persist to relational DB
        db_event = EventModel(
            id=event_obj.id,
            type=event_obj.type.value,
            source=event_obj.source,
            occurred_at=event_obj.occurred_at,
            received_at=event_obj.received_at,
            pipeline_id=event_obj.pipeline_id,
            service_id=event_obj.service_id,
            environment_id=event_obj.environment_id,
            summary=event_obj.summary,
            payload=event_obj.payload,
        )
        db.add(db_event)
        created_events.append(event_obj)

        # Correlate event into an Incident and extract evidence bundle
        EventCorrelationEngine.process_event(event_obj, db)

        # Enqueue into Redis for worker
        push_to_redis_queue(event_obj)

    db.commit()
    return created_events


# ─────────────────────────────────────────────────────────────────────────────
# 2. GitHub Deployment / CI-CD Actions Adapter
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/github",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest GitHub Deployment/CI-CD Webhook",
    description="Transforms GitHub Actions and deployment status webhooks into normalized deployment events.",
)
async def ingest_github_webhook(
    request: Request,
    x_github_event: Optional[str] = Header(None, alias="X-GitHub-Event"),
    db: Session = Depends(get_db),
):
    """Parses GitHub Webhook payload (deployment_status, check_run, workflow_run) into Event."""
    try:
        raw_body = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {e}",
        )

    event_type_header = x_github_event or raw_body.get("event", "deployment_status")
    repository = raw_body.get("repository", {}).get("name", "unknown-repo")

    # Handle deployment_status event
    if "deployment_status" in raw_body or event_type_header == "deployment_status":
        dep_status = raw_body.get("deployment_status", {})
        deployment = raw_body.get("deployment", {})
        env = deployment.get("environment") or raw_body.get("environment") or "production"
        state = dep_status.get("state", "failure")
        summary_text = (
            dep_status.get("description")
            or f"GitHub deployment of '{repository}' entered state '{state}'"
        )
        pipeline_id = str(deployment.get("id") or dep_status.get("id") or "")

    # Handle workflow_run / check_run event
    elif "workflow_run" in raw_body:
        run = raw_body.get("workflow_run", {})
        env = "ci-cd"
        state = run.get("conclusion") or run.get("status") or "failed"
        summary_text = f"GitHub Workflow '{run.get('name')}' finished with conclusion '{state}'"
        pipeline_id = str(run.get("id") or "")
    else:
        # Fallback generic GitHub event
        env = raw_body.get("environment", "production")
        state = raw_body.get("state", "failure")
        summary_text = f"GitHub event '{event_type_header}' for repository '{repository}': {state}"
        pipeline_id = str(raw_body.get("id", ""))

    sanitized_payload = {
        "event": event_type_header,
        "repository": repository,
        "state": state,
        "sender": raw_body.get("sender", {}).get("login", "github-actions"),
        "commit": raw_body.get("deployment", {}).get("sha") or raw_body.get("after", ""),
    }

    event_obj = Event(
        type=EventType.DEPLOYMENT,
        source="github-actions",
        occurred_at=datetime.now(timezone.utc),
        received_at=datetime.now(timezone.utc),
        pipeline_id=pipeline_id,
        service_id=repository,
        environment_id=env,
        summary=summary_text,
        payload=sanitized_payload,
    )

    db_event = EventModel(
        id=event_obj.id,
        type=event_obj.type.value,
        source=event_obj.source,
        occurred_at=event_obj.occurred_at,
        received_at=event_obj.received_at,
        pipeline_id=event_obj.pipeline_id,
        service_id=event_obj.service_id,
        environment_id=event_obj.environment_id,
        summary=event_obj.summary,
        payload=event_obj.payload,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Auto-correlate into an Incident
    EventCorrelationEngine.process_event(event_obj, db)

    push_to_redis_queue(event_obj)
    return event_obj


# ─────────────────────────────────────────────────────────────────────────────
# 3. Generic Custom Application Webhook Adapter
# ─────────────────────────────────────────────────────────────────────────────
@router.post(
    "/generic",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest Generic Application Webhook",
    description="Normalizes raw JSON error alerts from custom external applications into generic Events.",
)
async def ingest_generic_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """Accepts arbitrary JSON failure alerts from monitored applications, extracts common keys, and normalizes."""
    try:
        raw_body = await request.json()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON payload: {e}",
        )

    # Heuristic extraction of common fields across external systems
    service_id = (
        raw_body.get("service")
        or raw_body.get("service_name")
        or raw_body.get("app")
        or raw_body.get("service_id")
        or "external-service"
    )
    environment_id = (
        raw_body.get("environment")
        or raw_body.get("env")
        or raw_body.get("environment_id")
        or "production"
    )
    summary_text = (
        raw_body.get("message")
        or raw_body.get("error")
        or raw_body.get("summary")
        or raw_body.get("description")
        or "External service failure reported via generic webhook"
    )
    source = (
        raw_body.get("source")
        or raw_body.get("reporter")
        or "generic-webhook-adapter"
    )

    # Sanitize payload: retain only verified operational telemetry metadata keys
    allowed_operational_keys = {
        "service", "service_name", "app", "service_id", "environment", "env",
        "environment_id", "message", "error", "summary", "description",
        "source", "reporter", "severity", "cpu_usage", "memory_mb", "latency_ms", "host",
        "timestamp", "level", "stack_trace"
    }
    clean_payload = {
        k: v for k, v in raw_body.items()
        if k.lower() in allowed_operational_keys
    }

    event_obj = Event(
        type=EventType.EXTERNAL,
        source=str(source),
        occurred_at=datetime.now(timezone.utc),
        received_at=datetime.now(timezone.utc),
        service_id=str(service_id),
        environment_id=str(environment_id),
        summary=str(summary_text),
        payload=clean_payload,
    )

    db_event = EventModel(
        id=event_obj.id,
        type=event_obj.type.value,
        source=event_obj.source,
        occurred_at=event_obj.occurred_at,
        received_at=event_obj.received_at,
        pipeline_id=event_obj.pipeline_id,
        service_id=event_obj.service_id,
        environment_id=event_obj.environment_id,
        summary=event_obj.summary,
        payload=event_obj.payload,
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Auto-correlate into an Incident
    EventCorrelationEngine.process_event(event_obj, db)

    push_to_redis_queue(event_obj)
    return event_obj
