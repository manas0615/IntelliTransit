"""
Route Explanation Generator - Creates step-by-step human explanations of journey itineraries.
"""
from typing import Any, Dict, List


class RouteExplanationGenerator:
    """Generates structured natural language journey summaries."""

    @staticmethod
    def generate_explanation(itinerary: Dict[str, Any], preference: str = "FASTEST") -> str:
        """Create step-by-step explanation for a single itinerary."""
        legs = itinerary.get("legs", [])
        if not legs:
            return "No route legs available."

        steps = []
        for leg in legs:
            mode = leg["mode"]
            from_name = leg["from_name"]
            to_name = leg["to_name"]
            duration = leg["duration_min"]
            dist_m = leg.get("distance_meters", 0)

            if mode == "WALK":
                steps.append(f"Walk {int(dist_m)}m to {to_name} (~{duration} min)")
            elif mode == "BUS":
                route = f" on {leg['route_name']}" if leg.get("route_name") else ""
                steps.append(f"Take Bus{route} from {from_name} to {to_name} (~{duration} min, ₹{leg.get('fare', 0):.2f})")
            elif mode == "METRO":
                route = f" on {leg['route_name']}" if leg.get("route_name") else ""
                steps.append(f"Board Metro{route} at {from_name} to {to_name} (~{duration} min, ₹{leg.get('fare', 0):.2f})")
            elif mode == "TAXI":
                steps.append(f"Take Taxi from {from_name} to {to_name} (~{duration} min, ₹{leg.get('fare', 0):.2f})")
            else:
                steps.append(f"Travel from {from_name} to {to_name} via {mode} (~{duration} min)")

        summary = " → ".join(steps)
        total_time = itinerary.get("total_duration_min", 0)
        total_fare = itinerary.get("estimated_fare", 0.0)
        walking_m = int(itinerary.get("walking_distance_m", 0))

        footer = f"\nTotal: ~{total_time} mins | Estimated Fare: ₹{total_fare:.2f} | Total Walking: {walking_m}m"
        return summary + footer

    @staticmethod
    def generate_recommendation_reason(itinerary: Dict[str, Any], preference: str) -> str:
        """Explains why this route was ranked #1."""
        pref = preference.upper().strip()
        time_min = itinerary.get("total_duration_min", 0)
        fare = itinerary.get("estimated_fare", 0.0)
        walk_m = int(itinerary.get("walking_distance_m", 0))

        if pref == "FASTEST":
            return f"Fastest transit duration of {time_min} minutes."
        elif pref == "CHEAPEST":
            return f"Most economical option with an estimated total fare of ₹{fare:.2f}."
        elif pref == "LEAST_WALKING":
            return f"Requires the least physical walking ({walk_m} meters total)."
        elif pref == "FEWEST_TRANSFERS":
            return "Provides a direct journey with minimal transfers."
        elif pref == "BALANCED":
            return f"Best overall balance of travel time ({time_min}m), affordable fare (₹{fare:.2f}), and comfortable walking ({walk_m}m)."
        return "Recommended based on your preferences."
