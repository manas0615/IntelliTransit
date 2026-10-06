"""
Authentication service layer managing password hashing, registration, and token lifecycle.
"""
from typing import Any, Dict, Optional, Tuple
import bcrypt
from backend.app.models.user import UserModel
from backend.app.models.user_preference import UserPreferenceModel
from backend.app.utils.jwt_utils import create_access_token


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with work factor 12."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


class AuthService:
    """Business logic service for user authentication."""

    @staticmethod
    def register(full_name: str, email: str, password: str, phone: Optional[str] = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        Register a new user account and initialize default preferences.
        Returns (success, user_data_or_error_dict, message).
        """
        clean_email = email.lower().strip()
        if UserModel.get_by_email(clean_email):
            return False, {"code": "EMAIL_EXISTS", "field": "email"}, "An account with this email already exists."

        if phone:
            clean_phone = phone.strip()
            if UserModel.get_by_phone(clean_phone):
                return False, {"code": "PHONE_EXISTS", "field": "phone"}, "An account with this phone number already exists."
        else:
            clean_phone = None

        pw_hash = hash_password(password)
        user = UserModel.create(
            full_name=full_name.strip(),
            email=clean_email,
            password_hash=pw_hash,
            phone=clean_phone,
            role="USER"
        )

        # Initialize default user preferences
        UserPreferenceModel.create_or_update(
            user_id=user["user_id"],
            preferred_mode=None,
            route_preference="FASTEST",
            max_walking_distance_m=1500,
            avoid_taxi=False,
            avoid_transfers=False
        )

        token = create_access_token(user["user_id"], user["role"], user["email"], user.get("account_type"))
        result_data = {
            "user": {
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "phone": user["phone"],
                "role": user["role"],
                "account_type": user.get("account_type", "COMMUTER")
            },
            "token": token
        }
        return True, result_data, "Registration successful."

    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Authenticate user credentials and issue JWT access token.
        Returns (success, result_dict, message).
        """
        clean_email = email.lower().strip()
        user = UserModel.get_by_email(clean_email)
        if not user:
            return False, {"code": "INVALID_CREDENTIALS"}, "Invalid email or password."

        if not user.get("is_active"):
            return False, {"code": "ACCOUNT_DISABLED"}, "Your account has been deactivated. Please contact support."

        if not verify_password(password, user["password_hash"]):
            return False, {"code": "INVALID_CREDENTIALS"}, "Invalid email or password."

        token = create_access_token(user["user_id"], user["role"], user["email"], user.get("account_type"))
        result_data = {
            "user": {
                "user_id": user["user_id"],
                "full_name": user["full_name"],
                "email": user["email"],
                "phone": user["phone"],
                "role": user["role"],
                "account_type": user.get("account_type", "COMMUTER")
            },
            "token": token
        }
        return True, result_data, "Login successful."

    @staticmethod
    def change_password(user_id: str, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Verify current password and apply new bcrypt hash."""
        user = UserModel.get_by_id(user_id)
        if not user:
            return False, "User not found."

        # Fetch with password_hash
        full_user = UserModel.get_by_email(user["email"])
        if not verify_password(current_password, full_user["password_hash"]):
            return False, "Current password is incorrect."

        new_hash = hash_password(new_password)
        UserModel.update_password(user_id, new_hash)
        return True, "Password changed successfully."
