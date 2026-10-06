"""
Unit & Integration Tests for Admin Dashboard & RBAC Access Control.
"""
import pytest
import uuid
from app.models.user import UserModel


@pytest.fixture
def commuter_user(client):
    email = f"commuter_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "Standard Commuter",
        "email": email,
        "password": "Password123!"
    })
    data = reg.get_json()["data"]
    return {"user_id": data["user"]["user_id"], "token": data["token"]}


@pytest.fixture
def admin_user(client):
    email = f"admin_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "Platform Admin",
        "email": email,
        "password": "Password123!"
    })
    data = reg.get_json()["data"]
    user_id = data["user"]["user_id"]
    # Promote to ADMIN in DB
    UserModel.update_role(user_id, "ADMIN")

    # Re-login to get updated JWT token with ADMIN role
    login_resp = client.post("/api/auth/login", json={
        "email": email,
        "password": "Password123!"
    })
    token = login_resp.get_json()["data"]["token"]
    return {"user_id": user_id, "token": token}


def test_admin_rbac_forbidden_for_commuter(client, commuter_user):
    """Ensure standard commuters cannot access admin endpoints."""
    headers = {"Authorization": f"Bearer {commuter_user['token']}"}

    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 403

    resp_users = client.get("/api/admin/users", headers=headers)
    assert resp_users.status_code == 403


def test_user_cannot_access_admin(client, commuter_user):
    """Ensure standard commuter accounts cannot access admin endpoints."""
    headers = {"Authorization": f"Bearer {commuter_user['token']}"}
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 403


def test_admin_can_access_admin(client, admin_user):
    """Ensure administrator accounts can access admin endpoints."""
    headers = {"Authorization": f"Bearer {admin_user['token']}"}
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 200


def test_admin_metrics_and_overview(client, admin_user):
    """Ensure admins can retrieve aggregated metrics."""
    headers = {"Authorization": f"Bearer {admin_user['token']}"}

    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "total_users" in data
    assert "total_journeys" in data
    assert "total_revenue" in data
    assert "system_status" in data
    assert data["system_status"] == "OPERATIONAL"


def test_admin_services_and_fares(client, admin_user):
    """Ensure admins can list services and update fare matrix."""
    headers = {"Authorization": f"Bearer {admin_user['token']}"}

    # List services
    s_resp = client.get("/api/admin/services", headers=headers)
    assert s_resp.status_code == 200
    assert "services" in s_resp.get_json()["data"]

    # List fares
    f_resp = client.get("/api/admin/fares", headers=headers)
    assert f_resp.status_code == 200
    fares = f_resp.get_json()["data"]["fares"]
    assert len(fares) > 0

    fare_id = fares[0]["fare_id"]
    # Update fare
    update_resp = client.put(f"/api/admin/fares/{fare_id}", json={
        "base_fare": 12.00
    }, headers=headers)
    assert update_resp.status_code == 200
    assert float(update_resp.get_json()["data"]["base_fare"]) == 12.00
