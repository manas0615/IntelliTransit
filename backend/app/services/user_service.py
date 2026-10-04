"""
User Service Layer for profile, transportation preferences, and saved location management.
"""
from typing import Any, Dict, List, Optional
from backend.app.models.user import UserModel
from backend.app.models.user_preference import UserPreferenceModel
from backend.app.models.saved_location import SavedLocationModel


class UserService:
    """Business logic for user features and personalization."""

    @staticmethod
    def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete user profile including preferences."""
        user = UserModel.get_by_id(user_id)
        if not user:
            return None
        pref = UserPreferenceModel.get_by_user_id(user_id)
        user["preferences"] = pref
        return user

    @staticmethod
    def update_profile(user_id: str, full_name: Optional[str] = None, phone: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update profile fields."""
        if phone:
            existing = UserModel.get_by_phone(phone.strip())
            if existing and existing["user_id"] != user_id:
                raise ValueError("Phone number is already associated with another account.")
        return UserModel.update_profile(user_id, full_name, phone)

    @staticmethod
    def get_preferences(user_id: str) -> Dict[str, Any]:
        """Retrieve preferences, returning defaults if not yet set."""
        pref = UserPreferenceModel.get_by_user_id(user_id)
        if not pref:
            pref = UserPreferenceModel.create_or_update(user_id=user_id)
        return pref

    @staticmethod
    def update_preferences(
        user_id: str,
        preferred_mode: Optional[str] = None,
        route_preference: Optional[str] = None,
        max_walking_distance_m: Optional[int] = None,
        avoid_taxi: Optional[bool] = None,
        avoid_transfers: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update preference flags."""
        current = UserService.get_preferences(user_id)
        return UserPreferenceModel.create_or_update(
            user_id=user_id,
            preferred_mode=preferred_mode if preferred_mode is not None else current.get("preferred_mode"),
            route_preference=route_preference if route_preference is not None else current.get("route_preference"),
            max_walking_distance_m=max_walking_distance_m if max_walking_distance_m is not None else current.get("max_walking_distance_m"),
            avoid_taxi=avoid_taxi if avoid_taxi is not None else current.get("avoid_taxi", False),
            avoid_transfers=avoid_transfers if avoid_transfers is not None else current.get("avoid_transfers", False)
        )

    @staticmethod
    def list_saved_locations(user_id: str) -> List[Dict[str, Any]]:
        """List all saved locations for user."""
        return SavedLocationModel.list_by_user_id(user_id)

    @staticmethod
    def create_saved_location(
        user_id: str,
        label: str,
        location_name: str,
        latitude: float,
        longitude: float,
        address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a saved location ensuring limit of 20."""
        existing = SavedLocationModel.list_by_user_id(user_id)
        if len(existing) >= 20:
            raise ValueError("Maximum saved location limit (20) reached. Delete an existing location first.")
        return SavedLocationModel.create(user_id, label, location_name, latitude, longitude, address)

    @staticmethod
    def update_saved_location(
        location_id: str,
        user_id: str,
        label: Optional[str] = None,
        location_name: Optional[str] = None,
        address: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Update saved location ensuring ownership."""
        return SavedLocationModel.update(location_id, user_id, label, location_name, address, latitude, longitude)

    @staticmethod
    def delete_saved_location(location_id: str, user_id: str) -> bool:
        """Delete saved location ensuring ownership."""
        return SavedLocationModel.delete(location_id, user_id)
