"""
Unit tests for Geospatial utilities, Geocoding service, and OTP integration.
"""
from backend.app.utils.geo_utils import (
    haversine_distance_meters,
    haversine_distance_km,
    is_within_pune,
    interpolate_points
)
from backend.app.services.geocoding_service import GeocodingService
from backend.app.services.otp_service import OTPService


def test_haversine_formula():
    """Verify distance between Pune Station and Shivajinagar is ~3.5km."""
    # Pune Station: (18.5285, 73.8743), Shivajinagar: (18.5314, 73.8446)
    dist_m = haversine_distance_meters(18.5285, 73.8743, 18.5314, 73.8446)
    assert 2500 < dist_m < 4000
    assert 2.5 < haversine_distance_km(18.5285, 73.8743, 18.5314, 73.8446) < 4.0


def test_pune_boundary_check():
    """Verify points inside and outside Pune are classified correctly."""
    assert is_within_pune(18.5204, 73.8567) is True  # Central Pune (Shaniwar Wada)
    assert is_within_pune(18.5912, 73.7389) is True  # Hinjewadi
    assert is_within_pune(19.0760, 72.8777) is False  # Mumbai (outside Pune)
    assert is_within_pune(28.6139, 77.2090) is False  # Delhi


def test_geocoding_landmark_search():
    """Verify search returns expected Pune landmark coordinates."""
    results = GeocodingService.search_landmarks("Swargate")
    assert len(results) > 0
    assert "Swargate" in results[0]["name"]
    assert 18.49 < results[0]["latitude"] < 18.52

    coep = GeocodingService.search_landmarks("COEP")
    assert len(coep) > 0
    assert "COEP" in coep[0]["name"]


def test_otp_service_trip_planning():
    """Verify OTP service returns candidate itineraries with legs."""
    orig_lat, orig_lng = 18.5285, 73.8743  # Pune Station
    dest_lat, dest_lng = 18.5236, 73.8500  # Civil Court

    result = OTPService.plan_trip(orig_lat, orig_lng, dest_lat, dest_lng)
    assert result["status"] == "SUCCESS"
    assert len(result["itineraries"]) > 0

    itinerary = result["itineraries"][0]
    assert "duration" in itinerary
    assert "legs" in itinerary
    assert len(itinerary["legs"]) > 0
