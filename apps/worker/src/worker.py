"""RQ Worker entrypoint for background task execution.

Owner: Taranay (Backend Lead)
Phase: P1 (Technical Foundation)
"""
import logging
import sys
import time
from redis import Redis
from rq import Queue, Worker
from src.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] [worker] %(message)s",
)
logger = logging.getLogger("aiops-worker")


def get_redis_connection(max_retries: int = 5, retry_interval: float = 2.0) -> Redis:
    """Connect to Redis with retry support for container startup orchestration."""
    conn = Redis.from_url(settings.REDIS_URL)
    for attempt in range(1, max_retries + 1):
        try:
            if conn.ping():
                logger.info(f"Successfully connected to Redis at {settings.REDIS_URL}")
                return conn
        except Exception as e:
            logger.warning(
                f"Redis connection attempt {attempt}/{max_retries} failed: {e}. Retrying in {retry_interval}s..."
            )
            time.sleep(retry_interval)

    logger.error("Could not establish connection to Redis after maximum retries.")
    raise ConnectionError(f"Failed to connect to Redis at {settings.REDIS_URL}")


def start_worker():
    """Start the RQ worker listening on defined queues."""
    logger.info("Initializing AIOps Background Worker (Phase 1 Foundation)...")
    try:
        redis_conn = get_redis_connection()
        queues = [Queue(name, connection=redis_conn) for name in settings.QUEUES]
        worker = Worker(queues, connection=redis_conn)

        logger.info(f"Worker listening on queues: {settings.QUEUES}")
        worker.work(with_scheduler=True)
    except Exception as e:
        logger.error(f"Fatal error in worker process: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_worker()
