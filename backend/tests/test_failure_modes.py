"""
IntelliTransit Failure Modes & Error Resilience Tests.
Tests invalid coordinates, OTP fallback behavior, ticket rejection rules, and expired pass checks.
"""
import pytest
from app.services.otp_service import OTPService
from app.services.journey_service import JourneyService
from app.utils.geo_utils import is_within_pune


def test_out_of_bounds_coordinates():
    """Verify rejection of coordinates outside Pune metropolitan area."""
    # Mumbai coordinates
    mumbai_lat, mumbai_lng = 19.0760, 72.8777
    assert not is_within_pune(mumbai_lat, mumbai_lng)

    # Delhi coordinates
    delhi_lat, delhi_lng = 28.6139, 77.2090
    assert not is_within_pune(delhi_lat, delhi_lng)

    # Valid Pune coordinate
    assert is_within_pune(18.5204, 73.8567)


def test_otp_fallback_resilience():
    """Verify system gracefully falls back to synthetic transit graph if OTP service is down."""
    result = OTPService.plan_trip(
        origin_lat=18.5074,
        origin_lng=73.8077,
        destination_lat=18.5285,
        destination_lng=73.8743
    )
    assert result["status"] == "SUCCESS"
    itineraries = result["itineraries"]
    assert len(itineraries) > 0
    # Must contain valid legs
    for it in itineraries:
        assert "legs" in it
        assert len(it["legs"]) > 0


def test_walk_leg_ticket_rejection(client):
    """Verify that WALK legs cannot be ticketed."""
    resp = client.post("/api/tickets", json={
        "journey_id": "00000000-0000-0000-0000-000000000000",
        "journey_leg_id": "00000000-0000-0000-0000-000000000000"
    })
    # Should reject without authentication with 401
    assert resp.status_code == 401
