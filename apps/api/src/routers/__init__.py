"""API routers package."""
from .events import router as events_router
from .incidents import router as incidents_router

__all__ = ["events_router", "incidents_router"]
