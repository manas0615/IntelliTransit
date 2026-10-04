"""
IntelliTransit AI Tools - Authoritative Gemini Function Calling Definitions.
Defines the exact 6 tools available to Gemini 2.5 Flash and their Python execution dispatchers.
"""
import logging
from typing import Any, Dict, List, Optional
from backend.app.services.journey_service import JourneyService
from backend.app.services.geocoding_service import GeocodingService
from backend.app.models.user_preference import UserPreferenceModel
from backend.app.models.journey import JourneyModel
from backend.app.models.ticket import TicketModel
from backend.app.models.pass_model import PassModel

logger = logging.getLogger(__name__)

# Schema definitions for Gemini Function Calling
GEMINI_TOOLS_DECLARATION = [
    {
        "name": "plan_journey",
        "description": "Plan an optimal multimodal transit journey between two locations in the Pune metropolitan region.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "origin_name": {
                    "type": "STRING",
                    "description": "Origin landmark or area in Pune (e.g. 'Kothrud', 'Swargate', 'Pune Station', 'Viman Nagar', 'Hinjawadi')."
                },
                "destination_name": {
                    "type": "STRING",
                    "description": "Destination landmark or area in Pune (e.g. 'Shivajinagar', 'Hadapsar', 'Katraj', 'Baner')."
                },
                "preference_profile": {
                    "type": "STRING",
                    "description": "Routing priority preference: 'BALANCED', 'FASTEST', 'CHEAPEST', 'MIN_TRANSFERS', or 'LEAST_WALKING'. Default is BALANCED.",
                    "enum": ["BALANCED", "FASTEST", "CHEAPEST", "MIN_TRANSFERS", "LEAST_WALKING"]
                }
            },
            "required": ["origin_name", "destination_name"]
        }
    },
    {
        "name": "get_journey_details",
        "description": "Retrieve detailed breakdown of a previously planned journey by its journey ID, including all legs and fares.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "journey_id": {
                    "type": "STRING",
                    "description": "The UUID of the journey to fetch."
                }
            },
            "required": ["journey_id"]
        }
    },
    {
        "name": "get_user_preferences",
        "description": "Fetch the authenticated user's transit routing preferences and mode priorities.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_journey_history",
        "description": "Retrieve the user's recent journey planning search history.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "limit": {
                    "type": "INTEGER",
                    "description": "Maximum number of past journeys to return (default 5, max 20)."
                }
            }
        }
    },
    {
        "name": "get_active_tickets",
        "description": "Fetch all currently active transit tickets owned by the user.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_active_passes",
        "description": "Fetch all currently active transit passes (Daily, Weekly, Monthly) owned by the user.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    }
]


class AIToolExecutor:
    """Dispatches and executes tool calls triggered by Gemini or rule-based engine."""

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id
        self.journey_service = JourneyService()
        self.geocoding_service = GeocodingService()

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool by name with provided arguments."""
        try:
            if tool_name == "plan_journey":
                return self._plan_journey(arguments)
            elif tool_name == "get_journey_details":
                return self._get_journey_details(arguments)
            elif tool_name == "get_user_preferences":
                return self._get_user_preferences()
            elif tool_name == "get_journey_history":
                return self._get_journey_history(arguments)
            elif tool_name == "get_active_tickets":
                return self._get_active_tickets()
            elif tool_name == "get_active_passes":
                return self._get_active_passes()
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.exception("Error executing AI tool %s: %s", tool_name, e)
            return {"error": str(e)}

    def _plan_journey(self, args: Dict[str, Any]) -> Dict[str, Any]:
        origin_name = args.get("origin_name")
        destination_name = args.get("destination_name")
        preference_profile = args.get("preference_profile", "BALANCED").upper()

        # Geocode origin and destination
        origin_geo = GeocodingService.resolve_location(origin_name)
        dest_geo = GeocodingService.resolve_location(destination_name)

        if not origin_geo:
            return {"error": f"Could not find coordinates for origin: '{origin_name}' within Pune."}
        if not dest_geo:
            return {"error": f"Could not find coordinates for destination: '{destination_name}' within Pune."}

        plan_result = JourneyService.plan_journey(
            origin_data={
                "name": origin_geo["name"],
                "latitude": float(origin_geo["latitude"]),
                "longitude": float(origin_geo["longitude"])
            },
            destination_data={
                "name": dest_geo["name"],
                "latitude": float(dest_geo["latitude"]),
                "longitude": float(dest_geo["longitude"])
            },
            user_id=self.user_id,
            preferences_input={"routing_preference": preference_profile}
        )

        return plan_result

    def _get_journey_details(self, args: Dict[str, Any]) -> Dict[str, Any]:
        journey_id = args.get("journey_id")
        if not journey_id:
            return {"error": "journey_id is required."}
        details = JourneyService.get_journey_by_id(journey_id, user_id=self.user_id)
        if not details:
            return {"error": "Journey not found or access denied."}
        return details

    def _get_user_preferences(self) -> Dict[str, Any]:
        if not self.user_id:
            return {"preferences": "Guest user (no stored preferences)."}
        pref = UserPreferenceModel.get_by_user_id(self.user_id)
        return {"preferences": pref or {}}

    def _get_journey_history(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.user_id:
            return {"history": []}
        limit = min(args.get("limit", 5), 20)
        history = JourneyModel.list_by_user_id(self.user_id, limit=limit)
        return {"history": history}

    def _get_active_tickets(self) -> Dict[str, Any]:
        if not self.user_id:
            return {"active_tickets": []}
        tickets = TicketModel.list_by_user_id(self.user_id, status="ACTIVE")
        return {"active_tickets": tickets}

    def _get_active_passes(self) -> Dict[str, Any]:
        if not self.user_id:
            return {"active_passes": []}
        passes = PassModel.list_by_user_id(self.user_id, status="ACTIVE")
        return {"active_passes": passes}
