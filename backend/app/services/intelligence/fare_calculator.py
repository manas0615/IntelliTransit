"""
Fare Calculator - Computes and aggregates fares across all legs of candidate itineraries.
"""
from typing import Any, Dict, List
from backend.app.services.fare_service import FareService


class FareCalculator:
    """Calculates leg-level fares and multimodal journey sums."""

    @staticmethod
    def attach_fares(itinerary: Dict[str, Any]) -> Dict[str, Any]:
        """Compute fare for each leg and calculate total journey fare."""
        total_fare = 0.0
        legs = itinerary.get("legs", [])
        provenances = set()

        for leg in legs:
            mode = leg["mode"]
            dist_m = leg.get("distance_meters", 0.0)
            service_id = leg.get("service_id")

            fare_val, prov, res_service_id = FareService.calculate_leg_fare(mode, dist_m, service_id)
            leg["fare"] = fare_val
            leg["fare_provenance"] = prov
            if res_service_id:
                leg["service_id"] = res_service_id

            total_fare += fare_val
            provenances.add(prov)

        itinerary["estimated_fare"] = round(total_fare, 2)
        itinerary["fare_provenance"] = "SOURCED" if "SOURCED" in provenances and len(provenances) == 1 else "CURATED"
        return itinerary

    @staticmethod
    def process_all(itineraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Attach fares to all itineraries."""
        return [FareCalculator.attach_fares(it) for it in itineraries]
