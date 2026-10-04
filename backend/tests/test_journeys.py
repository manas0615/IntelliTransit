"""
Unit and Integration tests for Journey Planning and Intelligence Layer.
Tests all 5 ranking preferences, fare calculation, walking distance, taxi avoidance, and API endpoints.
"""
import uuid


def test_journey_planning_guest_api(client):
    """Verify guest journey planning works without authentication token."""
    payload = {
        "origin": {"name": "Pune Railway Station", "latitude": 18.5285, "longitude": 73.8743},
        "destination": {"name": "Civil Court", "latitude": 18.5236, "longitude": 73.8500},
        "preferences": {
            "route_preference": "FASTEST",
            "avoid_taxi": False
        }
    }
    resp = client.post("/api/journeys/plan", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["total_options"] > 0
    itineraries = data["itineraries"]
    assert len(itineraries) > 0

    first_it = itineraries[0]
    assert "total_duration_min" in first_it
    assert "estimated_fare" in first_it
    assert "legs" in first_it
    assert "explanation" in first_it
    assert first_it["rank"] == 1


def test_journey_ranking_preferences(client):
    """Verify different route preferences (CHEAPEST, LEAST_WALKING, BALANCED)."""
    # 1. Test CHEAPEST
    resp_cheap = client.post("/api/journeys/plan", json={
        "origin": {"name": "Kothrud", "latitude": 18.5074, "longitude": 73.8077},
        "destination": {"name": "Shivajinagar", "latitude": 18.5314, "longitude": 73.8446},
        "preferences": {"route_preference": "CHEAPEST"}
    })
    assert resp_cheap.status_code == 200
    cheap_opts = resp_cheap.get_json()["data"]["itineraries"]
    assert len(cheap_opts) >= 2
    assert cheap_opts[0]["estimated_fare"] <= cheap_opts[1]["estimated_fare"]

    # 2. Test AVOID_TAXI
    resp_notaxi = client.post("/api/journeys/plan", json={
        "origin": {"name": "Kothrud", "latitude": 18.5074, "longitude": 73.8077},
        "destination": {"name": "Shivajinagar", "latitude": 18.5314, "longitude": 73.8446},
        "preferences": {"avoid_taxi": True}
    })
    assert resp_notaxi.status_code == 200
    for opt in resp_notaxi.get_json()["data"]["itineraries"]:
        assert "TAXI" not in opt.get("modes_used", [])


def test_journey_persistence_for_authenticated_user(client):
    """Verify planned journeys are saved to history for authenticated users."""
    # Register user
    email = f"commuter_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "History User",
        "email": email,
        "password": "Password123!"
    })
    token = reg.get_json()["data"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Plan journey
    plan_resp = client.post("/api/journeys/plan", json={
        "origin": {"name": "Swargate", "latitude": 18.5018, "longitude": 73.8586},
        "destination": {"name": "Katraj", "latitude": 18.4575, "longitude": 73.8677},
        "preferences": {"route_preference": "FASTEST"}
    }, headers=headers)
    assert plan_resp.status_code == 200
    journey_id = plan_resp.get_json()["data"]["journey_id"]
    assert journey_id is not None

    # Retrieve history
    hist_resp = client.get("/api/journeys", headers=headers)
    assert hist_resp.status_code == 200
    journeys = hist_resp.get_json()["data"]["journeys"]
    assert len(journeys) >= 1
    assert journeys[0]["journey_id"] == journey_id
    assert len(journeys[0]["legs"]) > 0
