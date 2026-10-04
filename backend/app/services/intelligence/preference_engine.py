"""
Preference Engine - Enforces hard user constraints and filtering rules.
"""
from typing import Any, Dict, List, Optional


class PreferenceEngine:
    """Applies user constraint filtering to candidate itineraries."""

    @staticmethod
    def apply_filters(
        itineraries: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter candidate itineraries based on hard constraints.
        If all itineraries would be eliminated by constraints, returns fallback with warnings.
        """
        if not preferences or not itineraries:
            return itineraries

        filtered = list(itineraries)

        # 1. Avoid Taxi
        if preferences.get("avoid_taxi"):
            no_taxi = [it for it in filtered if "TAXI" not in it.get("modes_used", [])]
            if no_taxi:
                filtered = no_taxi

        # 2. Max Walking Distance Constraint
        max_walk = preferences.get("max_walking_distance_m")
        if max_walk is not None and max_walk > 0:
            within_walk = [it for it in filtered if it.get("walking_distance_m", 0) <= max_walk]
            if within_walk:
                filtered = within_walk

        # 3. Avoid Transfers Constraint
        if preferences.get("avoid_transfers"):
            direct_only = [it for it in filtered if it.get("transfers_count", 0) == 0]
            if direct_only:
                filtered = direct_only

        return filtered if filtered else itineraries
