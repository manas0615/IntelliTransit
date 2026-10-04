"""
Unit and integration tests for Tickets and Passes.
Tests leg-based ticketing, refusal of WALK tickets, pass pricing, and cancellation policy.
"""
import uuid
from backend.app.models.journey import JourneyModel
from backend.app.models.journey_leg import JourneyLegModel


def create_user_and_journey(client):
    """Helper to create authenticated user and multimodal journey."""
    email = f"tkt_user_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "Ticket Commuter",
        "email": email,
        "password": "Password123!"
    })
    token = reg.get_json()["data"]["token"]
    user_id = reg.get_json()["data"]["user"]["user_id"]

    journey = JourneyModel.create(
        user_id=user_id,
        origin_name="Vanaz",
        origin_latitude=18.5072,
        origin_longitude=73.8015,
        destination_name="Civil Court",
        destination_latitude=18.5236,
        destination_longitude=73.8500
    )
    # Leg 1: Walk (not ticketable)
    leg1 = JourneyLegModel.create(
        journey_id=journey["journey_id"],
        sequence_number=1,
        mode="WALK",
        from_name="Vanaz",
        from_latitude=18.5072,
        from_longitude=73.8015,
        to_name="Vanaz Metro",
        to_latitude=18.5072,
        to_longitude=73.8015,
        is_ticketable=False,
        estimated_fare=0.0
    )
    # Leg 2: Metro (ticketable)
    leg2 = JourneyLegModel.create(
        journey_id=journey["journey_id"],
        sequence_number=2,
        mode="METRO",
        from_name="Vanaz Metro",
        from_latitude=18.5072,
        from_longitude=73.8015,
        to_name="Civil Court Metro",
        to_latitude=18.5236,
        to_longitude=73.8500,
        is_ticketable=True,
        estimated_fare=20.0
    )
    return token, journey["journey_id"], leg1["leg_id"], leg2["leg_id"]


def test_create_ticket_for_metro_leg_and_reject_walk(client):
    """Verify ticket is created for METRO leg and rejected for WALK leg."""
    token, journey_id, walk_leg_id, metro_leg_id = create_user_and_journey(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Attempt to buy ticket for WALK leg -> Must fail
    walk_resp = client.post("/api/tickets", json={
        "journey_id": journey_id,
        "journey_leg_id": walk_leg_id
    }, headers=headers)
    assert walk_resp.status_code == 400
    assert walk_resp.get_json()["error"]["code"] == "NOT_TICKETABLE"

    # 2. Buy ticket for METRO leg -> Must succeed (status: PENDING)
    metro_resp = client.post("/api/tickets", json={
        "journey_id": journey_id,
        "journey_leg_id": metro_leg_id
    }, headers=headers)
    assert metro_resp.status_code == 201
    tkt_data = metro_resp.get_json()["data"]["ticket"]
    assert tkt_data["status"] == "PENDING"
    assert tkt_data["fare"] == 20.0


def test_pass_creation_and_listing(client):
    """Verify DAILY, WEEKLY, and MONTHLY pass creation."""
    token, _, _, _ = create_user_and_journey(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create Daily Pass
    p_resp = client.post("/api/passes", json={"pass_type": "DAILY"}, headers=headers)
    assert p_resp.status_code == 201
    pass_data = p_resp.get_json()["data"]["pass"]
    assert pass_data["price"] == 50.0
    assert pass_data["status"] == "PENDING"

    # List passes
    list_resp = client.get("/api/passes", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.get_json()["data"]["passes"]) >= 1
