"""P2 DRAFT - pending approval by all leads."""
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, ConfigDict


def new_id() -> str:
    """Generate a UUID4 string identifier."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class ContractModel(BaseModel):
    """Base model for domain-agnostic contracts."""
    model_config = ConfigDict(extra="forbid")
