"""
Saved locations route blueprint (/api/users/locations/*).
"""
from flask import Blueprint, request, g
from backend.app.schemas.user_schemas import SavedLocationCreateSchema, SavedLocationUpdateSchema
from backend.app.services.user_service import UserService
from backend.app.middleware.auth_middleware import require_auth
from backend.app.utils.responses import success_response, error_response

locations_bp = Blueprint("locations", __name__, url_prefix="/api/users/locations")

create_location_schema = SavedLocationCreateSchema()
update_location_schema = SavedLocationUpdateSchema()


@locations_bp.route("", methods=["GET"])
@require_auth
def list_locations():
    """List all saved locations for the authenticated user."""
    user = getattr(g, "current_user", None)
    locations = UserService.list_saved_locations(user["user_id"])
    return success_response(data={"locations": locations}, message="Locations loaded.")


@locations_bp.route("", methods=["POST"])
@require_auth
def create_location():
    """Create a new saved location."""
    user = getattr(g, "current_user", None)
    json_data = request.get_json(silent=True) or {}
    validated = create_location_schema.load(json_data)

    try:
        location = UserService.create_saved_location(
            user_id=user["user_id"],
            label=validated["label"],
            location_name=validated["location_name"],
            latitude=validated["latitude"],
            longitude=validated["longitude"],
            address=validated.get("address")
        )
        return success_response(data={"location": location}, message="Location saved.", status_code=201)
    except ValueError as e:
        return error_response("LIMIT_REACHED", str(e), 400)


@locations_bp.route("/<string:location_id>", methods=["PUT"])
@require_auth
def update_location(location_id: str):
    """Update an existing saved location."""
    user = getattr(g, "current_user", None)
    json_data = request.get_json(silent=True) or {}
    validated = update_location_schema.load(json_data)

    updated = UserService.update_saved_location(
        location_id=location_id,
        user_id=user["user_id"],
        label=validated.get("label"),
        location_name=validated.get("location_name"),
        address=validated.get("address"),
        latitude=validated.get("latitude"),
        longitude=validated.get("longitude")
    )
    if not updated:
        return error_response("NOT_FOUND", "Saved location not found or permission denied.", 404)

    return success_response(data={"location": updated}, message="Location updated.")


@locations_bp.route("/<string:location_id>", methods=["DELETE"])
@require_auth
def delete_location(location_id: str):
    """Delete a saved location."""
    user = getattr(g, "current_user", None)
    success = UserService.delete_saved_location(location_id, user["user_id"])
    if not success:
        return error_response("NOT_FOUND", "Saved location not found or permission denied.", 404)

    return success_response(data={}, message="Location deleted successfully.")
