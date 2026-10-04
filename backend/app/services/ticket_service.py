"""
Ticket Service - Manages leg-based ticket creation, lifecycle state transitions, and cancellation.
"""
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from backend.app.models.ticket import TicketModel
from backend.app.models.journey_leg import JourneyLegModel
from backend.app.models.journey import JourneyModel
from backend.app.models.payment import PaymentModel
from backend.app.models.fare_configuration import FareConfigurationModel


class TicketService:
    """Business logic for digital leg-based transit tickets."""

    @staticmethod
    def create_ticket(user_id: str, journey_id: str, journey_leg_id: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Create a new ticket and associated pending payment for an individual ticketable leg.
        Enforces that WALK legs cannot be ticketed.
        """
        journey = JourneyModel.get_by_id(journey_id)
        if not journey:
            return False, {"code": "JOURNEY_NOT_FOUND"}, "Journey not found."

        leg = JourneyLegModel.get_by_id(journey_leg_id)
        if not leg or leg["journey_id"] != journey_id:
            return False, {"code": "LEG_NOT_FOUND"}, "Journey leg not found or does not belong to this journey."

        if not leg.get("is_ticketable") or leg["mode"] == "WALK":
            return False, {"code": "NOT_TICKETABLE"}, "Walking and transfer legs do not require tickets."

        # Check for existing active/pending ticket for this leg
        existing = TicketModel.get_by_leg_id(journey_leg_id)
        if existing and existing["status"] in ("PENDING", "ACTIVE"):
            return True, {"ticket": existing}, "An active or pending ticket already exists for this leg."

        # Authoritative fare calculation
        fare = float(leg.get("estimated_fare") or 10.0)

        # 1. Create Local Payment record (status: PENDING)
        tx_ref = f"DEMO-{secrets.token_hex(8).upper()}"
        payment = PaymentModel.create(
            user_id=user_id,
            amount=fare,
            payment_type="TICKET",
            transaction_reference=tx_ref,
            status="PENDING",
            payment_method="SIMULATED"
        )

        # 2. Create Ticket Snapshot (status: PENDING)
        ticket_token = f"TKT-{secrets.token_urlsafe(24)}"
        ticket = TicketModel.create(
            user_id=user_id,
            journey_id=journey_id,
            journey_leg_id=journey_leg_id,
            payment_id=payment["payment_id"],
            ticket_token=ticket_token,
            origin=leg["from_name"],
            destination=leg["to_name"],
            fare=fare,
            status="PENDING"
        )
        ticket["payment"] = payment

        return True, {"ticket": ticket, "payment": payment}, "Ticket created in pending state. Proceed to payment."

    @staticmethod
    def get_ticket_details(ticket_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve ticket ensuring user ownership."""
        ticket = TicketModel.get_by_id(ticket_id)
        if not ticket or ticket["user_id"] != user_id:
            return None
        return ticket

    @staticmethod
    def list_user_tickets(user_id: str, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List tickets for a user."""
        return TicketModel.list_by_user_id(user_id, status=status, limit=limit, offset=offset)

    @staticmethod
    def cancel_ticket(ticket_id: str, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Cancel a ticket if eligible (pre-validity window).
        Transitions ticket to CANCELLED and associated payment to REFUNDED.
        """
        ticket = TicketModel.get_by_id(ticket_id)
        if not ticket or ticket["user_id"] != user_id:
            return False, None, "Ticket not found or unauthorized."

        if ticket["status"] == "USED":
            return False, None, "Completed or used tickets cannot be cancelled or refunded."
        if ticket["status"] == "EXPIRED":
            return False, None, "Expired tickets cannot be cancelled."
        if ticket["status"] == "CANCELLED":
            return False, None, "Ticket is already cancelled."

        cancelled = TicketModel.cancel(ticket_id, user_id)
        if not cancelled:
            return False, None, "Ticket is no longer eligible for cancellation (validity period already active)."

        # Update payment status to REFUNDED
        PaymentModel.update_status(ticket["payment_id"], status="REFUNDED")

        return True, cancelled, "Ticket cancelled and refund initiated successfully."
