"""Foundation tests for apps/worker Redis connection logic."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add apps/worker to path
worker_path = Path(__file__).resolve().parents[2] / "apps" / "worker"
sys.path.insert(0, str(worker_path))

from src.worker import get_redis_connection


@patch("src.worker.Redis")
def test_worker_redis_connection_success(mock_redis_cls):
    """Verify get_redis_connection returns connection when ping succeeds."""
    mock_conn = MagicMock()
    mock_conn.ping.return_value = True
    mock_redis_cls.from_url.return_value = mock_conn

    conn = get_redis_connection(max_retries=1)
    assert conn == mock_conn
    mock_conn.ping.assert_called_once()


@patch("src.worker.Redis")
def test_worker_redis_connection_failure(mock_redis_cls):
    """Verify get_redis_connection raises ConnectionError when ping fails."""
    mock_conn = MagicMock()
    mock_conn.ping.side_effect = Exception("Connection refused")
    mock_redis_cls.from_url.return_value = mock_conn

    import pytest
    with pytest.raises(ConnectionError):
        get_redis_connection(max_retries=1, retry_interval=0.1)
