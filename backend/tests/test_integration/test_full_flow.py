"""
IntelliTransit End-to-End Multimodal Lifecycle Integration Test.
Verifies the complete journey:
1. Registration & Authentication
2. Multimodal Journey Planning (OTP / Intelligence Layer)
3. Ticketable Leg Selection
4. Simulated Demo Payment Order & Authoritative Confirmation
5. Ticket QR Retrieval
6. Gate / Conductor Validation (ACTIVE -> USED)
7. Anti-Fraud Second Scan Rejection (ALREADY_USED)
"""
import pytest
import uuid
import hmac
import hashlib


def test_complete_commuter_transit_lifecycle(app, client):
    # -------------------------------------------------------------
    # 1. User Registration & JWT Authentication
    # -------------------------------------------------------------
    email = f"e2e_commuter_{uuid.uuid4().hex[:8]}@example.com"
    reg_resp = client.post("/api/auth/register", json={
        "full_name": "E2E Commuter",
        "email": email,
        "password": "SecurePassword123!"
    })
    assert reg_resp.status_code == 201
    auth_data = reg_resp.get_json()["data"]
    token = auth_data["token"]
    user_id = auth_data["user"]["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # -------------------------------------------------------------
    # 2. Plan Multimodal Journey (Kothrud to Pune Station)
    # -------------------------------------------------------------
    plan_resp = client.post("/api/journeys/plan", json={
        "origin": {
            "name": "Kothrud Stand",
            "latitude": 18.5074,
            "longitude": 73.8077
        },
        "destination": {
            "name": "Pune Railway Station",
            "latitude": 18.5285,
            "longitude": 73.8743
        },
        "preferences": {
            "route_preference": "BALANCED"
        }
    }, headers=headers)
    assert plan_resp.status_code == 200
    plan_data = plan_resp.get_json()["data"]
    journey_id = plan_data["journey_id"]
    itineraries = plan_data["itineraries"]
    assert len(itineraries) > 0

    first_itinerary = itineraries[0]
    ticketable_legs = [l for l in first_itinerary["legs"] if l.get("is_ticketable") or l.get("mode") in ("BUS", "METRO")]
    assert len(ticketable_legs) > 0
    selected_leg = ticketable_legs[0]
    leg_id = selected_leg["leg_id"]

    # -------------------------------------------------------------
    # 3. Create Leg-Based Ticket (PENDING status)
    # -------------------------------------------------------------
    tkt_resp = client.post("/api/tickets", json={
        "journey_id": journey_id,
        "journey_leg_id": leg_id
    }, headers=headers)
    assert tkt_resp.status_code == 201
    ticket = tkt_resp.get_json()["data"]["ticket"]
    ticket_id = ticket["ticket_id"]
    assert ticket["status"] == "PENDING"

    # -------------------------------------------------------------
    # 4. Simulated Demo Payment Order & Authoritative Confirmation
    # -------------------------------------------------------------
    order_resp = client.post("/api/payments/create-order", json={
        "item_type": "TICKET",
        "item_id": ticket_id
    }, headers=headers)
    assert order_resp.status_code == 201
    order_data = order_resp.get_json()["data"]
    payment_id = order_data["payment_id"]
    tx_ref = order_data["transaction_reference"]

    verify_resp = client.post("/api/payments/confirm", json={
        "payment_id": payment_id,
        "transaction_reference": tx_ref
    }, headers=headers)
    assert verify_resp.status_code == 200
    assert verify_resp.get_json()["data"]["payment_status"] == "SUCCESS"

    # Check ticket is now ACTIVE
    active_tkt_resp = client.get(f"/api/tickets/{ticket_id}", headers=headers)
    assert active_tkt_resp.status_code == 200
    active_ticket = active_tkt_resp.get_json()["data"]["ticket"]
    assert active_ticket["status"] == "ACTIVE"
    ticket_token = active_ticket["ticket_token"]

    # -------------------------------------------------------------
    # 5. Fetch Scannable QR Code Payload
    # -------------------------------------------------------------
    qr_resp = client.get(f"/api/tickets/{ticket_id}/qr", headers=headers)
    assert qr_resp.status_code == 200
    assert qr_resp.get_json()["data"]["qr_data_uri"].startswith("data:image/png;base64,")

    # -------------------------------------------------------------
    # 6. Conductor / Gate Inspection & Consumption (ACTIVE -> USED)
    # -------------------------------------------------------------
    # First verify commuter cannot perform conductor validation
    val_commuter_resp = client.post("/api/validation/validate", json={
        "token": ticket_token
    }, headers=headers)
    assert val_commuter_resp.status_code == 403

    # Authenticate as authorized conductor
    cond_login = client.post("/api/auth/login", json={
        "email": "conductor@intellitransit.com",
        "password": "ConductorPassword123!"
    })
    assert cond_login.status_code == 200
    cond_headers = {"Authorization": f"Bearer {cond_login.get_json()['data']['token']}"}

    val_resp1 = client.post("/api/validation/validate", json={
        "token": ticket_token,
        "remarks": "Gate 1 Turnstile Scan"
    }, headers=cond_headers)
    assert val_resp1.status_code == 200
    val_data = val_resp1.get_json()["data"]
    assert val_data["validation_status"] == "VALID"
    assert val_data["type"] == "TICKET"

    # Verify status in database is now USED
    used_tkt_resp = client.get(f"/api/tickets/{ticket_id}", headers=headers)
    assert used_tkt_resp.get_json()["data"]["ticket"]["status"] == "USED"

    # -------------------------------------------------------------
    # 7. Anti-Fraud: Second Scan Attempt Must Fail
    # -------------------------------------------------------------
    val_resp2 = client.post("/api/validation/validate", json={
        "token": ticket_token,
        "remarks": "Gate 2 Re-scan"
    }, headers=cond_headers)
    assert val_resp2.status_code == 400
    assert val_resp2.get_json()["error"]["code"] == "ALREADY_USED"
