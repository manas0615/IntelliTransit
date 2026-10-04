"""
FareConfiguration Model - Direct parameterized SQL for fare_configurations table.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class FareConfigurationModel:
    """Encapsulates CRUD operations for fare_configurations table."""

    @staticmethod
    def create(
        service_id: str,
        fare_type: str,
        base_fare: float,
        per_km_rate: Optional[float] = None,
        minimum_fare: Optional[float] = None,
        effective_from: Optional[str] = "CURRENT_TIMESTAMP",
        effective_until: Optional[str] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a new fare configuration."""
        query = """
            INSERT INTO fare_configurations (
                service_id, fare_type, base_fare, per_km_rate, minimum_fare,
                effective_from, effective_until, is_active
            )
            VALUES (%s, %s, %s, %s, %s, COALESCE(%s::timestamp, CURRENT_TIMESTAMP), %s, %s)
            RETURNING fare_id, service_id, fare_type, base_fare, per_km_rate, minimum_fare,
                      effective_from, effective_until, is_active, created_at;
        """
        return fetch_one(query, (
            service_id, fare_type, base_fare, per_km_rate, minimum_fare,
            effective_from, effective_until, is_active
        ))

    @staticmethod
    def get_by_id(fare_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve fare configuration by ID."""
        query = """
            SELECT fc.fare_id, fc.service_id, fc.fare_type, fc.base_fare, fc.per_km_rate,
                   fc.minimum_fare, fc.effective_from, fc.effective_until, fc.is_active, fc.created_at,
                   ts.mode, ts.operator_name, ts.service_name
            FROM fare_configurations fc
            JOIN transport_services ts ON fc.service_id = ts.service_id
            WHERE fc.fare_id = %s;
        """
        return fetch_one(query, (fare_id,))

    @staticmethod
    def get_active_by_service_id(service_id: str) -> Optional[Dict[str, Any]]:
        """Get current active fare configuration for a service."""
        query = """
            SELECT fare_id, service_id, fare_type, base_fare, per_km_rate, minimum_fare,
                   effective_from, effective_until, is_active, created_at
            FROM fare_configurations
            WHERE service_id = %s
              AND is_active = TRUE
              AND effective_from <= CURRENT_TIMESTAMP
              AND (effective_until IS NULL OR effective_until > CURRENT_TIMESTAMP)
            ORDER BY effective_from DESC
            LIMIT 1;
        """
        return fetch_one(query, (service_id,))

    @staticmethod
    def get_active_by_mode(mode: str) -> Optional[Dict[str, Any]]:
        """Get current active fare configuration by transport mode (BUS, METRO, TAXI)."""
        query = """
            SELECT fc.fare_id, fc.service_id, fc.fare_type, fc.base_fare, fc.per_km_rate,
                   fc.minimum_fare, fc.effective_from, fc.effective_until, fc.is_active, fc.created_at,
                   ts.mode, ts.operator_name, ts.service_name
            FROM fare_configurations fc
            JOIN transport_services ts ON fc.service_id = ts.service_id
            WHERE ts.mode = %s
              AND ts.is_active = TRUE
              AND fc.is_active = TRUE
              AND fc.effective_from <= CURRENT_TIMESTAMP
              AND (fc.effective_until IS NULL OR fc.effective_until > CURRENT_TIMESTAMP)
            ORDER BY fc.effective_from DESC
            LIMIT 1;
        """
        return fetch_one(query, (mode,))

    @staticmethod
    def list_all() -> List[Dict[str, Any]]:
        """List all fare configurations with service details."""
        query = """
            SELECT fc.fare_id, fc.service_id, fc.fare_type, fc.base_fare, fc.per_km_rate,
                   fc.minimum_fare, fc.effective_from, fc.effective_until, fc.is_active, fc.created_at,
                   ts.mode, ts.operator_name, ts.service_name
            FROM fare_configurations fc
            JOIN transport_services ts ON fc.service_id = ts.service_id
            ORDER BY ts.mode ASC, fc.effective_from DESC;
        """
        return fetch_all(query)

    @staticmethod
    def update(
        fare_id: str,
        base_fare: Optional[float] = None,
        per_km_rate: Optional[float] = None,
        minimum_fare: Optional[float] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Update fare configuration (Admin)."""
        query = """
            UPDATE fare_configurations
            SET base_fare = COALESCE(%s, base_fare),
                per_km_rate = COALESCE(%s, per_km_rate),
                minimum_fare = COALESCE(%s, minimum_fare),
                is_active = COALESCE(%s, is_active)
            WHERE fare_id = %s
            RETURNING fare_id, service_id, fare_type, base_fare, per_km_rate, minimum_fare,
                      effective_from, effective_until, is_active, created_at;
        """
        return fetch_one(query, (base_fare, per_km_rate, minimum_fare, is_active, fare_id))
