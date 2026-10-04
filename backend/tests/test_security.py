"""
IntelliTransit Security Tests.
Tests HTTP security headers, JWT tamper resistance, and SQL injection safety.
"""
import pytest
import jwt
from app.config import Config
from app.models.user import UserModel


def test_security_headers(client):
    """Verify production security headers on HTTP responses."""
    resp = client.get("/api/health")
    assert resp.status_code == 200

    headers = resp.headers
    assert "X-Frame-Options" in headers
    assert headers["X-Frame-Options"] == "DENY"

    assert "X-Content-Type-Options" in headers
    assert headers["X-Content-Type-Options"] == "nosniff"

    assert "Content-Security-Policy" in headers
    assert "default-src 'self'" in headers["Content-Security-Policy"]


def test_tampered_jwt_token(client):
    """Verify forged/tampered JWT tokens are strictly rejected."""
    # Create token with incorrect secret
    fake_token = jwt.encode(
        {"user_id": "00000000-0000-0000-0000-000000000000", "role": "ADMIN"},
        "wrong-secret-key-attack",
        algorithm="HS256"
    )
    resp = client.get("/api/users/profile", headers={"Authorization": f"Bearer {fake_token}"})
    assert resp.status_code == 401


def test_sql_injection_defense(client):
    """Verify parameterized SQL defense against SQL injection attempts."""
    malicious_email = "admin' OR '1'='1' --"
    user = UserModel.get_by_email(malicious_email)
    assert user is None

    # Test via login endpoint
    resp = client.post("/api/auth/login", json={
        "email": malicious_email,
        "password": "anypassword"
    })
    assert resp.status_code in (400, 401)
