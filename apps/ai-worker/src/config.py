"""AI Worker configuration module."""
import os
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    PROJECT_NAME: str = "AIOps AI Diagnosis Subsystem"
    VERSION: str = "0.1.0"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")


settings = AISettings()
