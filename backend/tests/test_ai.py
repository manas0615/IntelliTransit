"""
Unit & Integration Tests for AI Assistant Service and 6 Authoritative Tools.
"""
import pytest
import uuid
from app.services.ai_tools import AIToolExecutor, GEMINI_TOOLS_DECLARATION
from app.services.ai_service import AIService


@pytest.fixture
def auth_user(client):
    email = f"ai_user_{uuid.uuid4().hex[:8]}@example.com"
    reg = client.post("/api/auth/register", json={
        "full_name": "AI Commuter",
        "email": email,
        "password": "Password123!"
    })
    data = reg.get_json()["data"]
    return {"user_id": data["user"]["user_id"], "token": data["token"]}


def test_ai_tools_declaration():
    """Verify that exactly 6 authoritative tools are defined for Gemini."""
    assert len(GEMINI_TOOLS_DECLARATION) == 6
    names = [t["name"] for t in GEMINI_TOOLS_DECLARATION]
    expected_names = [
        "plan_journey",
        "get_journey_details",
        "get_user_preferences",
        "get_journey_history",
        "get_active_tickets",
        "get_active_passes"
    ]
    for exp in expected_names:
        assert exp in names


def test_ai_tool_executor(auth_user):
    """Test execution of tools directly through AIToolExecutor."""
    executor = AIToolExecutor(user_id=auth_user["user_id"])

    # 1. Plan journey tool
    res = executor.execute_tool("plan_journey", {
        "origin_name": "Swargate",
        "destination_name": "Pune Station",
        "preference_profile": "BALANCED"
    })
    assert "itineraries" in res
    assert len(res["itineraries"]) > 0

    # 2. Get user preferences tool
    pref_res = executor.execute_tool("get_user_preferences", {})
    assert "preferences" in pref_res

    # 3. Get active tickets tool
    tkt_res = executor.execute_tool("get_active_tickets", {})
    assert "active_tickets" in tkt_res

    # 4. Get active passes tool
    pass_res = executor.execute_tool("get_active_passes", {})
    assert "active_passes" in pass_res

    # 5. Get journey history tool
    hist_res = executor.execute_tool("get_journey_history", {"limit": 5})
    assert "history" in hist_res


def test_ai_chat_endpoint_fallback(client, auth_user):
    """Test AI chat endpoint conversational fallback."""
    token = auth_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Trip planning query
    resp = client.post("/api/ai/chat", json={
        "message": "How do I travel from Swargate to Pune Station?"
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "reply" in data
    assert "Optimal Route" in data["reply"] or "Swargate" in data["reply"]

    # Active tickets query
    tkt_resp = client.post("/api/ai/chat", json={
        "message": "Show my active tickets"
    }, headers=headers)
    assert tkt_resp.status_code == 200
    assert "tickets" in tkt_resp.get_json()["data"]["reply"].lower()
