"""
Route Ranker - Multi-criteria scoring and sorting for candidate transit itineraries.
"""
from typing import Any, Dict, List


class RouteRanker:
    """Scores and orders candidate itineraries according to selected route preference."""

    @staticmethod
    def rank_itineraries(
        itineraries: List[Dict[str, Any]],
        preference: str = "FASTEST"
    ) -> List[Dict[str, Any]]:
        """
        Rank itineraries by preference:
        FASTEST, CHEAPEST, LEAST_WALKING, FEWEST_TRANSFERS, BALANCED.
        """
        if not itineraries:
            return []

        clean_pref = preference.upper().strip() if preference else "FASTEST"

        if clean_pref == "FASTEST":
            ranked = sorted(
                itineraries,
                key=lambda x: (x.get("total_duration_min", 9999), x.get("walking_distance_m", 9999), x.get("estimated_fare", 9999))
            )
        elif clean_pref == "CHEAPEST":
            ranked = sorted(
                itineraries,
                key=lambda x: (x.get("estimated_fare", 9999), x.get("total_duration_min", 9999), x.get("walking_distance_m", 9999))
            )
        elif clean_pref == "LEAST_WALKING":
            ranked = sorted(
                itineraries,
                key=lambda x: (x.get("walking_distance_m", 9999), x.get("total_duration_min", 9999), x.get("estimated_fare", 9999))
            )
        elif clean_pref == "FEWEST_TRANSFERS":
            ranked = sorted(
                itineraries,
                key=lambda x: (x.get("transfers_count", 9999), x.get("total_duration_min", 9999), x.get("estimated_fare", 9999))
            )
        elif clean_pref == "BALANCED":
            ranked = RouteRanker._rank_balanced(itineraries)
        else:
            ranked = sorted(itineraries, key=lambda x: x.get("total_duration_min", 9999))

        # Assign final rank position and badge
        for index, item in enumerate(ranked, start=1):
            item["rank"] = index
            if index == 1:
                item["badge"] = f"Recommended ({clean_pref.replace('_', ' ').title()})"
            elif clean_pref == "FASTEST" and index == 2:
                item["badge"] = "Alternative Option"
            else:
                item["badge"] = f"Option {index}"

        return ranked

    @staticmethod
    def _rank_balanced(itineraries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Compute weighted normalized multi-criteria cost score:
        Score = 0.40 * Norm(Duration) + 0.30 * Norm(Fare) + 0.20 * Norm(Walk) + 0.10 * Norm(Transfers)
        """
        max_duration = max([it.get("total_duration_min", 1) for it in itineraries] or [1])
        max_fare = max([it.get("estimated_fare", 1.0) for it in itineraries] or [1.0])
        max_walk = max([it.get("walking_distance_m", 1.0) for it in itineraries] or [1.0])
        max_transfers = max([it.get("transfers_count", 1) for it in itineraries] or [1])

        # Avoid division by zero
        max_duration = max(1.0, float(max_duration))
        max_fare = max(1.0, float(max_fare))
        max_walk = max(1.0, float(max_walk))
        max_transfers = max(1.0, float(max_transfers))

        for it in itineraries:
            norm_time = it.get("total_duration_min", 0) / max_duration
            norm_fare = it.get("estimated_fare", 0.0) / max_fare
            norm_walk = it.get("walking_distance_m", 0.0) / max_walk
            norm_trans = it.get("transfers_count", 0) / max_transfers

            score = (0.40 * norm_time) + (0.30 * norm_fare) + (0.20 * norm_walk) + (0.10 * norm_trans)
            it["balanced_score"] = round(score, 3)

        return sorted(itineraries, key=lambda x: (x.get("balanced_score", 999.0), x.get("total_duration_min", 999)))
