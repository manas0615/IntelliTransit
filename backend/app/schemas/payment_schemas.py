"""
Payment request validation schemas for Simulated Demo Payments.
"""
from marshmallow import Schema, fields


class CreatePaymentOrderSchema(Schema):
    """Validation schema for POST /api/payments/create-order."""
    item_type = fields.String(required=False)
    item_id = fields.UUID(required=False, allow_none=True)
    ticket_id = fields.UUID(required=False, allow_none=True)
    pass_id = fields.UUID(required=False, allow_none=True)


class ConfirmPaymentSchema(Schema):
    """Validation schema for POST /api/payments/confirm."""
    payment_id = fields.UUID(required=False, allow_none=True)
    transaction_reference = fields.String(required=False, allow_none=True)


# Backwards compatibility alias
VerifyPaymentSchema = ConfirmPaymentSchema
