"""
Pass Service - Manages periodic transit passes (DAILY, WEEKLY, MONTHLY).
"""
import secrets
from typing import Any, Dict, List, Optional, Tuple
from backend.app.models.pass_model import PassModel
from backend.app.models.payment import PaymentModel

# Standard Curated Pune Pass Pricing (Classification: CURATED)
PASS_PRICING = {
    "DAILY": 50.00,
    "WEEKLY": 300.00,
    "MONTHLY": 1000.00
}


class PassService:
    """Business logic for periodic transit passes."""

    @staticmethod
    def create_pass(user_id: str, pass_type: str) -> Tuple[bool, Dict[str, Any], str]:
        """Create a new periodic pass in pending state with local payment record."""
        clean_type = pass_type.upper().strip()
        if clean_type not in PASS_PRICING:
            return False, {"code": "INVALID_PASS_TYPE"}, "Pass type must be DAILY, WEEKLY, or MONTHLY."

        price = PASS_PRICING[clean_type]

        # 1. Create Local Payment record
        tx_ref = f"DEMO-{secrets.token_hex(8).upper()}"
        payment = PaymentModel.create(
            user_id=user_id,
            amount=price,
            payment_type="PASS",
            transaction_reference=tx_ref,
            status="PENDING",
            payment_method="SIMULATED"
        )

        # 2. Create Pass in PENDING state
        pass_record = PassModel.create(
            user_id=user_id,
            payment_id=payment["payment_id"],
            pass_type=clean_type,
            price=price,
            status="PENDING"
        )
        pass_record["payment"] = payment

        return True, {"pass": pass_record, "payment": payment}, "Pass order created. Proceed to payment."

    @staticmethod
    def get_pass_details(pass_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get pass details ensuring user ownership."""
        p = PassModel.get_by_id(pass_id)
        if not p or p["user_id"] != user_id:
            return None
        return p

    @staticmethod
    def list_user_passes(user_id: str, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List passes owned by user."""
        return PassModel.list_by_user_id(user_id, status=status, limit=limit, offset=offset)

    @staticmethod
    def cancel_pass(pass_id: str, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Cancel pass before validity begins."""
        p = PassModel.get_by_id(pass_id)
        if not p or p["user_id"] != user_id:
            return False, None, "Pass not found or unauthorized."

        if p["status"] == "EXPIRED":
            return False, None, "Expired passes cannot be cancelled."
        if p["status"] == "CANCELLED":
            return False, None, "Pass is already cancelled."

        cancelled = PassModel.cancel(pass_id, user_id)
        if not cancelled:
            return False, None, "Pass cannot be cancelled once validity has started."

        PaymentModel.update_status(p["payment_id"], status="REFUNDED")
        return True, cancelled, "Pass cancelled and refund processed."
