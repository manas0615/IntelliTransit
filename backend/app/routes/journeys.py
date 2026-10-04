"""
Journey planning route blueprint (/api/journeys/*).
"""
from flask import Blueprint, request, g
from backend.app.schemas.journey_schemas import PlanJourneyRequestSchema
from backend.app.services.journey_service import JourneyService
from backend.app.middleware.auth_middleware import optional_auth, require_auth
from backend.app.utils.validators import parse_pagination
from backend.app.utils.responses import success_response, error_response

journeys_bp = Blueprint("journeys", __name__, url_prefix="/api/journeys")

plan_journey_schema = PlanJourneyRequestSchema()


@journeys_bp.route("/plan", methods=["POST"])
@optional_auth
def plan_journey():
    """
    Plan multimodal journey (Open to both Guests and Authenticated Users).
    """
    json_data = request.get_json(silent=True) or {}
    validated = plan_journey_schema.load(json_data)

    current_user = getattr(g, "current_user", None)
    user_id = current_user["user_id"] if current_user else None

    try:
        result = JourneyService.plan_journey(
            origin_data=validated["origin"],
            destination_data=validated["destination"],
            user_id=user_id,
            preferences_input=validated.get("preferences"),
            departure_time=validated.get("departure_time")
        )
        return success_response(data=result, message="Journey itineraries calculated successfully.")
    except ValueError as e:
        return error_response("PLANNING_ERROR", str(e), 400)


@journeys_bp.route("", methods=["GET"])
@require_auth
def list_journey_history():
    """List authenticated user's past saved journeys."""
    user = getattr(g, "current_user", None)
    limit, offset = parse_pagination(request.args.get("limit"), request.args.get("offset"))

    history = JourneyService.list_user_journeys(user["user_id"], limit=limit, offset=offset)
    return success_response(data={"journeys": history}, message="Journey history loaded.")


@journeys_bp.route("/<string:journey_id>", methods=["GET"])
@optional_auth
def get_journey_details(journey_id: str):
    """Get specific journey details and leg breakdown."""
    current_user = getattr(g, "current_user", None)
    user_id = current_user["user_id"] if current_user else None

    journey = JourneyService.get_journey_by_id(journey_id, user_id=user_id)
    if not journey:
        return error_response("NOT_FOUND", "Journey record not found or access denied.", 404)

    return success_response(data={"journey": journey}, message="Journey details loaded.")
