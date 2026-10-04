"""
Passes route blueprint (/api/passes/*).
"""
from flask import Blueprint, request, g
from backend.app.schemas.ticket_schemas import CreatePassRequestSchema
from backend.app.services.pass_service import PassService
from backend.app.middleware.auth_middleware import require_auth
from backend.app.utils.validators import parse_pagination
from backend.app.utils.responses import success_response, error_response

passes_bp = Blueprint("passes", __name__, url_prefix="/api/passes")

create_pass_schema = CreatePassRequestSchema()


@passes_bp.route("", methods=["POST"])
@require_auth
def create_pass():
    """Create a periodic transit pass (DAILY, WEEKLY, MONTHLY)."""
    user = getattr(g, "current_user", None)
    json_data = request.get_json(silent=True) or {}
    validated = create_pass_schema.load(json_data)

    success, result, message = PassService.create_pass(
        user_id=user["user_id"],
        pass_type=validated["pass_type"]
    )
    if not success:
        return error_response(result.get("code", "CREATION_FAILED"), message, 400)

    return success_response(data=result, message=message, status_code=201)


@passes_bp.route("", methods=["GET"])
@require_auth
def list_passes():
    """List passes for the authenticated user."""
    user = getattr(g, "current_user", None)
    status_filter = request.args.get("status")
    limit, offset = parse_pagination(request.args.get("limit"), request.args.get("offset"))

    passes = PassService.list_user_passes(user["user_id"], status=status_filter, limit=limit, offset=offset)
    return success_response(data={"passes": passes}, message="Passes loaded.")


@passes_bp.route("/<string:pass_id>", methods=["GET"])
@require_auth
def get_pass(pass_id: str):
    """Get pass details."""
    user = getattr(g, "current_user", None)
    p = PassService.get_pass_details(pass_id, user["user_id"])
    if not p:
        return error_response("NOT_FOUND", "Pass not found or access denied.", 404)

    return success_response(data={"pass": p}, message="Pass details loaded.")


@passes_bp.route("/<string:pass_id>/cancel", methods=["PUT"])
@require_auth
def cancel_pass(pass_id: str):
    """Cancel pass if eligible."""
    user = getattr(g, "current_user", None)
    success, cancelled, message = PassService.cancel_pass(pass_id, user["user_id"])
    if not success:
        return error_response("CANCELLATION_FAILED", message, 400)

    return success_response(data={"pass": cancelled}, message=message)
