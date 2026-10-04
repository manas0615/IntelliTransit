"""
SavedLocation Model - Direct parameterized SQL for saved_locations table (1:N with users).
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class SavedLocationModel:
    """Encapsulates CRUD operations for the saved_locations table."""

    @staticmethod
    def create(
        user_id: str,
        label: str,
        location_name: str,
        latitude: float,
        longitude: float,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new saved location for a user."""
        query = """
            INSERT INTO saved_locations (user_id, label, location_name, address, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING location_id, user_id, label, location_name, address, latitude, longitude, created_at, updated_at;
        """
        return fetch_one(query, (user_id, label, location_name, address, latitude, longitude))

    @staticmethod
    def get_by_id(location_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a saved location by ID."""
        query = """
            SELECT location_id, user_id, label, location_name, address, latitude, longitude, created_at, updated_at
            FROM saved_locations
            WHERE location_id = %s;
        """
        return fetch_one(query, (location_id,))

    @staticmethod
    def list_by_user_id(user_id: str) -> List[Dict[str, Any]]:
        """List all saved locations for a specific user."""
        query = """
            SELECT location_id, user_id, label, location_name, address, latitude, longitude, created_at, updated_at
            FROM saved_locations
            WHERE user_id = %s
            ORDER BY created_at ASC;
        """
        return fetch_all(query, (user_id,))

    @staticmethod
    def update(
        location_id: str,
        user_id: str,
        label: Optional[str] = None,
        location_name: Optional[str] = None,
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a saved location ensuring user ownership."""
        query = """
            UPDATE saved_locations
            SET label = COALESCE(%s, label),
                location_name = COALESCE(%s, location_name),
                address = COALESCE(%s, address),
                latitude = COALESCE(%s, latitude),
                longitude = COALESCE(%s, longitude),
                updated_at = CURRENT_TIMESTAMP
            WHERE location_id = %s AND user_id = %s
            RETURNING location_id, user_id, label, location_name, address, latitude, longitude, created_at, updated_at;
        """
        return fetch_one(query, (label, location_name, address, latitude, longitude, location_id, user_id))

    @staticmethod
    def delete(location_id: str, user_id: str) -> bool:
        """Delete a saved location ensuring user ownership."""
        query = """
            DELETE FROM saved_locations
            WHERE location_id = %s AND user_id = %s;
        """
        return execute_query(query, (location_id, user_id)) > 0
