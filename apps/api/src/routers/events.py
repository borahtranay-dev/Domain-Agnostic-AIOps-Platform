"""Event Ingestion and Retrieval Router for AIOps API.

Owner: Taranay (Backend Lead)
Phase: P3 (Component Construction)
"""
import json
import logging
import redis
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from aiops_contracts import Event, EventType
from src.config import settings
from src.database import get_db
from src.models.event import EventModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["Events"])


def push_to_redis_queue(event: Event) -> bool:
    """Best-effort enqueue to Redis events_queue for background worker."""
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=2)
        r.rpush("aiops:events_queue", event.model_dump_json())
        return True
    except Exception as e:
        logger.warning(f"Failed to enqueue event {event.id} to Redis: {e}")
        return False


@router.post(
    "",
    response_model=Event,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest an operational event",
    description="Captures raw failure/telemetry events, validates against P2 Event contract, and persists to database.",
)
def ingest_event(event_in: Event, db: Session = Depends(get_db)):
    """Ingest a validated operational event into the AIOps platform."""
    # Convert P2 Contract model to SQLAlchemy ORM model
    db_event = EventModel(
        id=event_in.id,
        type=event_in.type.value if isinstance(event_in.type, EventType) else str(event_in.type),
        source=event_in.source,
        occurred_at=event_in.occurred_at,
        received_at=event_in.received_at,
        pipeline_id=event_in.pipeline_id,
        service_id=event_in.service_id,
        environment_id=event_in.environment_id,
        summary=event_in.summary,
        payload=event_in.payload,
    )

    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    # Push to Redis queue for background worker ingestion
    push_to_redis_queue(event_in)

    return event_in


@router.get(
    "",
    response_model=List[Event],
    summary="List ingested events",
    description="Returns a paginated list of ingested events with optional filtering by type and source.",
)
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    type: Optional[EventType] = Query(None, description="Filter by EventType"),
    source: Optional[str] = Query(None, description="Filter by event source"),
    db: Session = Depends(get_db),
):
    query = db.query(EventModel)
    if type:
        query = query.filter(EventModel.type == type.value)
    if source:
        query = query.filter(EventModel.source == source)

    db_events = query.order_by(EventModel.received_at.desc()).offset(skip).limit(limit).all()

    # Map back to P2 Contract models
    return [
        Event(
            id=e.id,
            type=EventType(e.type),
            source=e.source,
            occurred_at=e.occurred_at,
            received_at=e.received_at,
            pipeline_id=e.pipeline_id,
            service_id=e.service_id,
            environment_id=e.environment_id,
            summary=e.summary,
            payload=e.payload or {},
        )
        for e in db_events
    ]


@router.get(
    "/{event_id}",
    response_model=Event,
    summary="Get single event by ID",
    description="Retrieves a specific operational event by its unique ID.",
)
def get_event(event_id: str, db: Session = Depends(get_db)):
    db_event = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event '{event_id}' not found")

    return Event(
        id=db_event.id,
        type=EventType(db_event.type),
        source=db_event.source,
        occurred_at=db_event.occurred_at,
        received_at=db_event.received_at,
        pipeline_id=db_event.pipeline_id,
        service_id=db_event.service_id,
        environment_id=db_event.environment_id,
        summary=db_event.summary,
        payload=db_event.payload or {},
    )
