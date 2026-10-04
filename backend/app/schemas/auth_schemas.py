"""
Authentication request validation schemas.
"""
from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    """Validation schema for user registration."""
    full_name = fields.String(
        required=True,
        validate=[validate.Length(min=2, max=100, error="Full name must be between 2 and 100 characters.")]
    )
    email = fields.Email(
        required=True,
        validate=[validate.Length(max=255, error="Email must not exceed 255 characters.")]
    )
    phone = fields.String(
        required=False,
        allow_none=True,
        validate=[validate.Regexp(r"^[6-9]\d{9}$", error="Phone must be a valid 10-digit Indian mobile number.")]
    )
    password = fields.String(
        required=True,
        validate=[validate.Length(min=8, max=128, error="Password must be at least 8 characters long.")]
    )


class LoginSchema(Schema):
    """Validation schema for user login."""
    email = fields.Email(required=True)
    password = fields.String(required=True)


class PasswordChangeSchema(Schema):
    """Validation schema for changing password."""
    current_password = fields.String(required=True)
    new_password = fields.String(
        required=True,
        validate=[validate.Length(min=8, max=128, error="New password must be at least 8 characters long.")]
    )
