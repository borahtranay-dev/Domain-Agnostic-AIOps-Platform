"""API configuration module."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AIOps Self-Healing Platform API"
    VERSION: str = "0.1.0"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "aiops_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "aiops_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "aiops_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))

    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_URL: str = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/0")

    AI_WORKER_URL: str = os.getenv("AI_WORKER_INTERNAL_URL", "http://ai-worker:8001")

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()
