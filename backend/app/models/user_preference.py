"""
UserPreference Model - Direct parameterized SQL for user_preferences table (1:1 with users).
"""
from typing import Any, Dict, Optional
from backend.app.models.db import fetch_one, execute_query


class UserPreferenceModel:
    """Encapsulates CRUD operations for the user_preferences table."""

    @staticmethod
    def create_or_update(
        user_id: str,
        preferred_mode: Optional[str] = None,
        route_preference: Optional[str] = "FASTEST",
        max_walking_distance_m: Optional[int] = 1500,
        avoid_taxi: bool = False,
        avoid_transfers: bool = False
    ) -> Dict[str, Any]:
        """Upsert user preferences for the given user_id."""
        query = """
            INSERT INTO user_preferences (user_id, preferred_mode, route_preference, max_walking_distance_m, avoid_taxi, avoid_transfers, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) DO UPDATE
            SET preferred_mode = EXCLUDED.preferred_mode,
                route_preference = EXCLUDED.route_preference,
                max_walking_distance_m = EXCLUDED.max_walking_distance_m,
                avoid_taxi = EXCLUDED.avoid_taxi,
                avoid_transfers = EXCLUDED.avoid_transfers,
                updated_at = CURRENT_TIMESTAMP
            RETURNING preference_id, user_id, preferred_mode, route_preference, max_walking_distance_m, avoid_taxi, avoid_transfers, updated_at;
        """
        return fetch_one(query, (user_id, preferred_mode, route_preference, max_walking_distance_m, avoid_taxi, avoid_transfers))

    @staticmethod
    def get_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve preferences by user UUID."""
        query = """
            SELECT preference_id, user_id, preferred_mode, route_preference, max_walking_distance_m, avoid_taxi, avoid_transfers, updated_at
            FROM user_preferences
            WHERE user_id = %s;
        """
        return fetch_one(query, (user_id,))
