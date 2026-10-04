"""
Admin Service - Platform management, analytics, user administration, and fare rule configuration.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.user import UserModel
from backend.app.models.journey import JourneyModel
from backend.app.models.ticket import TicketModel
from backend.app.models.pass_model import PassModel
from backend.app.models.payment import PaymentModel
from backend.app.models.transport_service import TransportServiceModel
from backend.app.models.fare_configuration import FareConfigurationModel
from backend.app.models.ticket_validation import TicketValidationModel
from backend.app.models.db import fetch_one, fetch_all, execute_query


class AdminService:
    """Encapsulates administrative queries, metrics aggregation, and configuration updates."""

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Aggregate high-level platform health and business metrics."""
        # 1. Total users
        u_row = fetch_one("SELECT COUNT(*) AS total_users FROM users;")
        total_users = int(u_row["total_users"]) if u_row else 0

        # 2. Total journeys planned
        j_row = fetch_one("SELECT COUNT(*) AS total_journeys FROM journeys;")
        total_journeys = int(j_row["total_journeys"]) if j_row else 0

        # 3. Total revenue
        total_revenue = PaymentModel.get_total_revenue()

        # 4. Active tickets & passes
        t_row = fetch_one("SELECT COUNT(*) AS active_tickets FROM tickets WHERE status = 'ACTIVE';")
        active_tickets = int(t_row["active_tickets"]) if t_row else 0

        p_row = fetch_one("SELECT COUNT(*) AS active_passes FROM passes WHERE status = 'ACTIVE';")
        active_passes = int(p_row["active_passes"]) if p_row else 0

        # 5. Total validations
        v_row = fetch_one("SELECT COUNT(*) AS total_validations FROM ticket_validations;")
        total_validations = int(v_row["total_validations"]) if v_row else 0

        return {
            "total_users": total_users,
            "total_journeys": total_journeys,
            "total_revenue": total_revenue,
            "active_tickets": active_tickets,
            "active_passes": active_passes,
            "total_validations": total_validations,
            "system_status": "OPERATIONAL"
        }

    @staticmethod
    def list_users(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List platform users with role and status."""
        return UserModel.list_all(limit=limit, offset=offset)

    @staticmethod
    def update_user_status(user_id: str, is_active: bool) -> Optional[Dict[str, Any]]:
        """Activate or deactivate a user account."""
        query = """
            UPDATE users
            SET is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, email, full_name, role, is_active, updated_at;
        """
        return fetch_one(query, (is_active, user_id))

    @staticmethod
    def update_user_role(user_id: str, role: str) -> Optional[Dict[str, Any]]:
        """Update user role (USER, ADMIN)."""
        clean_role = role.upper().strip()
        if clean_role not in ('USER', 'ADMIN'):
            raise ValueError(f"Invalid role: {role}. Must be USER or ADMIN.")

        query = """
            UPDATE users
            SET role = %s, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, email, full_name, role, is_active, updated_at;
        """
        return fetch_one(query, (clean_role, user_id))

    @staticmethod
    def list_transport_services() -> List[Dict[str, Any]]:
        """List all transport services (Bus, Metro, Taxi)."""
        return TransportServiceModel.list_all()

    @staticmethod
    def list_fare_configurations() -> List[Dict[str, Any]]:
        """List all active and historical fare configurations."""
        return FareConfigurationModel.list_all()

    @staticmethod
    def update_fare_configuration(
        fare_id: str,
        base_fare: Optional[float] = None,
        per_km_rate: Optional[float] = None,
        min_fare: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Update fare rules for a transit service."""
        return FareConfigurationModel.update(
            fare_id=fare_id,
            base_fare=base_fare,
            per_km_rate=per_km_rate,
            minimum_fare=min_fare
        )

    @staticmethod
    def get_recent_validations(limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent ticket and pass inspections."""
        return TicketValidationModel.list_recent(limit=limit)
