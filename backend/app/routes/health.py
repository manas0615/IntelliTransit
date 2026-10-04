"""
Health check route blueprint.
"""
from flask import Blueprint
from backend.app.models.db import check_db_health
from backend.app.utils.responses import success_response, error_response

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health_check():
    """System health check endpoint."""
    db_ok = check_db_health()
    otp_status = "OFFLINE"
    try:
        import requests
        from backend.app.config import Config
        r = requests.get(f"{Config.OTP_BASE_URL}/otp/routers/{Config.OTP_ROUTER_ID}", timeout=1)
        if r.status_code == 200:
            otp_status = "ONLINE"
    except Exception:
        otp_status = "OFFLINE"

    if db_ok:
        return success_response(
            data={
                "status": "healthy",
                "database": "connected",
                "otp": otp_status,
                "service": "IntelliTransit Backend API",
                "version": "1.0.0"
            },
            message="System is healthy and operational."
        )
    return error_response(
        code="DATABASE_UNAVAILABLE",
        message="Database connection check failed.",
        status_code=503,
        details={"database": "disconnected"}
    )
