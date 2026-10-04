"""
Unit tests for Marshmallow API validation schemas.
"""
import pytest
from marshmallow import ValidationError
from backend.app.schemas import (
    RegisterSchema,
    LoginSchema,
    PlanJourneyRequestSchema,
    CreateTicketRequestSchema,
    CreatePassRequestSchema,
    ValidateTicketTokenSchema,
    PreferencesUpdateSchema,
    SavedLocationCreateSchema
)


def test_register_schema_valid():
    """Valid registration payload passes validation."""
    schema = RegisterSchema()
    data = {
        "full_name": "Manas Sharma",
        "email": "manas@example.com",
        "phone": "9876543210",
        "password": "SecurePassword123!"
    }
    result = schema.load(data)
    assert result["email"] == "manas@example.com"


def test_register_schema_invalid_email():
    """Invalid email fails registration validation."""
    schema = RegisterSchema()
    with pytest.raises(ValidationError) as exc:
        schema.load({
            "full_name": "Test User",
            "email": "not-an-email",
            "password": "Password123"
        })
    assert "email" in exc.value.messages


def test_register_schema_short_password():
    """Short password fails validation."""
    schema = RegisterSchema()
    with pytest.raises(ValidationError) as exc:
        schema.load({
            "full_name": "Test User",
            "email": "test@example.com",
            "password": "short"
        })
    assert "password" in exc.value.messages


def test_plan_journey_schema_valid():
    """Valid journey planning input passes validation."""
    schema = PlanJourneyRequestSchema()
    data = {
        "origin": {"name": "Pune Station", "latitude": 18.5285, "longitude": 73.8743},
        "destination": {"name": "Shivajinagar", "latitude": 18.5314, "longitude": 73.8446},
        "preferences": {"route_preference": "CHEAPEST", "avoid_taxi": True}
    }
    result = schema.load(data)
    assert result["origin"]["name"] == "Pune Station"
    assert result["preferences"]["avoid_taxi"] is True


def test_create_pass_schema_valid():
    """Valid pass types are accepted."""
    schema = CreatePassRequestSchema()
    assert schema.load({"pass_type": "DAILY"})["pass_type"] == "DAILY"
    assert schema.load({"pass_type": "WEEKLY"})["pass_type"] == "WEEKLY"
    assert schema.load({"pass_type": "MONTHLY"})["pass_type"] == "MONTHLY"

    with pytest.raises(ValidationError):
        schema.load({"pass_type": "ANNUAL"})
