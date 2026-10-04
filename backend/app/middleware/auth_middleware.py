"""
Authentication and Role-Based Access Control (RBAC) middleware decorators.
"""
from functools import wraps
from typing import Callable, Optional
import jwt
from flask import request, g
from backend.app.models.user import UserModel
from backend.app.utils.jwt_utils import decode_access_token
from backend.app.utils.responses import error_response


def get_token_from_header() -> Optional[str]:
    """Extract Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        return None
    parts = auth_header.strip().split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def authenticate_request() -> Optional[dict]:
    """
    Attempt to authenticate current request via JWT.
    Returns user dict on success, None on absent or invalid token.
    """
    token = get_token_from_header()
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            return None
        user = UserModel.get_by_id(user_id)
        if not user or not user.get("is_active"):
            return None
        return user
    except (jwt.PyJWTError, Exception):
        return None


def require_auth(f: Callable) -> Callable:
    """Decorator requiring valid authenticated user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return error_response("MISSING_TOKEN", "Authentication token is required.", 401)
        try:
            payload = decode_access_token(token)
        except jwt.ExpiredSignatureError:
            return error_response("TOKEN_EXPIRED", "Authentication token has expired. Please log in again.", 401)
        except jwt.InvalidTokenError:
            return error_response("INVALID_TOKEN", "Invalid authentication token provided.", 401)

        user_id = payload.get("user_id") or payload.get("sub")
        user = UserModel.get_by_id(user_id)
        if not user:
            return error_response("USER_NOT_FOUND", "User account no longer exists.", 401)
        if not user.get("is_active"):
            return error_response("ACCOUNT_DISABLED", "This user account has been disabled.", 403)

        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def require_role(required_role: str) -> Callable:
    """Decorator requiring specific role (e.g. 'ADMIN')."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            current_user = getattr(g, "current_user", None)
            if not current_user or current_user.get("role") != required_role:
                return error_response(
                    "FORBIDDEN",
                    f"Administrator privileges are required for this action.",
                    403
                )
            return f(*args, **kwargs)
        return decorated
    return decorator


def optional_auth(f: Callable) -> Callable:
    """Decorator that attaches g.current_user if token present, but does not reject guests."""
    @wraps(f)
    def decorated(*args, **kwargs):
        g.current_user = authenticate_request()
        return f(*args, **kwargs)
    return decorated
