"""AI Worker configuration module.

Owner: Rudra (AI / RAG Lead)
Phase: P3 (Component Construction - AI Diagnosis & RAG)
"""
import os
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    PROJECT_NAME: str = "AIOps AI Diagnosis Subsystem"
    VERSION: str = "0.2.0"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Zero-Cost LLM configurations
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "gemini-1.5-flash")
    USE_OFFLINE_FALLBACK: bool = True  # Ensures 100% deterministic testing without API keys

    # Inter-service connectivity
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    REDIS_EVENTS_QUEUE: str = "aiops:events_queue"


settings = AISettings()
