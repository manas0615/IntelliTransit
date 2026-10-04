"""
Authoritative Fare Service for IntelliTransit.
Computes fare for individual transportation legs based on active PostgreSQL fare_configurations.
Walking contributes exactly ₹0.00.
"""
import logging
from typing import Dict, Optional, Tuple
from backend.app.models.fare_configuration import FareConfigurationModel

logger = logging.getLogger(__name__)


class FareService:
    """Service computing authoritative fares per transport mode and distance."""

    @staticmethod
    def calculate_leg_fare(mode: str, distance_meters: float, service_id: Optional[str] = None) -> Tuple[float, str, Optional[str]]:
        """
        Calculate fare for an individual journey leg.
        Returns (fare_amount, fare_provenance, resolved_service_id).
        """
        clean_mode = mode.upper().strip()

        # Walking is always free
        if clean_mode in ("WALK", "WALKING"):
            return 0.0, "SOURCED", None

        # Fetch active configuration from DB
        config = None
        if service_id:
            config = FareConfigurationModel.get_active_by_service_id(service_id)
        if not config:
            config = FareConfigurationModel.get_active_by_mode(clean_mode)

        dist_km = max(0.0, distance_meters / 1000.0)

        if not config:
            # Fallback curated defaults if DB not yet seeded
            logger.warning("No active fare configuration found for mode %s. Using default baseline.", clean_mode)
            if clean_mode == "BUS":
                return round(10.0 + (dist_km * 2.0), 2), "CURATED", None
            elif clean_mode == "METRO":
                return round(max(10.0, 10.0 + (dist_km * 2.5)), 2), "SOURCED", None
            elif clean_mode == "TAXI":
                return round(max(25.0, 25.0 + (dist_km * 17.0)), 2), "CURATED", None
            return 0.0, "ESTIMATED", None

        fare_type = config.get("fare_type", "DISTANCE_BASED")
        base_fare = float(config.get("base_fare", 0.0))
        per_km_rate = float(config.get("per_km_rate") or 0.0)
        min_fare = float(config.get("minimum_fare") or 0.0)
        resolved_service_id = config.get("service_id")

        if fare_type == "FLAT":
            fare = base_fare
        elif fare_type == "DISTANCE_BASED":
            fare = base_fare + (dist_km * per_km_rate)
            if min_fare > 0:
                fare = max(fare, min_fare)
        else:
            fare = base_fare + (dist_km * per_km_rate)

        provenance = "SOURCED" if clean_mode == "METRO" else "CURATED"
        return round(fare, 2), provenance, resolved_service_id
