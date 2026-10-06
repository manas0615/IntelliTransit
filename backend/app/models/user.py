"""
User Model - Direct parameterized SQL for users table.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class UserModel:
    """Encapsulates CRUD operations for the users table."""

    @staticmethod
    def _enrich_user(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not user:
            return None
        if not user.get("account_type"):
            role = user.get("role", "USER")
            email = (user.get("email") or "").lower()
            if role == "ADMIN":
                user["account_type"] = "CONDUCTOR" if "conductor" in email else "ADMINISTRATOR"
            else:
                user["account_type"] = "COMMUTER"
        return user

    @staticmethod
    def create(full_name: str, email: str, password_hash: str, phone: Optional[str] = None, role: str = "USER", account_type: Optional[str] = None) -> Dict[str, Any]:
        """Create a new user and return the inserted row."""
        if not account_type:
            account_type = "COMMUTER" if role == "USER" else ("CONDUCTOR" if "conductor" in email.lower() else "ADMINISTRATOR")
        query = """
            INSERT INTO users (full_name, email, phone, password_hash, role, account_type, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            RETURNING user_id, full_name, email, phone, role, account_type, is_active, created_at, updated_at;
        """
        row = fetch_one(query, (full_name, email.lower().strip(), phone, password_hash, role, account_type))
        return UserModel._enrich_user(row)

    @staticmethod
    def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by UUID."""
        query = """
            SELECT user_id, full_name, email, phone, role, account_type, is_active, created_at, updated_at
            FROM users
            WHERE user_id = %s;
        """
        row = fetch_one(query, (user_id,))
        return UserModel._enrich_user(row)

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user with password_hash by email."""
        query = """
            SELECT user_id, full_name, email, phone, password_hash, role, account_type, is_active, created_at, updated_at
            FROM users
            WHERE LOWER(email) = LOWER(%s);
        """
        row = fetch_one(query, (email.strip(),))
        return UserModel._enrich_user(row)

    @staticmethod
    def get_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by phone number."""
        query = """
            SELECT user_id, full_name, email, phone, role, account_type, is_active, created_at, updated_at
            FROM users
            WHERE phone = %s;
        """
        row = fetch_one(query, (phone.strip(),))
        return UserModel._enrich_user(row)

    @staticmethod
    def update_profile(user_id: str, full_name: Optional[str] = None, phone: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update user profile fields."""
        query = """
            UPDATE users
            SET full_name = COALESCE(%s, full_name),
                phone = COALESCE(%s, phone),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, full_name, email, phone, role, account_type, is_active, created_at, updated_at;
        """
        row = fetch_one(query, (full_name, phone, user_id))
        return UserModel._enrich_user(row)

    @staticmethod
    def update_password(user_id: str, password_hash: str) -> bool:
        """Update user password hash."""
        query = """
            UPDATE users
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s;
        """
        return execute_query(query, (password_hash, user_id)) > 0

    @staticmethod
    def update_role(user_id: str, role: str) -> Optional[Dict[str, Any]]:
        """Update user role (USER, ADMIN)."""
        clean_role = role.upper().strip()
        query = """
            UPDATE users
            SET role = %s,
                account_type = CASE WHEN %s = 'ADMIN' AND (account_type IS NULL OR account_type = 'COMMUTER') THEN 'ADMINISTRATOR'
                                    WHEN %s = 'USER' THEN 'COMMUTER'
                                    ELSE account_type END,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, full_name, email, phone, role, account_type, is_active, created_at, updated_at;
        """
        row = fetch_one(query, (clean_role, clean_role, clean_role, user_id))
        return UserModel._enrich_user(row)

    @staticmethod
    def set_active_status(user_id: str, is_active: bool) -> bool:
        """Activate or deactivate user account (Admin)."""
        query = """
            UPDATE users
            SET is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s;
        """
        return execute_query(query, (is_active, user_id)) > 0

    @staticmethod
    def list_all(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List all users with pagination for admin."""
        query = """
            SELECT user_id, full_name, email, phone, role, account_type, is_active, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s;
        """
        rows = fetch_all(query, (limit, offset))
        return [UserModel._enrich_user(r) for r in rows]

    @staticmethod
    def count() -> int:
        """Count total users."""
        res = fetch_one("SELECT COUNT(*) AS total FROM users;")
        return res["total"] if res else 0
