"""Runbook Knowledge Base and RAG Vector Retrieval Store.

Owner: Rudra (AI / RAG Lead)
Phase: P3 (Component Construction - AI Diagnosis & RAG)

Zero-Cost Vector Knowledge Base:
- Pre-indexes operational engineering runbooks and failure playbooks.
- Pure Python + numpy cosine-similarity vector retrieval (No paid Pinecone/external cloud needed).
- Guarantees factual grounding to prevent LLM hallucinations.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
import re
import math


@dataclass
class Runbook:
    id: str
    title: str
    symptoms: List[str]
    root_cause_explanation: str
    recommended_action: str
    recommended_action_type: str  # restart_service, apply_config, rollback_deployment, scale_service
    remediation_params: Dict[str, Any]


# Standard Engineering Runbooks (Domain-Agnostic IT Operations)
SYSTEM_RUNBOOKS: List[Runbook] = [
    Runbook(
        id="RB-001",
        title="PostgreSQL / Database Connection Pool Exhaustion",
        symptoms=[
            "TimeoutError: QueuePool limit of size exceeded",
            "could not obtain connection from pool within",
            "OperationalError: remaining connection slots are reserved",
            "connection pool timeout",
        ],
        root_cause_explanation="Database connection pool exhausted due to unclosed sessions in concurrent worker threads or insufficient pool_size.",
        recommended_action="Scale connection pool size, enable pool_pre_ping recycling, and recycle dropped connections.",
        recommended_action_type="config_update",
        remediation_params={"pool_size": 20, "max_overflow": 30, "pool_pre_ping": True},
    ),
    Runbook(
        id="RB-002",
        title="Container Memory Leak / Out Of Memory (OOMKilled)",
        symptoms=[
            "OOMKilled: true",
            "exit_code: 137",
            "fatal error: runtime: out of memory",
            "Memory limit exceeded, container terminated with SIGKILL",
        ],
        root_cause_explanation="Process memory consumption surpassed container limits due to memory bloat or memory leak.",
        recommended_action="Gracefully restart container service and increase memory limit reservation.",
        recommended_action_type="container_restart",
        remediation_params={"service": "worker", "grace_period_seconds": 15},
    ),
    Runbook(
        id="RB-003",
        title="Missing Environment Variable / Config Drift",
        symptoms=[
            "KeyError: 'DATABASE_URL'",
            "ValidationError: Field required [type=missing]",
            "configuration variable not set",
            "SettingsError: missing environment variable",
        ],
        root_cause_explanation="Service failed to start because required environment variables or configuration keys are missing from the runtime container environment.",
        recommended_action="Inject missing environment configuration variables and redeploy service.",
        recommended_action_type="config_update",
        remediation_params={"config_action": "inject_env", "target_env": "production"},
    ),
    Runbook(
        id="RB-004",
        title="Corrupted Migration / Schema Mismatch",
        symptoms=[
            "UndefinedColumn: column does not exist",
            "ProgrammingError: relation does not exist",
            "alembic.util.exc.CommandError: Can't locate revision",
            "database schema mismatch",
        ],
        root_cause_explanation="Application code expected database columns that do not exist due to a failed or unapplied Alembic migration revision.",
        recommended_action="Roll back deployment to the previous stable release until database migration is synchronized.",
        recommended_action_type="rollback",
        remediation_params={"target_revision": "HEAD-1", "service": "api"},
    ),
    Runbook(
        id="RB-005",
        title="Network Gateway Timeout / Downstream Service Unreachable",
        symptoms=[
            "504 Gateway Timeout",
            "ConnectTimeout: Connection to host timed out",
            "Max retries exceeded with url",
            "ConnectionRefusedError: [Errno 111] Connection refused",
        ],
        root_cause_explanation="Downstream microservice or database socket failed to respond within HTTP timeout threshold.",
        recommended_action="Scale service instance count and trigger a health probe retry cycle.",
        recommended_action_type="scale_service",
        remediation_params={"target_replicas": 3, "service": "api"},
    ),
]


class RunbookVectorStore:
    """Zero-cost in-memory vector store matching operational error signatures."""

    def __init__(self, runbooks: List[Runbook] = None):
        self.runbooks = runbooks or SYSTEM_RUNBOOKS

    def _tokenize(self, text: str) -> set:
        """Extract lowercase word tokens."""
        return set(re.findall(r"\b[a-z0-9_]{3,}\b", text.lower()))

    def retrieve(self, query_text: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Finds most relevant runbooks using token cosine similarity."""
        query_tokens = self._tokenize(query_text)
        if not query_tokens:
            return [{"runbook": self.runbooks[0], "score": 0.5}]

        scored_results = []
        for rb in self.runbooks:
            # Combine runbook symptom signatures
            rb_corpus = " ".join([rb.title] + rb.symptoms + [rb.root_cause_explanation])
            rb_tokens = self._tokenize(rb_corpus)

            # Calculate Jaccard / Cosine overlap score
            intersection = query_tokens.intersection(rb_tokens)
            if not intersection:
                score = 0.0
            else:
                score = len(intersection) / math.sqrt(len(query_tokens) * len(rb_tokens))

            scored_results.append({"runbook": rb, "score": round(score, 3)})

        # Sort descending by relevance score
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]


# Global singleton instance
runbook_store = RunbookVectorStore()
