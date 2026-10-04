"""
Pass Model - Direct parameterized SQL for passes table.
Periodic passes (DAILY, WEEKLY, MONTHLY) with 1:1 payment link.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class PassModel:
    """Encapsulates CRUD operations for passes table."""

    @staticmethod
    def create(
        user_id: str,
        payment_id: str,
        pass_type: str,
        price: float,
        pass_token: Optional[str] = None,
        status: str = "PENDING",
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new periodic pass record."""
        query = """
            INSERT INTO passes (
                user_id, payment_id, pass_type, price,
                pass_token, status, valid_from, valid_until
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING pass_id, user_id, payment_id, pass_type, price,
                      pass_token, status, valid_from, valid_until, created_at;
        """
        return fetch_one(query, (
            user_id, payment_id, pass_type, price,
            pass_token, status, valid_from, valid_until
        ))

    @staticmethod
    def get_by_id(pass_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve pass by UUID."""
        query = """
            SELECT p.pass_id, p.user_id, p.payment_id, p.pass_type, p.price,
                   p.pass_token, p.status, p.valid_from, p.valid_until, p.created_at,
                   pay.transaction_reference, pay.payment_method, pay.status AS payment_status
            FROM passes p
            JOIN payments pay ON p.payment_id = pay.payment_id
            WHERE p.pass_id = %s;
        """
        return fetch_one(query, (pass_id,))

    @staticmethod
    def get_by_token(pass_token: str) -> Optional[Dict[str, Any]]:
        """Retrieve pass by its QR pass token."""
        query = """
            SELECT pass_id, user_id, payment_id, pass_type, price,
                   pass_token, status, valid_from, valid_until, created_at
            FROM passes
            WHERE pass_token = %s;
        """
        return fetch_one(query, (pass_token,))

    @staticmethod
    def activate(pass_id: str, pass_token: str, valid_from: str, valid_until: str) -> Optional[Dict[str, Any]]:
        """Activate a pass upon successful payment verification."""
        query = """
            UPDATE passes
            SET status = 'ACTIVE',
                pass_token = %s,
                valid_from = %s,
                valid_until = %s
            WHERE pass_id = %s AND status = 'PENDING'
            RETURNING pass_id, user_id, payment_id, pass_type, price,
                      pass_token, status, valid_from, valid_until, created_at;
        """
        return fetch_one(query, (pass_token, valid_from, valid_until, pass_id))

    @staticmethod
    def cancel(pass_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Cancel a pass if eligible before validity begins."""
        query = """
            UPDATE passes
            SET status = 'CANCELLED'
            WHERE pass_id = %s
              AND user_id = %s
              AND status IN ('PENDING', 'ACTIVE')
              AND (valid_from IS NULL OR CURRENT_TIMESTAMP < valid_from)
            RETURNING pass_id, user_id, payment_id, pass_type, price,
                      pass_token, status, valid_from, valid_until, created_at;
        """
        return fetch_one(query, (pass_id, user_id))

    @staticmethod
    def list_by_user_id(user_id: str, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List passes owned by a user."""
        if status:
            query = """
                SELECT pass_id, user_id, payment_id, pass_type, price,
                       pass_token, status, valid_from, valid_until, created_at
                FROM passes
                WHERE user_id = %s AND status = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s;
            """
            return fetch_all(query, (user_id, status, limit, offset))
        query = """
            SELECT pass_id, user_id, payment_id, pass_type, price,
                   pass_token, status, valid_from, valid_until, created_at
            FROM passes
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s;
        """
        return fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def count_by_status() -> Dict[str, int]:
        """Aggregate pass counts by status for admin."""
        query = """
            SELECT status, COUNT(*) AS count
            FROM passes
            GROUP BY status;
        """
        rows = fetch_all(query)
        return {r["status"]: r["count"] for r in rows}
