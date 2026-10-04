"""
Request/response logging and security headers middleware.
"""
import time
import logging
from flask import Flask, request, g, Response

logger = logging.getLogger("intellitransit.access")


def register_request_logging(app: Flask) -> None:
    """Register before and after request hooks for latency tracking and security headers."""

    @app.before_request
    def start_timer():
        g.request_start_time = time.time()

    @app.after_request
    def log_and_secure(response: Response) -> Response:
        duration_ms = 0.0
        if hasattr(g, "request_start_time"):
            duration_ms = (time.time() - g.request_start_time) * 1000.0

        # Log request summary
        logger.info(
            "%s %s %d %.2fms (IP: %s)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            request.remote_addr
        )

        # Security Headers (Workstream B / Security Strategy)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy (allows MapLibre CDN, local scripts, OpenStreetMap tiles, blob workers)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https://*.tile.openstreetmap.org https://tile.openstreetmap.org https://unpkg.com; "
            "connect-src 'self' https://*.tile.openstreetmap.org https://tile.openstreetmap.org https://unpkg.com blob: data:; "
            "worker-src 'self' blob:; "
            "child-src 'self' blob:; "
            "frame-src 'none'; "
            "object-src 'none';"
        )

        return response
