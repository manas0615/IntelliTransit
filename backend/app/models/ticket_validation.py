"""
TicketValidation Model - Direct parameterized SQL for ticket_validations table.
Append-only audit inspection log for QR scans.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class TicketValidationModel:
    """Encapsulates CRUD operations for ticket_validations table."""

    @staticmethod
    def create(
        ticket_id: str,
        validator_user_id: str,
        validation_status: str,
        remarks: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record an inspection attempt in the validation audit log."""
        query = """
            INSERT INTO ticket_validations (ticket_id, validator_user_id, validation_status, remarks, validation_time)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING validation_id, ticket_id, validator_user_id, validation_status,
                      remarks, validation_time, created_at;
        """
        return fetch_one(query, (ticket_id, validator_user_id, validation_status, remarks))

    @staticmethod
    def list_by_ticket_id(ticket_id: str) -> List[Dict[str, Any]]:
        """List all inspection attempts for a ticket."""
        query = """
            SELECT tv.validation_id, tv.ticket_id, tv.validator_user_id, tv.validation_status,
                   tv.remarks, tv.validation_time, tv.created_at,
                   u.full_name AS validator_name, u.email AS validator_email
            FROM ticket_validations tv
            JOIN users u ON tv.validator_user_id = u.user_id
            WHERE tv.ticket_id = %s
            ORDER BY tv.validation_time DESC;
        """
        return fetch_all(query, (ticket_id,))

    @staticmethod
    def list_recent(limit: int = 50) -> List[Dict[str, Any]]:
        """List recent validations for admin audit dashboard."""
        query = """
            SELECT tv.validation_id, tv.ticket_id, tv.validator_user_id, tv.validation_status,
                   tv.remarks, tv.validation_time, tv.created_at,
                   u.full_name AS validator_name,
                   t.origin, t.destination, t.fare
            FROM ticket_validations tv
            JOIN users u ON tv.validator_user_id = u.user_id
            JOIN tickets t ON tv.ticket_id = t.ticket_id
            ORDER BY tv.validation_time DESC
            LIMIT %s;
        """
        return fetch_all(query, (limit,))

    @staticmethod
    def count_total() -> int:
        """Total validation events count."""
        res = fetch_one("SELECT COUNT(*) AS total FROM ticket_validations;")
        return res["total"] if res else 0
