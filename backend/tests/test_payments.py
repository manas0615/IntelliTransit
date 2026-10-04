"""
IntelliTransit - Payment Service & Route Tests (Simulated Demo Payments)
"""

import pytest
import uuid
from app.models.journey import JourneyModel
from app.models.journey_leg import JourneyLegModel


@pytest.fixture
def auth_user(client):
    email = f"pay_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "Payment Tester",
        "email": email,
        "password": "Password123!"
    })
    data = reg.get_json()["data"]
    return {"user_id": data["user"]["user_id"], "token": data["token"]}


@pytest.fixture
def other_user(client):
    email = f"other_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "Other Tester",
        "email": email,
        "password": "Password123!"
    })
    data = reg.get_json()["data"]
    return {"user_id": data["user"]["user_id"], "token": data["token"]}


def test_payment_order_and_simulated_confirmation_for_pass(client, auth_user):
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Purchase a pass in PENDING state
    pass_resp = client.post('/api/passes', json={
        "pass_type": "DAILY"
    }, headers=headers)
    assert pass_resp.status_code == 201
    pass_data = pass_resp.get_json()["data"]
    pass_id = pass_data["pass"]["pass_id"]
    initial_payment = pass_data.get("payment", {})
    payment_id = initial_payment.get("payment_id")
    tx_ref = initial_payment.get("transaction_reference")

    # 2. If order not already created, call create-order
    if not payment_id or not tx_ref:
        order_resp = client.post('/api/payments/create-order', json={
            "item_type": "PASS",
            "item_id": pass_id
        }, headers=headers)
        assert order_resp.status_code == 201
        order_data = order_resp.get_json()["data"]
        payment_id = order_data["payment_id"]
        tx_ref = order_data["transaction_reference"]
        assert order_data["amount"] == 50.00

    # 3. Confirm simulated payment
    confirm_resp = client.post('/api/payments/confirm', json={
        "payment_id": payment_id,
        "transaction_reference": tx_ref
    }, headers=headers)
    assert confirm_resp.status_code == 200
    confirm_data = confirm_resp.get_json()["data"]
    assert confirm_data["payment_status"] == "SUCCESS"

    # 4. Check pass is now ACTIVE
    pass_check = client.get(f'/api/passes/{pass_id}', headers=headers)
    assert pass_check.status_code == 200
    assert pass_check.get_json()["data"]["pass"]["status"] == "ACTIVE"


def test_duplicate_payment_confirmation_rejected(client, auth_user):
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create pass
    pass_resp = client.post('/api/passes', json={"pass_type": "WEEKLY"}, headers=headers)
    assert pass_resp.status_code == 201
    pass_data = pass_resp.get_json()["data"]
    payment_id = pass_data["payment"]["payment_id"]
    tx_ref = pass_data["payment"]["transaction_reference"]

    # First confirmation succeeds
    resp1 = client.post('/api/payments/confirm', json={
        "payment_id": payment_id,
        "transaction_reference": tx_ref
    }, headers=headers)
    assert resp1.status_code == 200

    # Duplicate confirmation must be rejected
    resp2 = client.post('/api/payments/confirm', json={
        "payment_id": payment_id,
        "transaction_reference": tx_ref
    }, headers=headers)
    assert resp2.status_code in (400, 409)
    err = resp2.get_json()
    assert "error" in err


def test_payment_ownership_validation(client, auth_user, other_user):
    user1_headers = {"Authorization": f"Bearer {auth_user['token']}"}
    user2_headers = {"Authorization": f"Bearer {other_user['token']}"}

    # User 1 creates a pass
    pass_resp = client.post('/api/passes', json={"pass_type": "DAILY"}, headers=user1_headers)
    payment_id = pass_resp.get_json()["data"]["payment"]["payment_id"]
    tx_ref = pass_resp.get_json()["data"]["payment"]["transaction_reference"]

    # User 2 attempts to confirm User 1's payment -> 403 Forbidden
    steal_resp = client.post('/api/payments/confirm', json={
        "payment_id": payment_id,
        "transaction_reference": tx_ref
    }, headers=user2_headers)
    assert steal_resp.status_code == 403


def test_payment_history(client, auth_user):
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get('/api/payments', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "payments" in data
    assert isinstance(data["payments"], list)
