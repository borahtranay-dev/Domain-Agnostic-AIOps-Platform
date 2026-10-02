"""FastAPI Application Entrypoint for AI / RAG Subsystem Foundation.

Owner: Rudra (AI / RAG Lead)
Phase: P1 (Technical Foundation)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

# Import LangChain to verify foundation dependency readiness
try:
    import langchain
    import langchain_core
    LANGCHAIN_AVAILABLE = True
    LANGCHAIN_VERSION = langchain.__version__
except ImportError:
    LANGCHAIN_AVAILABLE = False
    LANGCHAIN_VERSION = "not_installed"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Domain-Agnostic AIOps AI Diagnosis and RAG Subsystem",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Service metadata endpoint."""
    return {
        "service": "ai-worker",
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "langchain_status": {
            "available": LANGCHAIN_AVAILABLE,
            "version": LANGCHAIN_VERSION,
        },
        "phase": "P1 Technical Foundation",
        "note": "RAG pipeline and root cause diagnosis scheduled for Phase P5",
    }


@app.get("/health")
def health_check():
    """Health check endpoint confirming service and AI library availability."""
    return {
        "status": "ok",
        "service": "ai-worker",
        "version": settings.VERSION,
        "langchain_available": LANGCHAIN_AVAILABLE,
    }
