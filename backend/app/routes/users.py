"""
User profile and preferences route blueprint (/api/users/*).
"""
from flask import Blueprint, request, g
from backend.app.schemas.user_schemas import ProfileUpdateSchema, PreferencesUpdateSchema
from backend.app.services.user_service import UserService
from backend.app.middleware.auth_middleware import require_auth
from backend.app.utils.responses import success_response, error_response

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

profile_update_schema = ProfileUpdateSchema()
preferences_update_schema = PreferencesUpdateSchema()


@users_bp.route("/profile", methods=["GET"])
@require_auth
def get_profile():
    """Get full user profile including preferences."""
    user = getattr(g, "current_user", None)
    profile = UserService.get_profile(user["user_id"])
    return success_response(data={"user": profile}, message="Profile loaded.")


@users_bp.route("/profile", methods=["PUT"])
@require_auth
def update_profile():
    """Update profile fields (full name, phone)."""
    user = getattr(g, "current_user", None)
    json_data = request.get_json(silent=True) or {}
    validated = profile_update_schema.load(json_data)

    try:
        updated = UserService.update_profile(
            user_id=user["user_id"],
            full_name=validated.get("full_name"),
            phone=validated.get("phone")
        )
        return success_response(data={"user": updated}, message="Profile updated successfully.")
    except ValueError as e:
        return error_response("UPDATE_FAILED", str(e), 400)


@users_bp.route("/preferences", methods=["GET"])
@require_auth
def get_preferences():
    """Get transit routing preferences."""
    user = getattr(g, "current_user", None)
    preferences = UserService.get_preferences(user["user_id"])
    return success_response(data={"preferences": preferences}, message="Preferences loaded.")


@users_bp.route("/preferences", methods=["PUT"])
@require_auth
def update_preferences():
    """Update transit routing preferences."""
    user = getattr(g, "current_user", None)
    json_data = request.get_json(silent=True) or {}
    validated = preferences_update_schema.load(json_data)

    updated = UserService.update_preferences(
        user_id=user["user_id"],
        preferred_mode=validated.get("preferred_mode"),
        route_preference=validated.get("route_preference"),
        max_walking_distance_m=validated.get("max_walking_distance_m"),
        avoid_taxi=validated.get("avoid_taxi"),
        avoid_transfers=validated.get("avoid_transfers")
    )
    return success_response(data={"preferences": updated}, message="Preferences updated successfully.")
