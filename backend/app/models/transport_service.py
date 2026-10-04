"""
TransportService Model - Direct parameterized SQL for transport_services table.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class TransportServiceModel:
    """Encapsulates CRUD operations for transport_services table."""

    @staticmethod
    def create(
        mode: str,
        operator_name: str,
        service_name: str,
        external_id: Optional[str] = None,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a new transport service."""
        query = """
            INSERT INTO transport_services (mode, operator_name, service_name, external_id, description, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING service_id, mode, operator_name, service_name, external_id, description, is_active, created_at, updated_at;
        """
        return fetch_one(query, (mode, operator_name, service_name, external_id, description, is_active))

    @staticmethod
    def get_by_id(service_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a service by UUID."""
        query = """
            SELECT service_id, mode, operator_name, service_name, external_id, description, is_active, created_at, updated_at
            FROM transport_services
            WHERE service_id = %s;
        """
        return fetch_one(query, (service_id,))

    @staticmethod
    def get_by_mode(mode: str) -> Optional[Dict[str, Any]]:
        """Retrieve the primary active service for a mode (e.g., 'BUS', 'METRO', 'TAXI')."""
        query = """
            SELECT service_id, mode, operator_name, service_name, external_id, description, is_active, created_at, updated_at
            FROM transport_services
            WHERE mode = %s AND is_active = TRUE
            ORDER BY created_at ASC
            LIMIT 1;
        """
        return fetch_one(query, (mode,))

    @staticmethod
    def list_all(active_only: bool = False) -> List[Dict[str, Any]]:
        """List all transport services."""
        if active_only:
            query = """
                SELECT service_id, mode, operator_name, service_name, external_id, description, is_active, created_at, updated_at
                FROM transport_services
                WHERE is_active = TRUE
                ORDER BY mode ASC, operator_name ASC;
            """
            return fetch_all(query)
        query = """
            SELECT service_id, mode, operator_name, service_name, external_id, description, is_active, created_at, updated_at
            FROM transport_services
            ORDER BY mode ASC, operator_name ASC;
        """
        return fetch_all(query)

    @staticmethod
    def update(
        service_id: str,
        operator_name: Optional[str] = None,
        service_name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Dict[str, Any]]:
        """Update transport service details (Admin)."""
        query = """
            UPDATE transport_services
            SET operator_name = COALESCE(%s, operator_name),
                service_name = COALESCE(%s, service_name),
                description = COALESCE(%s, description),
                is_active = COALESCE(%s, is_active),
                updated_at = CURRENT_TIMESTAMP
            WHERE service_id = %s
            RETURNING service_id, mode, operator_name, service_name, external_id, description, is_active, created_at, updated_at;
        """
        return fetch_one(query, (operator_name, service_name, description, is_active, service_id))
