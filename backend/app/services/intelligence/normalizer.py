"""
Itinerary Normalizer - Converts raw OTP 2 response structures into clean internal IntelliTransit format.
"""
from typing import Any, Dict, List
from backend.app.utils.geo_utils import interpolate_points


class ItineraryNormalizer:
    """Normalizes raw OTP itineraries into standardized internal representations."""

    @staticmethod
    def normalize_itinerary(raw_itinerary: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Convert a single OTP itinerary dictionary into standard application format."""
        raw_legs = raw_itinerary.get("legs", [])
        normalized_legs = []
        total_walk_m = 0.0

        for seq, leg in enumerate(raw_legs, start=1):
            raw_mode = leg.get("mode", "WALK").upper()
            if raw_mode in ("CAR", "TAXI", "CAB"):
                mode = "TAXI"
                is_ticketable = True
            elif raw_mode in ("BUS", "TRANSIT"):
                mode = "BUS"
                is_ticketable = True
            elif raw_mode in ("SUBWAY", "RAIL", "TRAM", "METRO"):
                mode = "METRO"
                is_ticketable = True
            else:
                mode = "WALK"
                is_ticketable = False

            dist_m = float(leg.get("distance", 0.0))
            if mode == "WALK":
                total_walk_m += dist_m

            from_place = leg.get("from", {})
            to_place = leg.get("to", {})

            from_lat = float(from_place.get("lat", 0.0))
            from_lng = float(from_place.get("lon", 0.0))
            to_lat = float(to_place.get("lat", 0.0))
            to_lng = float(to_place.get("lon", 0.0))

            # Polyline points
            points = leg.get("points")
            if not isinstance(points, list) or len(points) == 0:
                if from_lat and to_lat:
                    points = interpolate_points(from_lat, from_lng, to_lat, to_lng, 4)
                else:
                    points = []

            duration_s = int(leg.get("duration", 0))
            duration_min = max(1, round(duration_s / 60))

            norm_leg = {
                "sequence_number": seq,
                "mode": mode,
                "from_name": from_place.get("name", "Origin"),
                "from_latitude": from_lat,
                "from_longitude": from_lng,
                "to_name": to_place.get("name", "Destination"),
                "to_latitude": to_lat,
                "to_longitude": to_lng,
                "duration_min": duration_min,
                "distance_meters": round(dist_m, 1),
                "is_ticketable": is_ticketable,
                "route_name": leg.get("route", ""),
                "agency_name": leg.get("agencyName", ""),
                "points": points or []
            }
            normalized_legs.append(norm_leg)

        total_duration_s = int(raw_itinerary.get("duration", 0))
        total_duration_min = max(1, round(total_duration_s / 60))

        # Distinct transit transfers
        transit_modes = [l["mode"] for l in normalized_legs if l["mode"] in ("BUS", "METRO", "TAXI")]
        transfers_count = max(0, len(transit_modes) - 1)

        return {
            "route_id": f"route-{index + 1}",
            "route_type": "MULTIMODAL" if len(set(transit_modes)) > 1 else ("DIRECT" if len(transit_modes) == 1 else "WALK"),
            "total_duration_min": total_duration_min,
            "walking_distance_m": round(total_walk_m, 1),
            "transfers_count": transfers_count,
            "modes_used": list(dict.fromkeys([l["mode"] for l in normalized_legs])),
            "legs": normalized_legs
        }

    @staticmethod
    def normalize_all(raw_itineraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize a list of OTP itineraries."""
        return [
            ItineraryNormalizer.normalize_itinerary(it, idx)
            for idx, it in enumerate(raw_itineraries)
        ]
