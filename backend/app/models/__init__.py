"""
IntelliTransit Models Package - Direct Parameterized PostgreSQL Data Access Layer.
"""
from backend.app.models.db import (
    init_db_pool,
    close_db_pool,
    get_db_pool,
    get_db_connection,
    get_db_cursor,
    execute_query,
    fetch_one,
    fetch_all,
    check_db_health
)
from backend.app.models.user import UserModel
from backend.app.models.user_preference import UserPreferenceModel
from backend.app.models.saved_location import SavedLocationModel
from backend.app.models.journey import JourneyModel
from backend.app.models.journey_leg import JourneyLegModel
from backend.app.models.transport_service import TransportServiceModel
from backend.app.models.fare_configuration import FareConfigurationModel
from backend.app.models.payment import PaymentModel
from backend.app.models.ticket import TicketModel
from backend.app.models.pass_model import PassModel
from backend.app.models.ticket_validation import TicketValidationModel

__all__ = [
    "init_db_pool",
    "close_db_pool",
    "get_db_pool",
    "get_db_connection",
    "get_db_cursor",
    "execute_query",
    "fetch_one",
    "fetch_all",
    "check_db_health",
    "UserModel",
    "UserPreferenceModel",
    "SavedLocationModel",
    "JourneyModel",
    "JourneyLegModel",
    "TransportServiceModel",
    "FareConfigurationModel",
    "PaymentModel",
    "TicketModel",
    "PassModel",
    "TicketValidationModel"
]
