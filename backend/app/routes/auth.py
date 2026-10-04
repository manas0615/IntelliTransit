"""
Authentication route blueprint (/api/auth/*).
"""
from flask import Blueprint, request, g
from backend.app.schemas.auth_schemas import RegisterSchema, LoginSchema, PasswordChangeSchema
from backend.app.services.auth_service import AuthService
from backend.app.middleware.auth_middleware import require_auth
from backend.app.utils.responses import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()
password_change_schema = PasswordChangeSchema()


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user account."""
    json_data = request.get_json(silent=True) or {}
    validated_data = register_schema.load(json_data)

    success, result, message = AuthService.register(
        full_name=validated_data["full_name"],
        email=validated_data["email"],
        password=validated_data["password"],
        phone=validated_data.get("phone")
    )
    if not success:
        return error_response(result.get("code", "REGISTRATION_FAILED"), message, 409)

    return success_response(data=result, message=message, status_code=201)


@auth_bp.route("/login", methods=["POST"])
def login():
    """Log in user and return JWT access token."""
    json_data = request.get_json(silent=True) or {}
    validated_data = login_schema.load(json_data)

    success, result, message = AuthService.login(
        email=validated_data["email"],
        password=validated_data["password"]
    )
    if not success:
        return error_response(result.get("code", "LOGIN_FAILED"), message, 401)

    return success_response(data=result, message=message, status_code=200)


@auth_bp.route("/me", methods=["GET"])
@require_auth
def get_current_user_profile():
    """Return currently authenticated user information."""
    user = getattr(g, "current_user", None)
    return success_response(data={"user": user}, message="User profile retrieved.")


@auth_bp.route("/change-password", methods=["POST"])
@require_auth
def change_password():
    """Change authenticated user password."""
    user = getattr(g, "current_user", None)
    json_data = request.get_json(silent=True) or {}
    validated = password_change_schema.load(json_data)

    success, message = AuthService.change_password(
        user_id=user["user_id"],
        current_password=validated["current_password"],
        new_password=validated["new_password"]
    )
    if not success:
        return error_response("PASSWORD_CHANGE_FAILED", message, 400)

    return success_response(data={}, message=message, status_code=200)
