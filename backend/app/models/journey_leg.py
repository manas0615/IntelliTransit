"""
JourneyLeg Model - Direct parameterized SQL for journey_legs table.
Enables leg-based ticketing and route breakdown.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class JourneyLegModel:
    """Encapsulates CRUD operations for the journey_legs table."""

    @staticmethod
    def create(
        journey_id: str,
        sequence_number: int,
        mode: str,
        from_name: str,
        from_latitude: float,
        from_longitude: float,
        to_name: str,
        to_latitude: float,
        to_longitude: float,
        service_id: Optional[str] = None,
        departure_time: Optional[str] = None,
        arrival_time: Optional[str] = None,
        duration_min: Optional[int] = None,
        walking_distance_m: Optional[int] = None,
        estimated_fare: Optional[float] = None,
        is_ticketable: bool = False
    ) -> Dict[str, Any]:
        """Insert a single journey leg record."""
        query = """
            INSERT INTO journey_legs (
                journey_id, sequence_number, mode, service_id,
                from_name, from_latitude, from_longitude,
                to_name, to_latitude, to_longitude,
                departure_time, arrival_time, duration_min,
                walking_distance_m, estimated_fare, is_ticketable
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING leg_id, journey_id, sequence_number, mode, service_id,
                      from_name, from_latitude, from_longitude,
                      to_name, to_latitude, to_longitude,
                      departure_time, arrival_time, duration_min,
                      walking_distance_m, estimated_fare, is_ticketable, created_at;
        """
        return fetch_one(query, (
            journey_id, sequence_number, mode, service_id,
            from_name, from_latitude, from_longitude,
            to_name, to_latitude, to_longitude,
            departure_time, arrival_time, duration_min,
            walking_distance_m, estimated_fare, is_ticketable
        ))

    @staticmethod
    def get_by_id(leg_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a journey leg by UUID."""
        query = """
            SELECT leg_id, journey_id, sequence_number, mode, service_id,
                   from_name, from_latitude, from_longitude,
                   to_name, to_latitude, to_longitude,
                   departure_time, arrival_time, duration_min,
                   walking_distance_m, estimated_fare, is_ticketable, created_at
            FROM journey_legs
            WHERE leg_id = %s;
        """
        return fetch_one(query, (leg_id,))

    @staticmethod
    def list_by_journey_id(journey_id: str) -> List[Dict[str, Any]]:
        """Retrieve all ordered legs for a given journey."""
        query = """
            SELECT jl.leg_id, jl.journey_id, jl.sequence_number, jl.mode, jl.service_id,
                   jl.from_name, jl.from_latitude, jl.from_longitude,
                   jl.to_name, jl.to_latitude, jl.to_longitude,
                   jl.departure_time, jl.arrival_time, jl.duration_min,
                   jl.walking_distance_m, jl.estimated_fare, jl.is_ticketable, jl.created_at,
                   ts.operator_name, ts.service_name
            FROM journey_legs jl
            LEFT JOIN transport_services ts ON jl.service_id = ts.service_id
            WHERE jl.journey_id = %s
            ORDER BY jl.sequence_number ASC;
        """
        return fetch_all(query, (journey_id,))
