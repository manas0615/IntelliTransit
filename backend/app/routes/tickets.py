"""
Tickets route blueprint (/api/tickets/*).
"""
from flask import Blueprint, request, g
from backend.app.schemas.ticket_schemas import CreateTicketRequestSchema
from backend.app.services.ticket_service import TicketService
from backend.app.middleware.auth_middleware import require_auth
from backend.app.utils.validators import parse_pagination
from backend.app.utils.responses import success_response, error_response

tickets_bp = Blueprint("tickets", __name__, url_prefix="/api/tickets")

create_ticket_schema = CreateTicketRequestSchema()


@tickets_bp.route("", methods=["POST"])
@require_auth
def create_ticket():
    """Create a ticket for a specific ticketable journey leg."""
    user = getattr(g, "current_user", None)
    json_data = request.get_json(silent=True) or {}
    validated = create_ticket_schema.load(json_data)

    success, result, message = TicketService.create_ticket(
        user_id=user["user_id"],
        journey_id=str(validated["journey_id"]),
        journey_leg_id=str(validated["journey_leg_id"])
    )
    if not success:
        return error_response(result.get("code", "CREATION_FAILED"), message, 400)

    return success_response(data=result, message=message, status_code=201)


@tickets_bp.route("", methods=["GET"])
@require_auth
def list_tickets():
    """List tickets for the current authenticated user."""
    user = getattr(g, "current_user", None)
    status_filter = request.args.get("status")
    limit, offset = parse_pagination(request.args.get("limit"), request.args.get("offset"))

    tickets = TicketService.list_user_tickets(user["user_id"], status=status_filter, limit=limit, offset=offset)
    return success_response(data={"tickets": tickets}, message="Tickets loaded.")


@tickets_bp.route("/<string:ticket_id>", methods=["GET"])
@require_auth
def get_ticket(ticket_id: str):
    """Retrieve ticket details."""
    user = getattr(g, "current_user", None)
    ticket = TicketService.get_ticket_details(ticket_id, user["user_id"])
    if not ticket:
        return error_response("NOT_FOUND", "Ticket not found or access denied.", 404)

    return success_response(data={"ticket": ticket}, message="Ticket details loaded.")


@tickets_bp.route("/<string:ticket_id>/cancel", methods=["PUT"])
@require_auth
def cancel_ticket(ticket_id: str):
    """Cancel ticket and initiate refund if eligible."""
    user = getattr(g, "current_user", None)
    success, cancelled, message = TicketService.cancel_ticket(ticket_id, user["user_id"])
    if not success:
        return error_response("CANCELLATION_FAILED", message, 400)

    return success_response(data={"ticket": cancelled}, message=message)
