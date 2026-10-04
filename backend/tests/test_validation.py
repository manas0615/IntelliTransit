"""
Unit & Integration Tests for Ticket and Pass Validation Engine.
Tests single-use ticket consumption, double-scan prevention, and QR generation.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from app.models.journey import JourneyModel
from app.models.journey_leg import JourneyLegModel
from app.models.ticket import TicketModel
from app.models.pass_model import PassModel


@pytest.fixture
def auth_user(client):
    email = f"validator_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "Ticket Inspector",
        "email": email,
        "password": "Password123!"
    })
    data = reg.get_json()["data"]
    return {"user_id": data["user"]["user_id"], "token": data["token"]}


def test_ticket_validation_flow(client, auth_user):
    token = auth_user["token"]
    user_id = auth_user["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Journey and Bus Leg
    journey = JourneyModel.create(
        user_id=user_id,
        origin_name="Swargate",
        origin_latitude=18.5018,
        origin_longitude=73.8580,
        destination_name="Shivajinagar",
        destination_latitude=18.5314,
        destination_longitude=73.8446
    )
    leg = JourneyLegModel.create(
        journey_id=journey["journey_id"],
        sequence_number=1,
        mode="BUS",
        from_name="Swargate",
        from_latitude=18.5018,
        from_longitude=73.8580,
        to_name="Shivajinagar",
        to_latitude=18.5314,
        to_longitude=73.8446,
        estimated_fare=20.00,
        is_ticketable=True
    )

    # 2. Purchase ticket
    tkt_resp = client.post("/api/tickets", json={
        "journey_id": journey["journey_id"],
        "journey_leg_id": leg["leg_id"]
    }, headers=headers)
    assert tkt_resp.status_code == 201
    ticket_id = tkt_resp.get_json()["data"]["ticket"]["ticket_id"]

    # 3. Simulate payment verification to make ticket ACTIVE
    now = datetime.now()
    valid_from = now.strftime("%Y-%m-%d %H:%M:%S")
    valid_until = (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")
    TicketModel.activate(ticket_id, valid_from, valid_until)

    ticket = TicketModel.get_by_id(ticket_id)
    ticket_token = ticket["ticket_token"]

    # 4. Request QR code
    qr_resp = client.get(f"/api/tickets/{ticket_id}/qr", headers=headers)
    assert qr_resp.status_code == 200
    qr_data = qr_resp.get_json()["data"]
    assert qr_data["qr_data_uri"].startswith("data:image/png;base64,")

    # 5. First scan -> Success, marked as USED
    val_resp1 = client.post("/api/validation/validate", json={
        "token": ticket_token
    }, headers=headers)
    assert val_resp1.status_code == 200
    assert val_resp1.get_json()["data"]["validation_status"] == "VALID"

    # 6. Second scan -> Fail with ALREADY_USED
    val_resp2 = client.post("/api/validation/validate", json={
        "token": ticket_token
    }, headers=headers)
    assert val_resp2.status_code == 400
    error_data = val_resp2.get_json()
    assert error_data["error"]["code"] == "ALREADY_USED"


def test_pass_validation_flow(client, auth_user):
    token = auth_user["token"]
    user_id = auth_user["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Purchase Pass
    pass_resp = client.post("/api/passes", json={
        "pass_type": "DAILY"
    }, headers=headers)
    assert pass_resp.status_code == 201
    pass_id = pass_resp.get_json()["data"]["pass"]["pass_id"]

    # 2. Activate Pass
    now = datetime.now()
    valid_from = now.strftime("%Y-%m-%d %H:%M:%S")
    valid_until = (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    pass_token = f"PASS-DAILY-{pass_id[:8]}"
    PassModel.activate(pass_id, pass_token, valid_from, valid_until)

    # 3. Validate Pass (First Scan) -> Success
    v1 = client.post("/api/validation/validate", json={"token": pass_token}, headers=headers)
    assert v1.status_code == 200
    assert v1.get_json()["data"]["type"] == "PASS"

    # 4. Validate Pass (Second Scan) -> Still Success (Unlimited rides within window)
    v2 = client.post("/api/validation/validate", json={"token": pass_token}, headers=headers)
    assert v2.status_code == 200
    assert v2.get_json()["data"]["type"] == "PASS"
