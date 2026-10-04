"""
User profile, preferences, and saved location validation schemas.
"""
from marshmallow import Schema, fields, validate


class ProfileUpdateSchema(Schema):
    """Validation schema for PUT /api/users/profile."""
    full_name = fields.String(
        required=False,
        validate=[validate.Length(min=2, max=100, error="Full name must be between 2 and 100 characters.")]
    )
    phone = fields.String(
        required=False,
        allow_none=True,
        validate=[validate.Regexp(r"^[6-9]\d{9}$", error="Phone must be a valid 10-digit Indian mobile number.")]
    )


class PreferencesUpdateSchema(Schema):
    """Validation schema for PUT /api/users/preferences."""
    preferred_mode = fields.String(
        required=False,
        allow_none=True,
        validate=[validate.OneOf(["BUS", "METRO", "TAXI"])]
    )
    route_preference = fields.String(
        required=False,
        allow_none=True,
        validate=[validate.OneOf(["FASTEST", "CHEAPEST", "LEAST_WALKING", "FEWEST_TRANSFERS", "BALANCED"])]
    )
    max_walking_distance_m = fields.Integer(
        required=False,
        allow_none=True,
        validate=[validate.Range(min=0, max=20000)]
    )
    avoid_taxi = fields.Boolean(required=False)
    avoid_transfers = fields.Boolean(required=False)


class SavedLocationCreateSchema(Schema):
    """Validation schema for POST /api/users/locations."""
    label = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=50, error="Label must not exceed 50 characters.")]
    )
    location_name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=150, error="Location name must not exceed 150 characters.")]
    )
    address = fields.String(required=False, allow_none=True)
    latitude = fields.Float(
        required=True,
        validate=[validate.Range(min=-90.0, max=90.0)]
    )
    longitude = fields.Float(
        required=True,
        validate=[validate.Range(min=-180.0, max=180.0)]
    )


class SavedLocationUpdateSchema(Schema):
    """Validation schema for PUT /api/users/locations/<id>."""
    label = fields.String(required=False, validate=[validate.Length(min=1, max=50)])
    location_name = fields.String(required=False, validate=[validate.Length(min=1, max=150)])
    address = fields.String(required=False, allow_none=True)
    latitude = fields.Float(required=False, validate=[validate.Range(min=-90.0, max=90.0)])
    longitude = fields.Float(required=False, validate=[validate.Range(min=-180.0, max=180.0)])
