"""
Geocoding service for Pune metropolitan landmarks and coordinate resolution.
"""
from typing import Any, Dict, List, Optional
from backend.app.utils.geo_utils import haversine_distance_meters, is_within_pune

# Curated Pune Transit Landmarks Knowledge Base (Classification: CURATED)
PUNE_LANDMARKS = [
    {"name": "Pune Railway Station", "latitude": 18.5285, "longitude": 73.8743, "category": "transit_hub", "aliases": ["pune station", "pune junction"]},
    {"name": "Shivajinagar Bus Stand", "latitude": 18.5314, "longitude": 73.8446, "category": "transit_hub", "aliases": ["shivajinagar", "shivajinagar station"]},
    {"name": "Swargate Bus Stand", "latitude": 18.5018, "longitude": 73.8586, "category": "transit_hub", "aliases": ["swargate", "swargate depot"]},
    {"name": "Civil Court Metro Interchange", "latitude": 18.5236, "longitude": 73.8500, "category": "metro_station", "aliases": ["civil court", "court metro"]},
    {"name": "COEP Technological University", "latitude": 18.5293, "longitude": 73.8565, "category": "education", "aliases": ["coep", "college of engineering pune"]},
    {"name": "Kothrud Stand", "latitude": 18.5074, "longitude": 73.8077, "category": "transit_hub", "aliases": ["kothrud", "kothrud depot"]},
    {"name": "Hinjewadi Phase 1", "latitude": 18.5912, "longitude": 73.7389, "category": "tech_park", "aliases": ["hinjewadi", "hinjawadi", "rajiv gandhi infotech park"]},
    {"name": "Hinjewadi Phase 3", "latitude": 18.5843, "longitude": 73.6934, "category": "tech_park", "aliases": ["megapolis", "hinjewadi phase 3"]},
    {"name": "Magarpatta City", "latitude": 18.5146, "longitude": 73.9298, "category": "tech_park", "aliases": ["magarpatta", "cybercity"]},
    {"name": "Viman Nagar", "latitude": 18.5679, "longitude": 73.9143, "category": "suburb", "aliases": ["viman nagar", "phoenix marketcity"]},
    {"name": "Pune International Airport", "latitude": 18.5822, "longitude": 73.9197, "category": "transit_hub", "aliases": ["airport", "pune airport", "lohegaon airport"]},
    {"name": "Katraj Bus Depot", "latitude": 18.4575, "longitude": 73.8677, "category": "transit_hub", "aliases": ["katraj", "katraj snake park"]},
    {"name": "Hadapsar Gadital", "latitude": 18.5013, "longitude": 73.9348, "category": "transit_hub", "aliases": ["hadapsar", "gadital"]},
    {"name": "Baner Phata", "latitude": 18.5590, "longitude": 73.7868, "category": "suburb", "aliases": ["baner", "baner road"]},
    {"name": "Aundh Parihar Chowk", "latitude": 18.5601, "longitude": 73.8072, "category": "suburb", "aliases": ["aundh", "parihar chowk"]},
    {"name": "PCMC Building Pimpri", "latitude": 18.6279, "longitude": 73.8009, "category": "government", "aliases": ["pcmc", "pimpri", "chinchwad"]},
    {"name": "Vanaz Metro Station", "latitude": 18.5072, "longitude": 73.8015, "category": "metro_station", "aliases": ["vanaz", "vanaz metro", "paud road metro"]},
    {"name": "Ramwadi Metro Station", "latitude": 18.5521, "longitude": 73.9174, "category": "metro_station", "aliases": ["ramwadi", "ramwadi metro"]},
    {"name": "Deccan Gymkhana", "latitude": 18.5167, "longitude": 73.8417, "category": "suburb", "aliases": ["deccan", "fc road", "jm road"]},
    {"name": "Camp Pune", "latitude": 18.5158, "longitude": 73.8786, "category": "suburb", "aliases": ["camp", "mg road", "cantonment"]}
]


class GeocodingService:
    """Provides location geocoding, search suggestions, and coordinate resolution."""

    @staticmethod
    def search_landmarks(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Pune landmarks by name or alias."""
        clean = query.lower().strip()
        if not clean:
            return PUNE_LANDMARKS[:limit]

        matches = []
        for lm in PUNE_LANDMARKS:
            if clean in lm["name"].lower():
                matches.append(lm)
                continue
            for alias in lm.get("aliases", []):
                if clean in alias.lower():
                    matches.append(lm)
                    break

        return matches[:limit]

    @staticmethod
    def resolve_location(name: str, fallback_lat: Optional[float] = None, fallback_lng: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Resolve a text name to coordinates, or validate fallback coordinates."""
        matches = GeocodingService.search_landmarks(name, limit=1)
        if matches:
            return matches[0]

        if fallback_lat is not None and fallback_lng is not None:
            if is_within_pune(fallback_lat, fallback_lng):
                return {
                    "name": name.strip(),
                    "latitude": float(fallback_lat),
                    "longitude": float(fallback_lng),
                    "category": "custom"
                }

        return None

    @staticmethod
    def reverse_geocode(lat: float, lng: float) -> Optional[Dict[str, Any]]:
        """Find the closest landmark to a given coordinate."""
        if not is_within_pune(lat, lng):
            return None

        closest = None
        min_dist = float("inf")
        for lm in PUNE_LANDMARKS:
            dist = haversine_distance_meters(lat, lng, lm["latitude"], lm["longitude"])
            if dist < min_dist:
                min_dist = dist
                closest = lm

        if closest:
            result = dict(closest)
            result["distance_meters"] = round(min_dist, 1)
            return result
        return None
