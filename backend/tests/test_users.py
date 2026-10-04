"""
Integration and API tests for User profile, preferences, and saved locations.
"""
import uuid


def get_authenticated_token(client, email_prefix="user"):
    """Helper creating user and returning JWT token."""
    email = f"{email_prefix}_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/auth/register", json={
        "full_name": "Test Commuter",
        "email": email,
        "password": "Password123!"
    })
    return resp.get_json()["data"]["token"]


def test_user_profile_and_preferences_api(client):
    """Verify profile retrieval, update, and preference updates."""
    token = get_authenticated_token(client, "profile_test")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Get profile
    p_resp = client.get("/api/users/profile", headers=headers)
    assert p_resp.status_code == 200
    assert "preferences" in p_resp.get_json()["data"]["user"]

    # 2. Update preferences
    pref_payload = {
        "preferred_mode": "METRO",
        "route_preference": "CHEAPEST",
        "avoid_taxi": True
    }
    pref_resp = client.put("/api/users/preferences", json=pref_payload, headers=headers)
    assert pref_resp.status_code == 200
    updated_pref = pref_resp.get_json()["data"]["preferences"]
    assert updated_pref["preferred_mode"] == "METRO"
    assert updated_pref["avoid_taxi"] is True


def test_saved_locations_api_and_isolation(client):
    """Verify location CRUD and multi-user data isolation."""
    token1 = get_authenticated_token(client, "user1")
    token2 = get_authenticated_token(client, "user2")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # User 1 creates location
    loc_payload = {
        "label": "Office",
        "location_name": "Cybercity Magarpatta",
        "latitude": 18.5146,
        "longitude": 73.9298
    }
    create_resp = client.post("/api/users/locations", json=loc_payload, headers=headers1)
    assert create_resp.status_code == 201
    loc_id = create_resp.get_json()["data"]["location"]["location_id"]

    # User 2 lists locations -> should NOT see User 1's location
    list2 = client.get("/api/users/locations", headers=headers2).get_json()["data"]["locations"]
    assert len(list2) == 0

    # User 2 cannot delete User 1's location
    del2 = client.delete(f"/api/users/locations/{loc_id}", headers=headers2)
    assert del2.status_code == 404

    # User 1 can delete their own location
    del1 = client.delete(f"/api/users/locations/{loc_id}", headers=headers1)
    assert del1.status_code == 200
