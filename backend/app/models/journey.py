"""
Journey Model - Direct parameterized SQL for journeys table.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class JourneyModel:
    """Encapsulates CRUD operations for the journeys table."""

    @staticmethod
    def create(
        origin_name: str,
        origin_latitude: float,
        origin_longitude: float,
        destination_name: str,
        destination_latitude: float,
        destination_longitude: float,
        user_id: Optional[str] = None,
        departure_time: Optional[str] = None,
        arrival_time: Optional[str] = None,
        total_duration_min: Optional[int] = None,
        walking_distance_m: Optional[int] = None,
        estimated_fare: Optional[float] = None,
        route_type: Optional[str] = "MULTIMODAL",
        otp_itinerary_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new journey record (for registered users or guests)."""
        query = """
            INSERT INTO journeys (
                user_id, origin_name, origin_latitude, origin_longitude,
                destination_name, destination_latitude, destination_longitude,
                departure_time, arrival_time, total_duration_min, walking_distance_m,
                estimated_fare, route_type, otp_itinerary_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING journey_id, user_id, origin_name, origin_latitude, origin_longitude,
                      destination_name, destination_latitude, destination_longitude,
                      departure_time, arrival_time, total_duration_min, walking_distance_m,
                      estimated_fare, route_type, otp_itinerary_id, created_at;
        """
        return fetch_one(query, (
            user_id, origin_name, origin_latitude, origin_longitude,
            destination_name, destination_latitude, destination_longitude,
            departure_time, arrival_time, total_duration_min, walking_distance_m,
            estimated_fare, route_type, otp_itinerary_id
        ))

    @staticmethod
    def get_by_id(journey_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a journey by UUID."""
        query = """
            SELECT journey_id, user_id, origin_name, origin_latitude, origin_longitude,
                   destination_name, destination_latitude, destination_longitude,
                   departure_time, arrival_time, total_duration_min, walking_distance_m,
                   estimated_fare, route_type, otp_itinerary_id, created_at
            FROM journeys
            WHERE journey_id = %s;
        """
        return fetch_one(query, (journey_id,))

    @staticmethod
    def list_by_user_id(user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve journey history for an authenticated user with pagination."""
        query = """
            SELECT journey_id, user_id, origin_name, origin_latitude, origin_longitude,
                   destination_name, destination_latitude, destination_longitude,
                   departure_time, arrival_time, total_duration_min, walking_distance_m,
                   estimated_fare, route_type, otp_itinerary_id, created_at
            FROM journeys
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s;
        """
        return fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def count_by_user_id(user_id: str) -> int:
        """Count total journeys for a specific user."""
        res = fetch_one("SELECT COUNT(*) AS total FROM journeys WHERE user_id = %s;", (user_id,))
        return res["total"] if res else 0

    @staticmethod
    def count_total() -> int:
        """Total journeys in the system for admin statistics."""
        res = fetch_one("SELECT COUNT(*) AS total FROM journeys;")
        return res["total"] if res else 0
