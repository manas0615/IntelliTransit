"""
Payment Model - Direct parameterized SQL for payments table.
Strict 1:1 relationship with Ticket or Pass. Backend authoritative.
Supports internal simulated payments for academic demonstration.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.db import fetch_one, fetch_all, execute_query


class PaymentModel:
    """Encapsulates CRUD operations for payments table."""

    @staticmethod
    def create(
        user_id: str,
        amount: float,
        payment_type: str,
        transaction_reference: str,
        currency: str = "INR",
        status: str = "PENDING",
        payment_method: str = "SIMULATED"
    ) -> Dict[str, Any]:
        """Create a new local payment record."""
        query = """
            INSERT INTO payments (user_id, amount, currency, payment_type, status, payment_method, transaction_reference)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING payment_id, user_id, amount, currency, payment_type, status,
                      payment_method, transaction_reference, created_at, updated_at;
        """
        return fetch_one(query, (user_id, amount, currency, payment_type, status, payment_method, transaction_reference))

    @staticmethod
    def get_by_id(payment_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve payment by ID."""
        query = """
            SELECT payment_id, user_id, amount, currency, payment_type, status,
                   payment_method, transaction_reference, created_at, updated_at
            FROM payments
            WHERE payment_id = %s;
        """
        return fetch_one(query, (payment_id,))

    @staticmethod
    def get_by_transaction_reference(transaction_reference: str) -> Optional[Dict[str, Any]]:
        """Retrieve payment by transaction reference."""
        query = """
            SELECT payment_id, user_id, amount, currency, payment_type, status,
                   payment_method, transaction_reference, created_at, updated_at
            FROM payments
            WHERE transaction_reference = %s;
        """
        return fetch_one(query, (transaction_reference,))

    @staticmethod
    def get_by_order_id(transaction_reference: str) -> Optional[Dict[str, Any]]:
        """Compatibility alias for get_by_transaction_reference."""
        return PaymentModel.get_by_transaction_reference(transaction_reference)

    @staticmethod
    def update_status(
        payment_id: str,
        status: str
    ) -> Optional[Dict[str, Any]]:
        """Update payment status (SUCCESS, FAILED, REFUNDED)."""
        query = """
            UPDATE payments
            SET status = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE payment_id = %s
            RETURNING payment_id, user_id, amount, currency, payment_type, status,
                      payment_method, transaction_reference, created_at, updated_at;
        """
        return fetch_one(query, (status, payment_id))

    @staticmethod
    def list_by_user_id(user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List payment history for a user with pagination."""
        query = """
            SELECT payment_id, user_id, amount, currency, payment_type, status,
                   payment_method, transaction_reference, created_at, updated_at
            FROM payments
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s;
        """
        return fetch_all(query, (user_id, limit, offset))

    @staticmethod
    def get_total_revenue() -> float:
        """Total successful revenue for admin dashboard."""
        res = fetch_one("SELECT COALESCE(SUM(amount), 0.0) AS revenue FROM payments WHERE status = 'SUCCESS';")
        return float(res["revenue"]) if res else 0.0

    @staticmethod
    def count_by_status() -> Dict[str, int]:
        """Aggregate payment counts by status for admin."""
        query = """
            SELECT status, COUNT(*) AS count
            FROM payments
            GROUP BY status;
        """
        rows = fetch_all(query)
        return {r["status"]: r["count"] for r in rows}

