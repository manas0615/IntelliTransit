"""
In-memory rate limiting middleware for single-machine academic deployment.
Uses a thread-safe sliding timestamp window per remote IP.
"""
import time
import threading
from typing import Dict, List
from flask import Flask, request, abort


class InMemoryRateLimiter:
    """Thread-safe sliding window in-memory rate limiter."""

    def __init__(self, default_limit_per_min: int = 60):
        self.default_limit = default_limit_per_min
        self.requests: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def is_allowed(self, key: str, limit: int = None, window_seconds: int = 60) -> bool:
        """Check if request from key is within allowable threshold."""
        effective_limit = limit if limit is not None else self.default_limit
        now = time.time()
        cutoff = now - window_seconds

        with self.lock:
            timestamps = self.requests.get(key, [])
            # Purge timestamps outside sliding window
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= effective_limit:
                self.requests[key] = timestamps
                return False

            timestamps.append(now)
            self.requests[key] = timestamps
            return True


# Global rate limiter instance
limiter = InMemoryRateLimiter()


def register_rate_limiter(app: Flask) -> None:
    """Apply rate limiting check on /api/ endpoints."""
    limit_per_min = app.config.get("RATE_LIMIT_PER_MINUTE", 60)
    limiter.default_limit = limit_per_min

    @app.before_request
    def check_rate_limit():
        if app.config.get("TESTING"):
            return  # Skip strict rate limits during unit tests

        if request.path.startswith("/api/") and request.method != "OPTIONS":
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
            
            # Auth endpoints have tighter limit: 20 per minute
            limit = 20 if request.path.startswith("/api/auth/") else limit_per_min

            if not limiter.is_allowed(client_ip, limit=limit, window_seconds=60):
                abort(429)
