"""
JWT Token Generation and Verification Utilities using PyJWT.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from backend.app.config import Config


def create_access_token(user_id: str, role: str, email: str, account_type: Optional[str] = None, expires_delta_hours: Optional[int] = None) -> str:
    """
    Generate a signed HS256 JWT access token with standard claims.
    """
    hours = expires_delta_hours if expires_delta_hours is not None else Config.JWT_ACCESS_TOKEN_EXPIRES_HOURS
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=hours)

    if not account_type:
        if role == "ADMIN":
            account_type = "CONDUCTOR" if "conductor" in email.lower() else "ADMINISTRATOR"
        else:
            account_type = "COMMUTER"

    payload = {
        "sub": user_id,
        "user_id": user_id,
        "role": role,
        "account_type": account_type,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp())
    }

    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT access token.
    Returns the payload dictionary if valid, raises jwt.PyJWTError on failure.
    """
    return jwt.decode(
        token,
        Config.JWT_SECRET_KEY,
        algorithms=[Config.JWT_ALGORITHM],
        options={"require": ["sub", "exp", "iat", "role"]}
    )
