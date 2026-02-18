# src/api/middleware.py

"""
Custom middleware for the Real-Time Cyber Threat Detection and Response System.

Provides:
- Rate limiting
- Request ID tracking
- Request/Response logging
- Security headers
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse.
    Uses token bucket algorithm for rate limiting.
    """

    def __init__(self, app, requests_per_minute: int = 100, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_buckets = defaultdict(list)
        self.hour_buckets = defaultdict(list)
        self.lock = threading.Lock()

    def _clean_old_requests(self, client_id: str, now: datetime):
        """Remove requests older than the time window."""
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        with self.lock:
            self.minute_buckets[client_id] = [
                req_time for req_time in self.minute_buckets[client_id]
                if req_time > minute_ago
            ]
            self.hour_buckets[client_id] = [
                req_time for req_time in self.hour_buckets[client_id]
                if req_time > hour_ago
            ]

    def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client has exceeded rate limits."""
        now = datetime.now()
        self._clean_old_requests(client_id, now)

        with self.lock:
            minute_count = len(self.minute_buckets[client_id])
            hour_count = len(self.hour_buckets[client_id])

            if minute_count >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for client {client_id}: {minute_count} requests/minute")
                return True
            if hour_count >= self.requests_per_hour:
                logger.warning(f"Rate limit exceeded for client {client_id}: {hour_count} requests/hour")
                return True

            # Add current request
            self.minute_buckets[client_id].append(now)
            self.hour_buckets[client_id].append(now)
            return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request with rate limiting."""
        # Get client identifier (IP address or authenticated user)
        client_id = request.client.host if request.client else "unknown"

        # Check rate limit
        if self._is_rate_limited(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests. Please try again later.",
                    "details": f"Rate limit: {self.requests_per_minute}/min, {self.requests_per_hour}/hour"
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )

        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        with self.lock:
            remaining = self.requests_per_minute - len(self.minute_buckets[client_id])
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all incoming requests and outgoing responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client": request.client.host if request.client else "unknown"
            }
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        
        return response
