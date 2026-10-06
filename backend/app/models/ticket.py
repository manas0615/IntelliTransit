"""
Ticket Model - Direct parameterized SQL for tickets table.
Enforces leg-based ticketing, snapshot values, unique payment mapping, and state transitions.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class TicketModel:
    """Encapsulates CRUD operations for tickets table."""

    @staticmethod
    def create(
        user_id: str,
        journey_id: str,
        journey_leg_id: str,
        payment_id: str,
        ticket_token: str,
        origin: str,
        destination: str,
        fare: float,
        status: str = "PENDING",
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new ticket record snapshot."""
        query = """
            INSERT INTO tickets (
                user_id, journey_id, journey_leg_id, payment_id,
                ticket_token, status, origin, destination, fare,
                valid_from, valid_until
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ticket_id, user_id, journey_id, journey_leg_id, payment_id,
                      ticket_token, status, origin, destination, fare,
                      valid_from, valid_until, created_at;
        """
        return fetch_one(query, (
            user_id, journey_id, journey_leg_id, payment_id,
            ticket_token, status, origin, destination, fare,
            valid_from, valid_until
        ))

    @staticmethod
    def get_by_id(ticket_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a ticket with leg and payment context."""
        query = """
            SELECT t.ticket_id, t.user_id, t.journey_id, t.journey_leg_id, t.payment_id,
                   t.ticket_token, t.status, t.origin, t.destination, t.fare,
                   t.valid_from, t.valid_until, t.created_at,
                   jl.mode, ts.operator_name, ts.service_name,
                   p.transaction_reference, p.payment_method, p.status AS payment_status
            FROM tickets t
            JOIN journey_legs jl ON t.journey_leg_id = jl.leg_id
            LEFT JOIN transport_services ts ON jl.service_id = ts.service_id
            JOIN payments p ON t.payment_id = p.payment_id
            WHERE t.ticket_id = %s;
        """
        return fetch_one(query, (ticket_id,))

    @staticmethod
    def get_by_token(ticket_token: str) -> Optional[Dict[str, Any]]:
        """Retrieve a ticket by its secure QR ticket token for validation."""
        query = """
            SELECT t.ticket_id, t.user_id, t.journey_id, t.journey_leg_id, t.payment_id,
                   t.ticket_token, t.status, t.origin, t.destination, t.fare,
                   t.valid_from, t.valid_until, t.created_at,
                   jl.mode, ts.operator_name, ts.service_name
            FROM tickets t
            JOIN journey_legs jl ON t.journey_leg_id = jl.leg_id
            LEFT JOIN transport_services ts ON jl.service_id = ts.service_id
            WHERE t.ticket_token = %s;
        """
        return fetch_one(query, (ticket_token,))

    @staticmethod
    def get_by_leg_id(journey_leg_id: str) -> Optional[Dict[str, Any]]:
        """Find existing ticket for a journey leg to prevent duplicate purchases."""
        query = """
            SELECT ticket_id, user_id, journey_id, journey_leg_id, payment_id,
                   ticket_token, status, origin, destination, fare, valid_from, valid_until, created_at
            FROM tickets
            WHERE journey_leg_id = %s;
        """
        return fetch_one(query, (journey_leg_id,))

    @staticmethod
    def activate(ticket_id: str, valid_from: str, valid_until: str) -> Optional[Dict[str, Any]]:
        """Activate a ticket following successful payment verification."""
        query = """
            UPDATE tickets
            SET status = 'ACTIVE',
                valid_from = %s,
                valid_until = %s
            WHERE ticket_id = %s AND status = 'PENDING'
            RETURNING ticket_id, user_id, journey_id, journey_leg_id, payment_id,
                      ticket_token, status, origin, destination, fare,
                      valid_from, valid_until, created_at;
        """
        return fetch_one(query, (valid_from, valid_until, ticket_id))

    @staticmethod
    def mark_used(ticket_id: str) -> Optional[Dict[str, Any]]:
        """Transition ticket status ACTIVE -> USED upon validation."""
        query = """
            UPDATE tickets
            SET status = 'USED'
            WHERE ticket_id = %s AND status = 'ACTIVE'
            RETURNING ticket_id, user_id, journey_id, journey_leg_id, payment_id,
                      ticket_token, status, origin, destination, fare,
                      valid_from, valid_until, created_at;
        """
        return fetch_one(query, (ticket_id,))

    @staticmethod
    def cancel(ticket_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Cancel a ticket if eligible (pre-validity window).
        Ensures user ownership.
        """
        query = """
            UPDATE tickets
            SET status = 'CANCELLED'
            WHERE ticket_id = %s
              AND user_id = %s
              AND status IN ('PENDING', 'ACTIVE')
              AND (valid_from IS NULL OR CURRENT_TIMESTAMP < valid_from)
            RETURNING ticket_id, user_id, journey_id, journey_leg_id, payment_id,
                      ticket_token, status, origin, destination, fare,
                      valid_from, valid_until, created_at;
        """
        return fetch_one(query, (ticket_id, user_id))

    @staticmethod
    def list_by_user_id(user_id: str, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List tickets for a user with optional status filter."""
        if status:
            query = """
                SELECT t.ticket_id, t.user_id, t.journey_id, t.journey_leg_id, t.payment_id,
                       t.ticket_token, t.status, t.origin, t.destination, t.fare,
                       t.valid_from, t.valid_until, t.created_at,
                       jl.mode, ts.operator_name, ts.service_name
                FROM tickets t
                JOIN journey_legs jl ON t.journey_leg_id = jl.leg_id
                LEFT JOIN transport_services ts ON jl.service_id = ts.service_id
                WHERE t.user_id = %s AND t.status = %s
                ORDER BY t.created_at DESC
                LIMIT %s OFFSET %s;
            """
            return fetch_all(query, (user_id, status, limit, offset))
        query = """
            SELECT t.ticket_id, t.user_id, t.journey_id, t.journey_leg_id, t.payment_id,
                   t.ticket_token, t.status, t.origin, t.destination, t.fare,
                   t.valid_from, t.valid_until, t.created_at,
                   jl.mode, ts.operator_name, ts.service_name
            FROM tickets t
            JOIN journey_legs jl ON t.journey_leg_id = jl.leg_id
            LEFT JOIN transport_services ts ON jl.service_id = ts.service_id
            WHERE t.user_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s;
        """
        return fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def count_by_status() -> Dict[str, int]:
        """Aggregate ticket counts by status for admin."""
        query = """
            SELECT status, COUNT(*) AS count
            FROM tickets
            GROUP BY status;
        """
        rows = fetch_all(query)
        return {r["status"]: r["count"] for r in rows}

    @staticmethod
    def list_all_for_inspection(limit: int = 50, offset: int = 0, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tickets across all commuters for conductor inspection."""
        params = []
        where_clause = ""
        if status:
            where_clause = "WHERE t.status = %s"
            params.append(status)
        params.extend([limit, offset])

        query = f"""
            SELECT t.ticket_id, t.user_id, t.journey_id, t.journey_leg_id, t.payment_id,
                   t.ticket_token, t.status, t.origin, t.destination, t.fare,
                   t.valid_from, t.valid_until, t.created_at,
                   u.full_name AS passenger_name, u.email AS passenger_email,
                   jl.mode AS transport_mode, ts.service_name, ts.operator_name,
                   p.status AS payment_status, p.payment_method,
                   (SELECT COUNT(*) FROM ticket_validations tv WHERE tv.ticket_id = t.ticket_id) AS validation_count,
                   (SELECT tv.validation_status FROM ticket_validations tv WHERE tv.ticket_id = t.ticket_id ORDER BY tv.validation_time DESC LIMIT 1) AS last_validation_status
            FROM tickets t
            JOIN users u ON t.user_id = u.user_id
            JOIN journey_legs jl ON t.journey_leg_id = jl.leg_id
            LEFT JOIN transport_services ts ON jl.service_id = ts.service_id
            LEFT JOIN payments p ON t.payment_id = p.payment_id
            {where_clause}
            ORDER BY t.created_at DESC
            LIMIT %s OFFSET %s;
        """
        return fetch_all(query, tuple(params))
