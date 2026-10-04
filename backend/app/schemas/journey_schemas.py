"""
Journey planning request validation schemas.
"""
from marshmallow import Schema, fields, validate


class LocationPointSchema(Schema):
    """Validation schema for geographic origin/destination."""
    name = fields.String(
        required=True,
        validate=[validate.Length(min=1, max=150, error="Location name must not exceed 150 characters.")]
    )
    latitude = fields.Float(
        required=True,
        validate=[validate.Range(min=-90.0, max=90.0, error="Latitude must be between -90 and 90.")]
    )
    longitude = fields.Float(
        required=True,
        validate=[validate.Range(min=-180.0, max=180.0, error="Longitude must be between -180 and 180.")]
    )


class JourneyPreferencesInputSchema(Schema):
    """Validation schema for user/guest route preferences in journey query."""
    route_preference = fields.String(
        required=False,
        load_default="FASTEST",
        validate=[validate.OneOf(["FASTEST", "CHEAPEST", "LEAST_WALKING", "FEWEST_TRANSFERS", "BALANCED"])]
    )
    max_walking_distance_m = fields.Integer(
        required=False,
        allow_none=True,
        validate=[validate.Range(min=0, max=20000, error="Max walking distance must be non-negative.")]
    )
    avoid_taxi = fields.Boolean(required=False, load_default=False)
    avoid_transfers = fields.Boolean(required=False, load_default=False)
    preferred_mode = fields.String(
        required=False,
        allow_none=True,
        validate=[validate.OneOf(["BUS", "METRO", "TAXI"])]
    )


class PlanJourneyRequestSchema(Schema):
    """Validation schema for POST /api/journeys/plan."""
    origin = fields.Nested(LocationPointSchema, required=True)
    destination = fields.Nested(LocationPointSchema, required=True)
    departure_time = fields.DateTime(required=False, allow_none=True)
    preferences = fields.Nested(JourneyPreferencesInputSchema, required=False)
