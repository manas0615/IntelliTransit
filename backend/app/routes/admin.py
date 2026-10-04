"""
IntelliTransit Admin Routes.
Protected administrative endpoints for system metrics, user role administration, and fare management.
"""
from flask import Blueprint, request, g
from backend.app.services.admin_service import AdminService
from backend.app.middleware.auth_middleware import require_role
from backend.app.utils.validators import parse_pagination
from backend.app.utils.responses import success_response, error_response

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/metrics", methods=["GET"])
@admin_bp.route("/overview", methods=["GET"])
@require_role("ADMIN")
def get_metrics():
    """Retrieve system-wide aggregated metrics."""
    metrics = AdminService.get_system_metrics()
    return success_response(data=metrics, message="System metrics retrieved.")


@admin_bp.route("/users", methods=["GET"])
@require_role("ADMIN")
def list_users():
    """List platform users."""
    limit, offset = parse_pagination(request.args.get("limit"), request.args.get("offset"))
    users = AdminService.list_users(limit=limit, offset=offset)
    return success_response(data={"users": users}, message="Users list retrieved.")


@admin_bp.route("/users/<string:user_id>/status", methods=["PUT"])
@require_role("ADMIN")
def update_user_status(user_id: str):
    """Toggle user active status (suspend/reactivate)."""
    data = request.get_json(silent=True) or {}
    is_active = data.get("is_active")
    if is_active is None:
        return error_response("VALIDATION_ERROR", "is_active boolean field is required.", 400)

    updated = AdminService.update_user_status(user_id, bool(is_active))
    if not updated:
        return error_response("NOT_FOUND", "User not found.", 404)

    return success_response(data=updated, message=f"User status updated to {'Active' if is_active else 'Suspended'}.")


@admin_bp.route("/users/<string:user_id>/role", methods=["PUT"])
@require_role("ADMIN")
def update_user_role(user_id: str):
    """Update user role (USER, ADMIN)."""
    data = request.get_json(silent=True) or {}
    role = data.get("role")
    if not role:
        return error_response("VALIDATION_ERROR", "role field is required.", 400)

    try:
        updated = AdminService.update_user_role(user_id, role)
        if not updated:
            return error_response("NOT_FOUND", "User not found.", 404)
        return success_response(data=updated, message=f"User role updated to {role}.")
    except ValueError as e:
        return error_response("VALIDATION_ERROR", str(e), 400)


@admin_bp.route("/services", methods=["GET"])
@require_role("ADMIN")
def list_services():
    """List transport services."""
    services = AdminService.list_transport_services()
    return success_response(data={"services": services}, message="Transport services retrieved.")


@admin_bp.route("/fares", methods=["GET"])
@require_role("ADMIN")
def list_fares():
    """List active fare rules."""
    fares = AdminService.list_fare_configurations()
    return success_response(data={"fares": fares}, message="Fare configurations retrieved.")


@admin_bp.route("/fares/<string:fare_id>", methods=["PUT"])
@require_role("ADMIN")
def update_fare(fare_id: str):
    """Update base fare, per km rate, or min fare for a transit service."""
    data = request.get_json(silent=True) or {}
    base_fare = data.get("base_fare")
    per_km_rate = data.get("per_km_rate")
    min_fare = data.get("min_fare")

    updated = AdminService.update_fare_configuration(
        fare_id=fare_id,
        base_fare=float(base_fare) if base_fare is not None else None,
        per_km_rate=float(per_km_rate) if per_km_rate is not None else None,
        min_fare=float(min_fare) if min_fare is not None else None
    )

    if not updated:
        return error_response("NOT_FOUND", "Fare configuration not found.", 404)

    return success_response(data=updated, message="Fare configuration updated.")


@admin_bp.route("/validations", methods=["GET"])
@require_role("ADMIN")
def list_validations():
    """List recent validation audit logs."""
    limit, _ = parse_pagination(request.args.get("limit"), request.args.get("offset"))
    validations = AdminService.get_recent_validations(limit=limit)
    return success_response(data={"validations": validations}, message="Validations log retrieved.")
