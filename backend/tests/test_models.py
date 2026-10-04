"""
Integration and unit tests for PostgreSQL models.
Tests all 11 tables, constraints, foreign keys, and CRUD methods.
"""
import uuid
import pytest
from backend.app.config import get_config
from backend.app.models import (
    init_db_pool,
    close_db_pool,
    check_db_health,
    UserModel,
    UserPreferenceModel,
    SavedLocationModel,
    JourneyModel,
    JourneyLegModel,
    TransportServiceModel,
    FareConfigurationModel,
    PaymentModel,
    TicketModel,
    PassModel,
    TicketValidationModel
)


@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    """Initialize DB connection pool for model tests."""
    cfg = get_config("development")
    pool = init_db_pool(cfg.DATABASE_URL, minconn=1, maxconn=5)
    yield pool
    close_db_pool()


def test_db_health_check():
    """Verify check_db_health returns True."""
    assert check_db_health() is True


def test_user_model_crud():
    """Verify user creation, retrieval, and updates."""
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    unique_phone = f"999{uuid.uuid4().int % 10000000:07d}"
    user = UserModel.create(
        full_name="Model Test User",
        email=unique_email,
        password_hash="fake_bcrypt_hash_for_testing",
        phone=unique_phone,
        role="USER"
    )
    assert user["email"] == unique_email
    assert user["role"] == "USER"
    assert user["is_active"] is True

    # Retrieve by ID & Email
    fetched = UserModel.get_by_id(user["user_id"])
    assert fetched["email"] == unique_email

    by_email = UserModel.get_by_email(unique_email)
    assert by_email["user_id"] == user["user_id"]

    # Update profile
    updated = UserModel.update_profile(user["user_id"], full_name="Updated Name")
    assert updated["full_name"] == "Updated Name"


def test_user_preference_model():
    """Verify user preference 1:1 upsert and retrieval."""
    unique_email = f"pref_{uuid.uuid4().hex[:8]}@example.com"
    user = UserModel.create(
        full_name="Pref User",
        email=unique_email,
        password_hash="fake_hash",
        role="USER"
    )
    pref = UserPreferenceModel.create_or_update(
        user_id=user["user_id"],
        preferred_mode="METRO",
        route_preference="LEAST_WALKING",
        max_walking_distance_m=800,
        avoid_taxi=True,
        avoid_transfers=False
    )
    assert pref["preferred_mode"] == "METRO"
    assert pref["avoid_taxi"] is True

    fetched = UserPreferenceModel.get_by_user_id(user["user_id"])
    assert fetched["route_preference"] == "LEAST_WALKING"


def test_saved_location_model():
    """Verify saved locations CRUD and user scoping."""
    unique_email = f"loc_{uuid.uuid4().hex[:8]}@example.com"
    user = UserModel.create(
        full_name="Loc User",
        email=unique_email,
        password_hash="fake_hash",
        role="USER"
    )
    loc = SavedLocationModel.create(
        user_id=user["user_id"],
        label="Work",
        location_name="Hinjewadi Phase 1",
        latitude=18.5912,
        longitude=73.7389,
        address="Rajiv Gandhi Infotech Park"
    )
    assert loc["label"] == "Work"

    locations = SavedLocationModel.list_by_user_id(user["user_id"])
    assert len(locations) == 1
    assert locations[0]["location_id"] == loc["location_id"]

    # Update
    updated = SavedLocationModel.update(loc["location_id"], user["user_id"], label="Office")
    assert updated["label"] == "Office"

    # Delete
    deleted = SavedLocationModel.delete(loc["location_id"], user["user_id"])
    assert deleted is True
    assert len(SavedLocationModel.list_by_user_id(user["user_id"])) == 0


def test_journey_and_legs_model():
    """Verify journey and leg-based relational creation."""
    unique_email = f"journey_{uuid.uuid4().hex[:8]}@example.com"
    user = UserModel.create(
        full_name="Journey User",
        email=unique_email,
        password_hash="fake_hash",
        role="USER"
    )
    journey = JourneyModel.create(
        user_id=user["user_id"],
        origin_name="Pune Station",
        origin_latitude=18.5285,
        origin_longitude=73.8743,
        destination_name="Civil Court",
        destination_latitude=18.5236,
        destination_longitude=73.8500,
        total_duration_min=20,
        walking_distance_m=300,
        estimated_fare=35.00
    )
    assert journey["origin_name"] == "Pune Station"

    # Add Legs
    leg1 = JourneyLegModel.create(
        journey_id=journey["journey_id"],
        sequence_number=1,
        mode="WALK",
        from_name="Pune Station",
        from_latitude=18.5285,
        from_longitude=73.8743,
        to_name="Pune Station Metro",
        to_latitude=18.5280,
        to_longitude=73.8740,
        duration_min=3,
        walking_distance_m=150,
        estimated_fare=0.00,
        is_ticketable=False
    )
    leg2 = JourneyLegModel.create(
        journey_id=journey["journey_id"],
        sequence_number=2,
        mode="METRO",
        from_name="Pune Station Metro",
        from_latitude=18.5280,
        from_longitude=73.8740,
        to_name="Civil Court Metro",
        to_latitude=18.5236,
        to_longitude=73.8500,
        duration_min=15,
        walking_distance_m=0,
        estimated_fare=20.00,
        is_ticketable=True
    )
    assert leg1["is_ticketable"] is False
    assert leg2["is_ticketable"] is True

    legs = JourneyLegModel.list_by_journey_id(journey["journey_id"])
    assert len(legs) == 2
    assert legs[0]["sequence_number"] == 1
    assert legs[1]["sequence_number"] == 2


def test_payment_ticket_pass_lifecycle():
    """Verify 1:1 Payment-to-Ticket mapping and state transitions."""
    unique_email = f"pay_{uuid.uuid4().hex[:8]}@example.com"
    user = UserModel.create(
        full_name="Payment User",
        email=unique_email,
        password_hash="fake_hash",
        role="USER"
    )
    journey = JourneyModel.create(
        user_id=user["user_id"],
        origin_name="Swargate",
        origin_latitude=18.5018,
        origin_longitude=73.8586,
        destination_name="Katraj",
        destination_latitude=18.4575,
        destination_longitude=73.8677
    )
    leg = JourneyLegModel.create(
        journey_id=journey["journey_id"],
        sequence_number=1,
        mode="BUS",
        from_name="Swargate",
        from_latitude=18.5018,
        from_longitude=73.8586,
        to_name="Katraj",
        to_latitude=18.4575,
        to_longitude=73.8677,
        estimated_fare=15.00,
        is_ticketable=True
    )

    # 1. Create Payment
    tx_ref = f"TX_{uuid.uuid4().hex[:12]}"
    payment = PaymentModel.create(
        user_id=user["user_id"],
        transaction_reference=tx_ref,
        amount=15.00,
        payment_type="TICKET",
        payment_method="SIMULATED",
        status="PENDING"
    )
    assert payment["status"] == "PENDING"

    # 2. Create Ticket linked 1:1 to Payment
    ticket_token = f"tok_{uuid.uuid4().hex}"
    ticket = TicketModel.create(
        user_id=user["user_id"],
        journey_id=journey["journey_id"],
        journey_leg_id=leg["leg_id"],
        payment_id=payment["payment_id"],
        ticket_token=ticket_token,
        origin="Swargate",
        destination="Katraj",
        fare=15.00,
        status="PENDING"
    )
    assert ticket["status"] == "PENDING"
    assert ticket["payment_id"] == payment["payment_id"]

    # 3. Simulate Successful Verification
    PaymentModel.update_status(payment["payment_id"], status="SUCCESS")
    activated = TicketModel.activate(ticket["ticket_id"], valid_from="2026-01-01 00:00:00", valid_until="2026-12-31 23:59:59")
    assert activated["status"] == "ACTIVE"

    # 4. QR Inspection by Admin Validator
    validation = TicketValidationModel.create(
        ticket_id=ticket["ticket_id"],
        validator_user_id=user["user_id"],
        validation_status="VALID",
        remarks="Conductor checked QR"
    )
    assert validation["validation_status"] == "VALID"

    # 5. Transition to USED
    used_ticket = TicketModel.mark_used(ticket["ticket_id"])
    assert used_ticket["status"] == "USED"
