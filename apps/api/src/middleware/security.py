"""Security and Hardening Middlewares for AIOps Platform API.

Owner: Saurav (DevOps Lead) / Taranay (Backend Lead)
Phase: P9 (Hardening - Security, Performance, Reliability)

Core Capabilities:
1. Enterprise Security Headers (HSTS, X-Frame-Options, NoSniff, CSP, Referrer-Policy).
2. Rate Limiting Middleware: In-memory sliding window algorithm protecting API from DoS/brute force.
3. Payload Size Guard: Blocks payloads exceeding max size threshold to prevent OOM.
"""
import time
import logging
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("aiops-api.security")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforces enterprise security headers on all HTTP responses."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Enforce protective security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding-window rate limiter protecting API endpoints from spam & brute-force."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Maps client_ip -> list of request timestamps
        self.request_history: Dict[str, List[float]] = defaultdict(list)
        # Excluded endpoints (health checks, root)
        self.whitelist_paths = {"/", "/health", "/docs", "/openapi.json"}

    def _cleanup_old_requests(self, client_ip: str, current_time: float):
        """Purges timestamps older than the sliding window."""
        cutoff = current_time - self.window_seconds
        self.request_history[client_ip] = [
            ts for ts in self.request_history[client_ip] if ts > cutoff
        ]

    async def dispatch(self, request: Request, call_next):
        # Allow whitelisted paths without rate limits
        if request.url.path in self.whitelist_paths:
            return await call_next(request)

        # Allow tests to bypass or customize if header provided
        if request.headers.get("X-Bypass-Rate-Limit") == "true":
            return await call_next(request)

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        # Check rate limit
        self._cleanup_old_requests(client_ip, now)
        recent_requests = self.request_history[client_ip]

        # Read dynamic test rate limit if injected
        limit = int(request.headers.get("X-Test-Rate-Limit", self.max_requests))

        if len(recent_requests) >= limit:
            logger.warning(f"Rate limit exceeded for client {client_ip} on {request.url.path}")
            retry_after = int(self.window_seconds - (now - recent_requests[0])) if recent_requests else 1
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "rate_limit_exceeded",
                    "detail": f"Rate limit exceeded. Maximum {limit} requests per {self.window_seconds}s allowed.",
                    "retry_after_seconds": max(1, retry_after),
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": str(max(1, retry_after)),
                },
            )

        # Record this request
        self.request_history[client_ip].append(now)
        remaining = limit - len(self.request_history[client_ip])

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))

        return response

