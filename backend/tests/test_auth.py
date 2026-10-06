"""
Integration and API tests for Authentication endpoints (/api/auth/*).
Includes tests for seeded accounts (Admin, Conductor, Commuter) and authentication flows.
"""
import uuid
from backend.app.models.user import UserModel


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


def test_seed_admin_account(client):
    """Verify seeded Administrator account exists and has role ADMIN."""
    user = UserModel.get_by_email("admin@intellitransit.com")
    assert user is not None
    assert user["role"] == "ADMIN"
    assert user["is_active"] is True


def test_seed_conductor_account(client):
    """Verify seeded Conductor account exists and has role ADMIN."""
    user = UserModel.get_by_email("conductor@intellitransit.com")
    assert user is not None
    assert user["role"] == "ADMIN"
    assert user["is_active"] is True


def test_seed_commuter_account(client):
    """Verify seeded Commuter account exists and has role USER."""
    user = UserModel.get_by_email("rahul.sharma@example.com")
    assert user is not None
    assert user["role"] == "USER"
    assert user["is_active"] is True


def test_user_login(client):
    """Verify commuter login with seeded credentials returns role USER."""
    resp = client.post("/api/auth/login", json={
        "email": "rahul.sharma@example.com",
        "password": "UserPassword123!"
    })
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "token" in data
    assert data["user"]["role"] == "USER"
    assert data["user"]["email"] == "rahul.sharma@example.com"


def test_admin_login(client):
    """Verify administrator login with seeded credentials returns role ADMIN."""
    resp = client.post("/api/auth/login", json={
        "email": "admin@intellitransit.com",
        "password": "AdminPassword123!"
    })
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "token" in data
    assert data["user"]["role"] == "ADMIN"
    assert data["user"]["email"] == "admin@intellitransit.com"


def test_conductor_login(client):
    """Verify conductor login with seeded credentials returns role ADMIN."""
    resp = client.post("/api/auth/login", json={
        "email": "conductor@intellitransit.com",
        "password": "ConductorPassword123!"
    })
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "token" in data
    assert data["user"]["role"] == "ADMIN"
    assert data["user"]["email"] == "conductor@intellitransit.com"
