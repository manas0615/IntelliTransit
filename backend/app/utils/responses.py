"""
Standardized API response helpers for IntelliTransit.
Enforces the frozen response format across all endpoints.
Handles Decimal and datetime serialization automatically.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple
from flask import jsonify, Response


def sanitize_json(obj: Any) -> Any:
    """Recursively convert Decimals to float and datetimes to ISO strings."""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(i) for i in obj]
    return obj


def success_response(
    data: Optional[Any] = None,
    message: str = "Request completed successfully",
    status_code: int = 200
) -> Tuple[Response, int]:
    """
    Format standard success response:
    {
        "success": true,
        "data": ...,
        "message": "..."
    }
    """
    clean_data = sanitize_json(data if data is not None else {})
    payload = {
        "success": True,
        "data": clean_data,
        "message": message
    }
    return jsonify(payload), status_code


def error_response(
    code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None
) -> Tuple[Response, int]:
    """
    Format standard error response:
    {
        "success": false,
        "error": {
            "code": "...",
            "message": "...",
            "details": {...} (optional)
        }
    }
    """
    err: Dict[str, Any] = {
        "code": code,
        "message": message
    }
    if details:
        err["details"] = sanitize_json(details)

    payload = {
        "success": False,
        "error": err
    }
    return jsonify(payload), status_code
