"""
User Model - Direct parameterized SQL for users table.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class UserModel:
    """Encapsulates CRUD operations for the users table."""

    @staticmethod
    def create(full_name: str, email: str, password_hash: str, phone: Optional[str] = None, role: str = "USER") -> Dict[str, Any]:
        """Create a new user and return the inserted row."""
        query = """
            INSERT INTO users (full_name, email, phone, password_hash, role, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING user_id, full_name, email, phone, role, is_active, created_at, updated_at;
        """
        return fetch_one(query, (full_name, email.lower().strip(), phone, password_hash, role))

    @staticmethod
    def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by UUID."""
        query = """
            SELECT user_id, full_name, email, phone, role, is_active, created_at, updated_at
            FROM users
            WHERE user_id = %s;
        """
        return fetch_one(query, (user_id,))

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Retrieve user with password_hash by email."""
        query = """
            SELECT user_id, full_name, email, phone, password_hash, role, is_active, created_at, updated_at
            FROM users
            WHERE LOWER(email) = LOWER(%s);
        """
        return fetch_one(query, (email.strip(),))

    @staticmethod
    def get_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """Retrieve user by phone number."""
        query = """
            SELECT user_id, full_name, email, phone, role, is_active, created_at, updated_at
            FROM users
            WHERE phone = %s;
        """
        return fetch_one(query, (phone.strip(),))

    @staticmethod
    def update_profile(user_id: str, full_name: Optional[str] = None, phone: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update user profile fields."""
        query = """
            UPDATE users
            SET full_name = COALESCE(%s, full_name),
                phone = COALESCE(%s, phone),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, full_name, email, phone, role, is_active, created_at, updated_at;
        """
        return fetch_one(query, (full_name, phone, user_id))

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
        query = """
            UPDATE users
            SET role = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, full_name, email, phone, role, is_active, created_at, updated_at;
        """
        return fetch_one(query, (role, user_id))

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
            SELECT user_id, full_name, email, phone, role, is_active, created_at, updated_at
            FROM users
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s;
        """
        return fetch_all(query, (limit, offset))

    @staticmethod
    def count() -> int:
        """Count total users."""
        res = fetch_one("SELECT COUNT(*) AS total FROM users;")
        return res["total"] if res else 0
