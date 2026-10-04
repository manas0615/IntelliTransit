"""
Ticket & Pass Validation Engine.
Handles QR token scanning, single-use ticket consumption (ACTIVE -> USED),
pass validity checks, and append-only audit logging in ticket_validations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from backend.app.models.ticket import TicketModel
from backend.app.models.pass_model import PassModel
from backend.app.models.ticket_validation import TicketValidationModel
from backend.app.models.db import get_db_connection, fetch_one


class ValidationService:
    """Core validation engine for station gates, bus conductors, and inspectors."""

    @staticmethod
    def validate_token(
        validator_user_id: str,
        token_str: str,
        remarks: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any], str]:
        """
        Validate a scanned QR code token string (Ticket or Pass).
        Enforces single-use consumption for tickets and time-window validity for passes.
        """
        token_clean = token_str.strip()
        now = datetime.now()

        # Check if it's a Pass token
        if token_clean.startswith("PASS-") or "PASS" in token_clean.upper():
            pass_item = PassModel.get_by_token(token_clean)
            if not pass_item:
                # Try finding pass by pass_id
                pass_item = PassModel.get_by_id(token_clean)

            if not pass_item:
                return False, {"code": "INVALID_TOKEN", "type": "PASS"}, "Invalid pass token."

            # Check status
            if pass_item["status"] != "ACTIVE":
                return False, {
                    "code": f"PASS_{pass_item['status']}",
                    "type": "PASS",
                    "status": pass_item["status"]
                }, f"Pass is {pass_item['status']} (not ACTIVE)."

            # Check validity window
            valid_until = pass_item.get("valid_until")
            if valid_until and isinstance(valid_until, datetime) and now > valid_until:
                return False, {"code": "PASS_EXPIRED", "type": "PASS", "valid_until": str(valid_until)}, "Pass has expired."

            return True, {
                "type": "PASS",
                "validation_status": "SUCCESS",
                "item": pass_item,
                "pass_type": pass_item["pass_type"],
                "applicable_mode": pass_item.get("applicable_mode", "BUS/METRO"),
                "valid_until": str(pass_item.get("valid_until"))
            }, "Pass is valid and active."

        # Otherwise treat as Ticket token
        ticket = TicketModel.get_by_token(token_clean)
        if not ticket:
            ticket = TicketModel.get_by_id(token_clean)

        if not ticket:
            return False, {"code": "INVALID_TOKEN", "type": "TICKET"}, "Invalid ticket token or ticket not found."

        ticket_id = ticket["ticket_id"]
        status = ticket["status"]

        # Check already used
        if status == "USED":
            TicketValidationModel.create(
                ticket_id=ticket_id,
                validator_user_id=validator_user_id,
                validation_status="INVALID",
                remarks=remarks or "Attempted re-scan of consumed ticket"
            )
            return False, {
                "code": "ALREADY_USED",
                "type": "TICKET",
                "ticket_id": ticket_id,
                "status": status
            }, "Ticket has ALREADY been used. Entry denied."

        # Check non-active statuses
        if status != "ACTIVE":
            val_stat = "CANCELLED" if status == "CANCELLED" else "INVALID"
            TicketValidationModel.create(
                ticket_id=ticket_id,
                validator_user_id=validator_user_id,
                validation_status=val_stat,
                remarks=remarks or f"Ticket status is {status}"
            )
            return False, {
                "code": f"TICKET_{status}",
                "type": "TICKET",
                "ticket_id": ticket_id,
                "status": status
            }, f"Ticket cannot be validated. Current status: {status}."

        # Check validity window
        valid_until = ticket.get("valid_until")
        if valid_until and isinstance(valid_until, datetime) and now > valid_until:
            TicketValidationModel.create(
                ticket_id=ticket_id,
                validator_user_id=validator_user_id,
                validation_status="EXPIRED",
                remarks=remarks or "Ticket validity window expired"
            )
            return False, {
                "code": "TICKET_EXPIRED",
                "type": "TICKET",
                "ticket_id": ticket_id,
                "valid_until": str(valid_until)
            }, "Ticket has expired."

        # Atomic State Transition: ACTIVE -> USED
        with get_db_connection():
            updated_ticket = TicketModel.mark_used(ticket_id)
            validation_entry = TicketValidationModel.create(
                ticket_id=ticket_id,
                validator_user_id=validator_user_id,
                validation_status="VALID",
                remarks=remarks or "Ticket scanned and marked as USED"
            )

        return True, {
            "type": "TICKET",
            "validation_status": "VALID",
            "ticket": updated_ticket,
            "origin": ticket.get("origin"),
            "destination": ticket.get("destination"),
            "mode": ticket.get("mode"),
            "operator": ticket.get("operator_name") or ticket.get("service_name"),
            "fare": float(ticket.get("fare", 0.0)),
            "validation_time": str(validation_entry.get("validation_time", now))
        }, "Ticket successfully validated and consumed."

    @staticmethod
    def get_recent_validations(limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent validation log for audit and conductor overview."""
        return TicketValidationModel.list_recent(limit=limit)

    @staticmethod
    def get_ticket_history(ticket_id: str) -> List[Dict[str, Any]]:
        """Get validation logs for a specific ticket."""
        return TicketValidationModel.list_by_ticket_id(ticket_id)
