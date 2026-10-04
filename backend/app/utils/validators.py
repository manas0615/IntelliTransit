"""
Common validation utilities and coordinate verification for Pune metropolitan region.
"""
from typing import Optional, Tuple
from backend.app.config import Config


def is_in_pune_bounds(latitude: float, longitude: float) -> bool:
    """Check if given coordinate falls inside Pune metropolitan bounding box."""
    return (
        Config.PUNE_BOUNDS_MIN_LAT <= latitude <= Config.PUNE_BOUNDS_MAX_LAT
        and Config.PUNE_BOUNDS_MIN_LNG <= longitude <= Config.PUNE_BOUNDS_MAX_LNG
    )


def parse_pagination(limit_param: Optional[str], offset_param: Optional[str], default_limit: int = 20, max_limit: int = 100) -> Tuple[int, int]:
    """Parse and clamp pagination limit and offset parameters safely."""
    try:
        limit = int(limit_param) if limit_param else default_limit
        if limit < 1:
            limit = default_limit
        elif limit > max_limit:
            limit = max_limit
    except (ValueError, TypeError):
        limit = default_limit

    try:
        offset = int(offset_param) if offset_param else 0
        if offset < 0:
            offset = 0
    except (ValueError, TypeError):
        offset = 0

    return limit, offset
