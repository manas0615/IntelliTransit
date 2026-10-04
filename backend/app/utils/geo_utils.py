"""
Geospatial calculation and coordinate validation utilities for Pune region.
"""
import math
from typing import List, Tuple
from backend.app.config import Config


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth in meters.
    """
    r = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers."""
    return haversine_distance_meters(lat1, lon1, lat2, lon2) / 1000.0


def is_within_pune(lat: float, lon: float) -> bool:
    """Verify coordinate falls within Pune metropolitan boundaries."""
    return (
        Config.PUNE_BOUNDS_MIN_LAT <= lat <= Config.PUNE_BOUNDS_MAX_LAT
        and Config.PUNE_BOUNDS_MIN_LNG <= lon <= Config.PUNE_BOUNDS_MAX_LNG
    )


def interpolate_points(lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 5) -> List[Tuple[float, float]]:
    """
    Interpolate points between two coordinates for polyline generation.
    Returns list of (lat, lng) tuples.
    """
    points = []
    for i in range(num_points + 1):
        fraction = i / float(num_points)
        lat = lat1 + fraction * (lat2 - lat1)
        lon = lon1 + fraction * (lon2 - lon1)
        points.append((round(lat, 6), round(lon, 6)))
    return points
