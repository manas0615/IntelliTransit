"""
Ticket & Pass Validation Routes.
Endpoints for scanning QR tokens, generating QR payloads, and viewing audit logs.
"""
from flask import Blueprint, request, g, jsonify
from backend.app.services.validation_service import ValidationService
from backend.app.services.qr_service import QRService
from backend.app.models.ticket import TicketModel
from backend.app.models.pass_model import PassModel
from backend.app.middleware.auth_middleware import require_auth
from backend.app.utils.validators import parse_pagination
from backend.app.utils.responses import success_response, error_response

validation_bp = Blueprint("validation", __name__, url_prefix="/api")


@validation_bp.route("/validation/validate", methods=["POST"])
@validation_bp.route("/validation/tickets", methods=["POST"])
@require_auth
def validate_token():
    """
    Validate a ticket or pass token scanned by conductor/gate scanner.
    Body:
      {
        "token": "TKT-..." | "PASS-..." | "uuid",
        "remarks": "Gate 1 entry" (optional)
      }
    """
    user = getattr(g, "current_user", None)
    data = request.get_json(silent=True) or {}
    token_str = data.get("token") or data.get("ticket_token") or data.get("qr_code")

    if not token_str:
        return error_response("VALIDATION_ERROR", "Token is required for validation.", 400)

    remarks = data.get("remarks")
    success, result, message = ValidationService.validate_token(
        validator_user_id=user["user_id"],
        token_str=token_str,
        remarks=remarks
    )

    if not success:
        return error_response(result.get("code", "VALIDATION_FAILED"), message, 400, details=result)

    return success_response(data=result, message=message, status_code=200)


@validation_bp.route("/tickets/<string:ticket_id>/qr", methods=["GET"])
@validation_bp.route("/validation/tickets/<string:ticket_id>/qr", methods=["GET"])
@require_auth
def get_ticket_qr(ticket_id: str):
    """
    Generate and return QR code data URI for a ticket.
    """
    user = getattr(g, "current_user", None)
    ticket = TicketModel.get_by_id(ticket_id)
    if not ticket:
        return error_response("NOT_FOUND", "Ticket not found.", 404)

    # Only owner or admin can view ticket QR
    if ticket["user_id"] != user["user_id"] and user.get("role") != "ADMIN":
        return error_response("FORBIDDEN", "Access denied to this ticket.", 403)

    token = ticket["ticket_token"] or ticket["ticket_id"]
    qr_data_uri = QRService.generate_qr_data_uri(token)

    return success_response(data={
        "ticket_id": ticket_id,
        "ticket_token": token,
        "status": ticket["status"],
        "qr_data_uri": qr_data_uri
    }, message="Ticket QR code generated.")


@validation_bp.route("/passes/<string:pass_id>/qr", methods=["GET"])
@validation_bp.route("/validation/passes/<string:pass_id>/qr", methods=["GET"])
@require_auth
def get_pass_qr(pass_id: str):
    """
    Generate and return QR code data URI for a transit pass.
    """
    user = getattr(g, "current_user", None)
    pass_item = PassModel.get_by_id(pass_id)
    if not pass_item:
        return error_response("NOT_FOUND", "Pass not found.", 404)

    if pass_item["user_id"] != user["user_id"] and user.get("role") != "ADMIN":
        return error_response("FORBIDDEN", "Access denied to this pass.", 403)

    token = pass_item.get("pass_token") or pass_item["pass_id"]
    qr_data_uri = QRService.generate_qr_data_uri(token)

    return success_response(data={
        "pass_id": pass_id,
        "pass_token": token,
        "status": pass_item["status"],
        "qr_data_uri": qr_data_uri
    }, message="Pass QR code generated.")


@validation_bp.route("/validation/history", methods=["GET"])
@require_auth
def list_validation_history():
    """List recent validation audit events."""
    limit, _ = parse_pagination(request.args.get("limit"), request.args.get("offset"))
    events = ValidationService.get_recent_validations(limit=limit)
    return success_response(data={"validations": events}, message="Validation audit events loaded.")
