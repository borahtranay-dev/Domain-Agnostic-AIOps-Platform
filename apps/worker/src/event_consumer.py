"""Asynchronous Redis Event Queue Consumer.

Owner: Taranay (Backend Lead) / Saurav (DevOps Lead)
Phase: P4 (Event & Incident Pipeline & Webhook Adapters)

Dequeues normalized telemetry and deployment events from Redis 'aiops:events_queue'
and manages asynchronous background processing.
"""
import json
import logging
from typing import Optional
from redis import Redis

from aiops_contracts import Event

logger = logging.getLogger("aiops-worker.event_consumer")

EVENTS_QUEUE_KEY = "aiops:events_queue"


def consume_single_event(redis_conn: Redis, timeout: int = 1) -> Optional[Event]:
    """Pops and parses a single Event contract from the Redis queue.
    
    Returns:
        Normalized Event contract instance or None if queue is empty.
    """
    try:
        raw_item = redis_conn.lpop(EVENTS_QUEUE_KEY)
        if not raw_item:
            return None

        event_data = json.loads(raw_item.decode("utf-8") if isinstance(raw_item, bytes) else raw_item)
        event_obj = Event.model_validate(event_data)
        logger.info(f"Consumed Event from Redis: ID={event_obj.id}, Source={event_obj.source}, Service={event_obj.service_id}")
        return event_obj
    except Exception as e:
        logger.error(f"Error consuming event from queue '{EVENTS_QUEUE_KEY}': {e}")
        return None
