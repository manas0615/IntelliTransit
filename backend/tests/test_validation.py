"""
Unit & Integration Tests for Ticket and Pass Validation Engine.
Tests single-use ticket consumption, double-scan prevention, QR generation,
and RBAC enforcement on conductor validation endpoints.
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
    email = f"commuter_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "Test Commuter",
        "email": email,
        "password": "Password123!"
    })
    data = reg.get_json()["data"]
    return {"user_id": data["user"]["user_id"], "token": data["token"]}


@pytest.fixture
def conductor_headers(client):
    login = client.post("/api/auth/login", json={
        "email": "conductor@intellitransit.com",
        "password": "ConductorPassword123!"
    })
    token = login.get_json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_cannot_access_validator(client, auth_user):
    """Ensure standard commuter accounts cannot access validator endpoints."""
    headers = {"Authorization": f"Bearer {auth_user['token']}"}
    resp1 = client.post("/api/validation/validate", json={"token": "TKT-FAKE"}, headers=headers)
    assert resp1.status_code == 403

    resp2 = client.get("/api/validation/history", headers=headers)
    assert resp2.status_code == 403


def test_admin_can_access_validator(client, conductor_headers):
    """Ensure authorized staff/admin accounts can access validator endpoints."""
    resp = client.get("/api/validation/history", headers=conductor_headers)
    assert resp.status_code == 200


def test_ticket_validation_flow(client, auth_user, conductor_headers):
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

    # 4. Request QR code (commuter can fetch their own QR code)
    qr_resp = client.get(f"/api/tickets/{ticket_id}/qr", headers=headers)
    assert qr_resp.status_code == 200
    qr_data = qr_resp.get_json()["data"]
    assert qr_data["qr_data_uri"].startswith("data:image/png;base64,")

    # 5. Commuter attempts to scan/validate -> Rejection with 403 Forbidden
    val_unauth = client.post("/api/validation/validate", json={
        "token": ticket_token
    }, headers=headers)
    assert val_unauth.status_code == 403

    # 6. Conductor scan -> Success, marked as USED
    val_resp1 = client.post("/api/validation/validate", json={
        "token": ticket_token
    }, headers=conductor_headers)
    assert val_resp1.status_code == 200
    assert val_resp1.get_json()["data"]["validation_status"] == "VALID"

    # 7. Second scan -> Fail with ALREADY_USED
    val_resp2 = client.post("/api/validation/validate", json={
        "token": ticket_token
    }, headers=conductor_headers)
    assert val_resp2.status_code == 400
    error_data = val_resp2.get_json()
    assert error_data["error"]["code"] == "ALREADY_USED"


def test_pass_validation_flow(client, auth_user, conductor_headers):
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

    # 3. Conductor validates pass (First Scan) -> Success
    v1 = client.post("/api/validation/validate", json={"token": pass_token}, headers=conductor_headers)
    assert v1.status_code == 200
    assert v1.get_json()["data"]["type"] == "PASS"

    # 4. Conductor validates pass (Second Scan) -> Still Success (Unlimited rides within window)
    v2 = client.post("/api/validation/validate", json={"token": pass_token}, headers=conductor_headers)
    assert v2.status_code == 200
    assert v2.get_json()["data"]["type"] == "PASS"
