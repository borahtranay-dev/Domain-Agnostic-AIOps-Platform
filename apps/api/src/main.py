"""FastAPI Application Entrypoint for Domain-Agnostic AIOps API Subsystem.

Owner: Taranay (Backend Lead)
Phase: P1 (Technical Foundation)
"""
import redis
from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database import check_database_connection

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Domain-Agnostic AIOps Self-Healing Platform Core API",
)

# Enable CORS for Developer Cockpit (apps/web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint exposing API identity and documentation reference."""
    return {
        "service": "aiops-api",
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health")
def health_check():
    """Liveness probe to confirm that the HTTP server is alive and responding."""
    return {
        "status": "ok",
        "service": "api",
        "version": settings.VERSION,
    }


@app.get("/ready")
def readiness_check(response: Response):
    """Readiness probe checking downstream dependencies (PostgreSQL)."""
    db_ok, db_msg = check_database_connection()
    if not db_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "not_ready",
            "database": {"connected": False, "message": db_msg},
        }

    return {
        "status": "ready",
        "database": {"connected": True, "message": db_msg},
    }


@app.get("/api/v1/system-status")
def system_status():
    """Aggregated connectivity overview for all foundational infrastructure."""
    # Check Database
    db_ok, db_msg = check_database_connection()

    # Check Redis
    redis_ok = False
    redis_msg = ""
    try:
        r = redis.from_url(settings.REDIS_URL, socket_timeout=2)
        if r.ping():
            redis_ok = True
            redis_msg = "Redis connection healthy"
        else:
            redis_msg = "Redis ping returned false"
    except Exception as e:
        redis_msg = f"Redis connection failed: {str(e)}"

    return {
        "service": "api",
        "version": settings.VERSION,
        "dependencies": {
            "postgresql": {"connected": db_ok, "details": db_msg},
            "redis": {"connected": redis_ok, "details": redis_msg},
        },
    }
