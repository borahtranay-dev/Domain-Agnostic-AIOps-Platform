"""Worker configuration module."""
import os
from pydantic_settings import BaseSettings


class WorkerSettings(BaseSettings):
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_URL: str = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")
    QUEUES: list[str] = ["aiops-default"]
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = WorkerSettings()
