"""
Integration and API tests for Authentication endpoints (/api/auth/*).
"""
import uuid


def test_register_and_login_flow(client):
    """Verify user registration, login, and token-based /api/auth/me retrieval."""
    unique_email = f"api_user_{uuid.uuid4().hex[:8]}@example.com"
    unique_phone = f"987{uuid.uuid4().int % 10000000:07d}"
    reg_payload = {
        "full_name": "API Tester",
        "email": unique_email,
        "password": "Password123!",
        "phone": unique_phone
    }
    # 1. Register
    reg_resp = client.post("/api/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.get_json()
    assert reg_data["success"] is True
    assert "token" in reg_data["data"]

    # 2. Duplicate registration rejected with 409
    dup_resp = client.post("/api/auth/register", json=reg_payload)
    assert dup_resp.status_code == 409

    # 3. Login
    login_resp = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.get_json()["data"]["token"]

    # 4. Access protected /api/auth/me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.get_json()["data"]["user"]["email"] == unique_email


def test_auth_rejections(client):
    """Verify missing, invalid, and expired token rejections."""
    # Missing token
    resp1 = client.get("/api/auth/me")
    assert resp1.status_code == 401

    # Malformed token
    resp2 = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp2.status_code == 401
