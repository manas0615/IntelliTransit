"""
Journey Service - Orchestrates OTP routing, Intelligence Layer processing, and persistence.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from backend.app.models.journey import JourneyModel
from backend.app.models.journey_leg import JourneyLegModel
from backend.app.models.user_preference import UserPreferenceModel
from backend.app.services.geocoding_service import GeocodingService
from backend.app.services.otp_service import OTPService
from backend.app.services.intelligence import (
    ItineraryNormalizer,
    FareCalculator,
    PreferenceEngine,
    RouteRanker,
    RouteExplanationGenerator
)
from backend.app.utils.geo_utils import is_within_pune


class JourneyService:
    """Orchestration service for multimodal journey planning."""

    @staticmethod
    def plan_journey(
        origin_data: Dict[str, Any],
        destination_data: Dict[str, Any],
        user_id: Optional[str] = None,
        preferences_input: Optional[Dict[str, Any]] = None,
        departure_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Execute full journey planning pipeline:
        Validate -> Resolve -> Query OTP -> Normalize -> Attach Fares -> Filter -> Rank -> Explain -> Persist.
        """
        # 1. Resolve coordinates
        orig_lat = origin_data.get("latitude")
        orig_lng = origin_data.get("longitude")
        orig_name = origin_data.get("name", "Origin")

        dest_lat = destination_data.get("latitude")
        dest_lng = destination_data.get("longitude")
        dest_name = destination_data.get("name", "Destination")

        if orig_lat is None or orig_lng is None:
            resolved_orig = GeocodingService.resolve_location(orig_name)
            if resolved_orig:
                orig_lat, orig_lng = resolved_orig["latitude"], resolved_orig["longitude"]
                orig_name = resolved_orig["name"]
            else:
                raise ValueError(f"Origin location '{orig_name}' could not be resolved to valid Pune coordinates.")

        if dest_lat is None or dest_lng is None:
            resolved_dest = GeocodingService.resolve_location(dest_name)
            if resolved_dest:
                dest_lat, dest_lng = resolved_dest["latitude"], resolved_dest["longitude"]
                dest_name = resolved_dest["name"]
            else:
                raise ValueError(f"Destination location '{dest_name}' could not be resolved to valid Pune coordinates.")

        if not is_within_pune(orig_lat, orig_lng):
            raise ValueError("Origin coordinate is outside the supported Pune metropolitan service area.")
        if not is_within_pune(dest_lat, dest_lng):
            raise ValueError("Destination coordinate is outside the supported Pune metropolitan service area.")

        # 2. Merge Preferences (User Profile + Request Overrides)
        effective_prefs = {
            "route_preference": "FASTEST",
            "avoid_taxi": False,
            "avoid_transfers": False,
            "max_walking_distance_m": 1500,
            "preferred_mode": None
        }
        if user_id:
            user_pref = UserPreferenceModel.get_by_user_id(user_id)
            if user_pref:
                for k, v in user_pref.items():
                    if v is not None:
                        effective_prefs[k] = v

        if preferences_input:
            for k, v in preferences_input.items():
                if v is not None:
                    effective_prefs[k] = v

        # 3. Query OpenTripPlanner 2
        otp_result = OTPService.plan_trip(
            origin_lat=orig_lat,
            origin_lng=orig_lng,
            destination_lat=dest_lat,
            destination_lng=dest_lng,
            departure_time=departure_time,
            max_walk_distance_m=effective_prefs.get("max_walking_distance_m")
        )

        raw_itineraries = otp_result.get("itineraries", [])

        # 4. Intelligence Layer Pipeline
        normalized = ItineraryNormalizer.normalize_all(raw_itineraries)
        fare_attached = FareCalculator.process_all(normalized)
        filtered = PreferenceEngine.apply_filters(fare_attached, effective_prefs)
        ranked = RouteRanker.rank_itineraries(filtered, effective_prefs.get("route_preference", "FASTEST"))

        # 5. Generate Route Explanations
        for it in ranked:
            it["explanation"] = RouteExplanationGenerator.generate_explanation(it, effective_prefs.get("route_preference", "FASTEST"))
            it["recommendation_reason"] = RouteExplanationGenerator.generate_recommendation_reason(it, effective_prefs.get("route_preference", "FASTEST"))

        # 6. Persist Journey and Legs for Authenticated User
        saved_journey_id = None
        if user_id and ranked:
            for it in reversed(ranked):
                created_journey = JourneyModel.create(
                    user_id=user_id,
                    origin_name=orig_name,
                    origin_latitude=orig_lat,
                    origin_longitude=orig_lng,
                    destination_name=dest_name,
                    destination_latitude=dest_lat,
                    destination_longitude=dest_lng,
                    departure_time=departure_time.isoformat() if departure_time else None,
                    total_duration_min=it.get("total_duration_min"),
                    walking_distance_m=int(it.get("walking_distance_m", 0)),
                    estimated_fare=it.get("estimated_fare"),
                    route_type=it.get("route_type", "MULTIMODAL")
                )
                j_id = created_journey["journey_id"]
                it["journey_id"] = j_id

                for leg in it.get("legs", []):
                    created_leg = JourneyLegModel.create(
                        journey_id=j_id,
                        sequence_number=leg["sequence_number"],
                        mode=leg["mode"],
                        service_id=leg.get("service_id"),
                        from_name=leg["from_name"],
                        from_latitude=leg["from_latitude"],
                        from_longitude=leg["from_longitude"],
                        to_name=leg["to_name"],
                        to_latitude=leg["to_latitude"],
                        to_longitude=leg["to_longitude"],
                        duration_min=leg["duration_min"],
                        walking_distance_m=int(leg.get("distance_meters", 0)) if leg["mode"] == "WALK" else 0,
                        estimated_fare=leg.get("fare", 0.0),
                        is_ticketable=leg.get("is_ticketable", False)
                    )
                    leg["leg_id"] = created_leg["leg_id"]
                    leg["journey_id"] = j_id

            saved_journey_id = ranked[0]["journey_id"]

        return {
            "origin": {"name": orig_name, "latitude": orig_lat, "longitude": orig_lng},
            "destination": {"name": dest_name, "latitude": dest_lat, "longitude": dest_lng},
            "journey_id": saved_journey_id,
            "applied_preferences": effective_prefs,
            "total_options": len(ranked),
            "routing_source": "OTP" if otp_result.get("source") == "OTP_LIVE" else "OFFLINE_FALLBACK",
            "itineraries": ranked
        }

    @staticmethod
    def get_journey_by_id(journey_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve stored journey with all associated legs."""
        journey = JourneyModel.get_by_id(journey_id)
        if not journey:
            return None
        if user_id and journey.get("user_id") and journey.get("user_id") != user_id:
            return None

        legs = JourneyLegModel.list_by_journey_id(journey_id)
        journey["legs"] = legs
        return journey

    @staticmethod
    def list_user_journeys(user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """List past journey history for authenticated user."""
        journeys = JourneyModel.list_by_user_id(user_id, limit, offset)
        for j in journeys:
            j["legs"] = JourneyLegModel.list_by_journey_id(j["journey_id"])
        return journeys
