"""
Unit tests for Health Check API.
"""
def test_health_check_endpoint(client):
    """GET /api/health returns 200 and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["data"]["database"] == "connected"


def test_404_not_found(client):
    """Unknown API endpoint returns standardized 404 JSON."""
    response = client.get("/api/nonexistent-endpoint")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"


def test_security_headers_present(client):
    """Verify security headers are attached to responses."""
    response = client.get("/api/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert "Content-Security-Policy" in response.headers
