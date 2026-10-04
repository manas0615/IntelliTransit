"""
Payment Service - Internal Simulated Demo Payment System.
Handles server-authoritative payment initiation, verification, and atomic ticket/pass activation.
Real payment gateway integration is outside the scope of this academic demonstration.
"""
import secrets
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from backend.app.models.payment import PaymentModel
from backend.app.models.ticket import TicketModel
from backend.app.models.pass_model import PassModel
from backend.app.models.db import get_db_connection, fetch_one, execute_query

logger = logging.getLogger(__name__)


class PaymentService:
    """Service encapsulating internal simulated payment flows."""

    @staticmethod
    def create_order_for_item(user_id: str, item_type: str, item_id: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Initialize a simulated payment session for a pending ticket or pass.
        Returns server-authoritative details for the in-app Demo Payment modal.
        """
        clean_type = item_type.upper().strip()
        amount = 0.0
        currency = "INR"

        if clean_type == "TICKET":
            ticket = TicketModel.get_by_id(item_id)
            if not ticket or ticket["user_id"] != user_id:
                return False, {"code": "TICKET_NOT_FOUND"}, "Ticket not found or unauthorized."
            if ticket["status"] != "PENDING":
                return False, {"code": "INVALID_STATUS"}, f"Ticket is already in {ticket['status']} status."
            amount = float(ticket["fare"])
            payment_id = ticket["payment_id"]
        elif clean_type == "PASS":
            pass_item = PassModel.get_by_id(item_id)
            if not pass_item or pass_item["user_id"] != user_id:
                return False, {"code": "PASS_NOT_FOUND"}, "Pass not found or unauthorized."
            if pass_item["status"] != "PENDING":
                return False, {"code": "INVALID_STATUS"}, f"Pass is already in {pass_item['status']} status."
            amount = float(pass_item["price"])
            payment_id = pass_item["payment_id"]
        else:
            return False, {"code": "INVALID_ITEM_TYPE"}, "Item type must be TICKET or PASS."

        payment = PaymentModel.get_by_id(payment_id)
        if not payment:
            tx_ref = f"DEMO-{secrets.token_hex(8).upper()}"
            payment = PaymentModel.create(
                user_id=user_id,
                amount=amount,
                payment_type=clean_type,
                transaction_reference=tx_ref,
                currency=currency,
                status="PENDING",
                payment_method="SIMULATED"
            )
        else:
            tx_ref = payment.get("transaction_reference")

        return True, {
            "payment_id": payment["payment_id"],
            "transaction_reference": tx_ref,
            "order_id": tx_ref,  # compatibility alias
            "amount": amount,
            "currency": currency,
            "payment_method": "SIMULATED",
            "item_type": clean_type,
            "item_id": item_id,
            "status": "PENDING"
        }, "Demo payment initialized."

    @staticmethod
    def confirm_simulated_payment(
        user_id: str,
        payment_id: Optional[str] = None,
        transaction_reference: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Confirm simulated demo payment and atomically activate the ticket or pass.
        Enforces server-authoritative amount match, ownership, and prevents duplicate confirmation.
        """
        payment = None
        if payment_id:
            payment = PaymentModel.get_by_id(payment_id)
        if not payment and transaction_reference:
            payment = PaymentModel.get_by_transaction_reference(transaction_reference)

        if not payment:
            return False, {"code": "PAYMENT_NOT_FOUND"}, "Payment record not found."

        # Ownership validation
        if str(payment["user_id"]) != str(user_id):
            return False, {"code": "FORBIDDEN"}, "Unauthorized access to this payment."

        # Prevent duplicate payment confirmation
        if payment["status"] == "SUCCESS":
            return False, {
                "code": "DUPLICATE_PAYMENT",
                "payment_id": payment["payment_id"],
                "payment_status": "SUCCESS"
            }, "Payment has already been processed and confirmed."

        if payment["status"] != "PENDING":
            return False, {
                "code": "INVALID_PAYMENT_STATUS",
                "payment_id": payment["payment_id"]
            }, f"Payment is in {payment['status']} status and cannot be confirmed."

        now = datetime.now()
        activated_item = None

        with get_db_connection():
            # Validate and activate associated item
            if payment["payment_type"] == "TICKET":
                t_row = fetch_one("SELECT ticket_id, user_id, status, fare FROM tickets WHERE payment_id = %s;", (payment["payment_id"],))
                if not t_row:
                    return False, {"code": "TICKET_NOT_FOUND"}, "Associated ticket not found."
                if str(t_row["user_id"]) != str(user_id):
                    return False, {"code": "FORBIDDEN"}, "Ticket ownership mismatch."
                if t_row["status"] != "PENDING":
                    return False, {"code": "INVALID_TICKET_STATUS"}, f"Ticket is already {t_row['status']}."
                if float(t_row["fare"]) != float(payment["amount"]):
                    return False, {"code": "AMOUNT_MISMATCH"}, "Server calculated fare does not match payment amount."

                valid_from = now.strftime("%Y-%m-%d %H:%M:%S")
                valid_until = (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
                activated_item = TicketModel.activate(t_row["ticket_id"], valid_from, valid_until)

            elif payment["payment_type"] == "PASS":
                p_row = fetch_one("SELECT pass_id, user_id, pass_type, status, price FROM passes WHERE payment_id = %s;", (payment["payment_id"],))
                if not p_row:
                    return False, {"code": "PASS_NOT_FOUND"}, "Associated pass not found."
                if str(p_row["user_id"]) != str(user_id):
                    return False, {"code": "FORBIDDEN"}, "Pass ownership mismatch."
                if p_row["status"] != "PENDING":
                    return False, {"code": "INVALID_PASS_STATUS"}, f"Pass is already {p_row['status']}."
                if float(p_row["price"]) != float(payment["amount"]):
                    return False, {"code": "AMOUNT_MISMATCH"}, "Server calculated pass price does not match payment amount."

                pass_type = p_row["pass_type"]
                duration_days = 1 if pass_type == "DAILY" else (7 if pass_type == "WEEKLY" else 30)
                valid_from = now.strftime("%Y-%m-%d %H:%M:%S")
                valid_until = (now + timedelta(days=duration_days)).strftime("%Y-%m-%d %H:%M:%S")
                pass_token = f"PASS-{pass_type}-{p_row['pass_id'][:8]}"
                activated_item = PassModel.activate(p_row["pass_id"], pass_token, valid_from, valid_until)

            # Update Payment status to SUCCESS
            updated_payment = PaymentModel.update_status(payment["payment_id"], status="SUCCESS")

        return True, {
            "payment": updated_payment,
            "activated_item": activated_item,
            "payment_type": payment["payment_type"],
            "payment_status": "SUCCESS",
            "payment_method": "SIMULATED"
        }, "Payment Successful — Demo Mode. Item is now ACTIVE."

    @staticmethod
    def verify_payment(
        order_reference: Optional[str] = None,
        user_id: Optional[str] = None,
        payment_id: Optional[str] = None,
        transaction_reference: Optional[str] = None,
        **kwargs
    ) -> Tuple[bool, Dict[str, Any], str]:
        """Compatibility adapter routing verify calls to confirm_simulated_payment."""
        ref = transaction_reference or order_reference or kwargs.get("order_id")
        pid = payment_id
        if not user_id and (pid or ref):
            p = PaymentModel.get_by_id(pid) if pid else PaymentModel.get_by_transaction_reference(ref)
            if p:
                user_id = str(p["user_id"])

        return PaymentService.confirm_simulated_payment(
            user_id=user_id or "",
            payment_id=pid,
            transaction_reference=ref
        )

    @staticmethod
    def list_user_payments(user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List simulated payment history for user."""
        return PaymentModel.list_by_user_id(user_id, limit, offset)

    @staticmethod
    def get_payment_details(payment_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single payment details."""
        payment = PaymentModel.get_by_id(payment_id)
        if not payment or str(payment["user_id"]) != str(user_id):
            return None
        return payment
