"""
Ticket and Pass request validation schemas.
"""
from marshmallow import Schema, fields, validate


class CreateTicketRequestSchema(Schema):
    """Validation schema for POST /api/tickets (Leg-based ticket creation)."""
    journey_id = fields.UUID(required=True, error_messages={"invalid": "Invalid journey UUID format."})
    journey_leg_id = fields.UUID(required=True, error_messages={"invalid": "Invalid journey leg UUID format."})


class CreatePassRequestSchema(Schema):
    """Validation schema for POST /api/passes."""
    pass_type = fields.String(
        required=True,
        validate=[validate.OneOf(["DAILY", "WEEKLY", "MONTHLY"], error="Pass type must be DAILY, WEEKLY, or MONTHLY.")]
    )


class ValidateTicketTokenSchema(Schema):
    """Validation schema for POST /api/validation/tickets."""
    token = fields.String(
        required=True,
        validate=[validate.Length(min=8, max=255, error="Token must be a valid ticket token string.")]
    )
    remarks = fields.String(required=False, allow_none=True)
