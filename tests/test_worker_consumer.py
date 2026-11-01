"""Unit tests for Phase P4 background worker event queue consumer.

Owner: Saurav (DevOps Lead) / Taranay (Backend Lead)
Phase: P4 (Event & Incident Pipeline & Webhook Adapters)
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime, timezone
import pytest

# Ensure apps/worker is isolated and in sys.path
WORKER_DIR = Path(__file__).resolve().parent.parent / "apps" / "worker"
if str(WORKER_DIR) not in sys.path:
    sys.path.insert(0, str(WORKER_DIR))

# Clear cached src modules
for mod in list(sys.modules.keys()):
    if mod == "src" or mod.startswith("src."):
        del sys.modules[mod]

from src.event_consumer import consume_single_event, EVENTS_QUEUE_KEY
from aiops_contracts import Event, EventType


def test_consume_single_event_success():
    """Verify event is successfully dequeued and deserialized into Event contract."""
    test_event = Event(
        type=EventType.TELEMETRY,
        source="prometheus-alertmanager",
        service_id="auth-service",
        environment_id="production",
        summary="High memory consumption detected",
        payload={"memory_mb": 4096},
    )

    mock_redis = MagicMock()
    mock_redis.lpop.return_value = test_event.model_dump_json().encode("utf-8")

    consumed = consume_single_event(mock_redis)
    assert consumed is not None
    assert consumed.id == test_event.id
    assert consumed.source == "prometheus-alertmanager"
    assert consumed.service_id == "auth-service"
    assert consumed.payload["memory_mb"] == 4096
    mock_redis.lpop.assert_called_once_with(EVENTS_QUEUE_KEY)


def test_consume_single_event_empty_queue():
    """Verify None is returned when queue is empty."""
    mock_redis = MagicMock()
    mock_redis.lpop.return_value = None

    consumed = consume_single_event(mock_redis)
    assert consumed is None
