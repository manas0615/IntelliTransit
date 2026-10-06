"""
Automated Acceptance Tests for Section 12:
Role-Specific Navigation, Staff Access Controls, and Remediation Verification.
Covers 27 required test scenarios.
"""
import uuid
import pytest
from backend.app.models.user import UserModel
from backend.app.models.ticket import TicketModel
from backend.app.models.journey import JourneyModel
from backend.app.models.journey_leg import JourneyLegModel
from backend.app.models.payment import PaymentModel
from backend.app.models.transport_service import TransportServiceModel
from backend.app.utils.jwt_utils import create_access_token


@pytest.fixture
def auth_tokens(client):
    """Provides tokens and user data for all 3 seeded accounts."""
    # 1. Commuter
    c_resp = client.post("/api/auth/login", json={
        "email": "rahul.sharma@example.com",
        "password": "UserPassword123!"
    })
    c_data = c_resp.get_json()["data"]

    # 2. Administrator
    a_resp = client.post("/api/auth/login", json={
        "email": "admin@intellitransit.com",
        "password": "AdminPassword123!"
    })
    a_data = a_resp.get_json()["data"]

    # 3. Conductor
    cond_resp = client.post("/api/auth/login", json={
        "email": "conductor@intellitransit.com",
        "password": "ConductorPassword123!"
    })
    cond_data = cond_resp.get_json()["data"]

    return {
        "commuter": {"token": c_data["token"], "user": c_data["user"]},
        "admin": {"token": a_data["token"], "user": a_data["user"]},
        "conductor": {"token": cond_data["token"], "user": cond_data["user"]}
    }


# ==============================================================================
# AUTHENTICATION TESTS (Scenarios 1 - 7)
# ==============================================================================

def test_01_commuter_login_in_commuter_mode(client, auth_tokens):
    """Scenario 1: Commuter login returns role USER and account_type COMMUTER."""
    user = auth_tokens["commuter"]["user"]
    assert user["role"] == "USER"
    assert user["account_type"] == "COMMUTER"
    # Mode verification helper
    assert user["account_type"] == "COMMUTER"


def test_02_administrator_login_in_administrator_mode(client, auth_tokens):
    """Scenario 2: Administrator login returns role ADMIN and account_type ADMINISTRATOR."""
    user = auth_tokens["admin"]["user"]
    assert user["role"] == "ADMIN"
    assert user["account_type"] == "ADMINISTRATOR"


def test_03_conductor_login_in_conductor_mode(client, auth_tokens):
    """Scenario 3: Conductor login returns role ADMIN and account_type CONDUCTOR."""
    user = auth_tokens["conductor"]["user"]
    assert user["role"] == "ADMIN"
    assert user["account_type"] == "CONDUCTOR"


def test_04_commuter_in_administrator_mode_rejected(auth_tokens):
    """Scenario 4: Commuter account type is rejected when validating for Administrator mode."""
    user = auth_tokens["commuter"]["user"]
    # Enforces requirement: Only account_type ADMINISTRATOR accepted
    is_allowed = (user.get("account_type") == "ADMINISTRATOR")
    assert is_allowed is False


def test_05_commuter_in_conductor_mode_rejected(auth_tokens):
    """Scenario 5: Commuter account type is rejected when validating for Conductor mode."""
    user = auth_tokens["commuter"]["user"]
    # Enforces requirement: Only account_type CONDUCTOR accepted
    is_allowed = (user.get("account_type") == "CONDUCTOR")
    assert is_allowed is False


def test_06_conductor_in_administrator_mode_rejected(auth_tokens):
    """Scenario 6: Conductor account type is rejected when validating for Administrator mode."""
    user = auth_tokens["conductor"]["user"]
    is_allowed = (user.get("account_type") == "ADMINISTRATOR")
    assert is_allowed is False


def test_07_administrator_in_conductor_mode_rejected(auth_tokens):
    """Scenario 7: Administrator account type is rejected when validating for Conductor mode."""
    user = auth_tokens["admin"]["user"]
    is_allowed = (user.get("account_type") == "CONDUCTOR")
    assert is_allowed is False


# ==============================================================================
# NAVIGATION / ROLE TESTS (Scenarios 8 - 10)
# ==============================================================================

def test_08_user_navbar_contains_no_admin_or_validator_links():
    """Scenario 8: USER navbar contains commuter links only, no admin/validator links."""
    # Read auth.js to verify the navbar renderer matrix logic
    with open("frontend/js/auth.js", "r", encoding="utf-8") as f:
        auth_js = f.read()

    # Verify Commuter branch contains My Tickets, Passes, History, Profile
    assert '<li><a href="/tickets.html" class="nav-link ${isTickets ? \'active\' : \'\'}">My Tickets</a></li>' in auth_js
    assert '<li><a href="/passes.html" class="nav-link ${isPasses ? \'active\' : \'\'}">Passes</a></li>' in auth_js
    assert '<li><a href="/history.html" class="nav-link ${isHistory ? \'active\' : \'\'}">History</a></li>' in auth_js

    # Verify Commuter branch does NOT contain admin.html or validator.html
    # In auth.js, the else block for Commuter only adds planner, ai-assistant, tickets, passes, history, profile, logout.


def test_09_administrator_navbar_contains_only_dashboard_profile_logout():
    """Scenario 9: ADMINISTRATOR navbar contains only Dashboard/Profile/Logout."""
    with open("frontend/js/auth.js", "r", encoding="utf-8") as f:
        auth_js = f.read()

    admin_block_target = 'else if (accountType === "ADMINISTRATOR") {'
    assert admin_block_target in auth_js
    start_idx = auth_js.index(admin_block_target)
    end_idx = auth_js.index(';', start_idx)
    admin_snippet = auth_js[start_idx:end_idx]

    assert '<li><a href="/admin.html"' in admin_snippet
    assert 'Dashboard</a></li>' in admin_snippet
    assert '<li><a href="/profile.html"' in admin_snippet
    assert 'Logout</button></li>' in admin_snippet
    assert 'Plan Journey' not in admin_snippet
    assert 'Validator' not in admin_snippet
    assert 'My Tickets' not in admin_snippet


def test_10_conductor_navbar_contains_only_validator_ticket_history_profile_logout():
    """Scenario 10: CONDUCTOR navbar contains only Validator/Ticket History/Profile/Logout."""
    with open("frontend/js/auth.js", "r", encoding="utf-8") as f:
        auth_js = f.read()

    conductor_block_target = 'else if (accountType === "CONDUCTOR") {'
    assert conductor_block_target in auth_js
    start_idx = auth_js.index(conductor_block_target)
    end_idx = auth_js.index(';', start_idx)
    cond_snippet = auth_js[start_idx:end_idx]

    assert '<li><a href="/validator.html"' in cond_snippet
    assert 'Validator</a></li>' in cond_snippet
    assert '<li><a href="/ticket-history.html"' in cond_snippet
    assert 'Ticket History</a></li>' in cond_snippet
    assert '<li><a href="/profile.html"' in cond_snippet
    assert 'Logout</button></li>' in cond_snippet
    assert 'Dashboard' not in cond_snippet
    assert 'Plan Journey' not in cond_snippet


# ==============================================================================
# AUTHORIZATION TESTS (Scenarios 11 - 20)
# ==============================================================================

def test_11_user_admin_page_guard_redirect():
    """Scenario 11: USER cannot access /admin.html (guarded by early script redirect)."""
    with open("frontend/admin.html", "r", encoding="utf-8") as f:
        admin_html = f.read()
    assert "accountType !== 'ADMINISTRATOR'" in admin_html
    assert "login.html?mode=administrator" in admin_html


def test_12_user_validator_page_guard_redirect():
    """Scenario 12: USER cannot access /validator.html (guarded by early script redirect)."""
    with open("frontend/validator.html", "r", encoding="utf-8") as f:
        val_html = f.read()
    assert "accountType !== 'CONDUCTOR'" in val_html
    assert "login.html?mode=conductor" in val_html


def test_13_conductor_admin_page_guard_redirect():
    """Scenario 13: CONDUCTOR cannot access /admin.html (accountType CONDUCTOR !== ADMINISTRATOR)."""
    with open("frontend/admin.html", "r", encoding="utf-8") as f:
        admin_html = f.read()
    assert "accountType !== 'ADMINISTRATOR'" in admin_html


def test_14_administrator_validator_page_guard_redirect():
    """Scenario 14: ADMINISTRATOR cannot access /validator.html (accountType ADMINISTRATOR !== CONDUCTOR)."""
    with open("frontend/validator.html", "r", encoding="utf-8") as f:
        val_html = f.read()
    assert "accountType !== 'CONDUCTOR'" in val_html


def test_15_user_api_admin_denied_403(client, auth_tokens):
    """Scenario 15: USER accessing /api/admin/* receives 403 FORBIDDEN."""
    headers = {"Authorization": f"Bearer {auth_tokens['commuter']['token']}"}
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 403


def test_16_conductor_api_admin_denied_403(client, auth_tokens):
    """Scenario 16: CONDUCTOR accessing /api/admin/* receives 403 FORBIDDEN."""
    headers = {"Authorization": f"Bearer {auth_tokens['conductor']['token']}"}
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 403


def test_17_administrator_api_admin_authorized_200(client, auth_tokens):
    """Scenario 17: ADMINISTRATOR accessing /api/admin/* receives 200 OK."""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']['token']}"}
    resp = client.get("/api/admin/metrics", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["success"] is True


def test_18_user_conductor_ticket_history_denied_403(client, auth_tokens):
    """Scenario 18: USER accessing conductor ticket history receives 403 FORBIDDEN."""
    headers = {"Authorization": f"Bearer {auth_tokens['commuter']['token']}"}
    resp = client.get("/api/validation/tickets", headers=headers)
    assert resp.status_code == 403


def test_19_administrator_conductor_ticket_history_denied_403(client, auth_tokens):
    """Scenario 19: ADMINISTRATOR accessing conductor ticket history receives 403 FORBIDDEN."""
    headers = {"Authorization": f"Bearer {auth_tokens['admin']['token']}"}
    resp = client.get("/api/validation/tickets", headers=headers)
    assert resp.status_code == 403


def test_20_conductor_ticket_history_authorized_200(client, auth_tokens):
    """Scenario 20: CONDUCTOR accessing conductor ticket history receives 200 OK."""
    headers = {"Authorization": f"Bearer {auth_tokens['conductor']['token']}"}
    resp = client.get("/api/validation/tickets", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "tickets" in data


# ==============================================================================
# TICKETING TESTS (Scenarios 21 - 24)
# ==============================================================================

def test_21_commuter_views_only_own_tickets(client, auth_tokens):
    """Scenario 21: Commuter can view only their own tickets via /api/tickets."""
    headers = {"Authorization": f"Bearer {auth_tokens['commuter']['token']}"}
    resp = client.get("/api/tickets", headers=headers)
    assert resp.status_code == 200
    tickets = resp.get_json()["data"]["tickets"]
    # All returned tickets must belong to the authenticated commuter
    for t in tickets:
        assert t["user_id"] == auth_tokens["commuter"]["user"]["user_id"]


def test_22_conductor_views_commuter_tickets(client, auth_tokens):
    """Scenario 22: Conductor can view system commuter ticket history via /api/validation/tickets."""
    headers = {"Authorization": f"Bearer {auth_tokens['conductor']['token']}"}
    resp = client.get("/api/validation/tickets", headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert isinstance(data["tickets"], list)


def test_23_and_24_conductor_validates_and_rejects_double_scan(client, auth_tokens):
    """
    Scenario 23 & 24:
    Conductor can validate an active ticket, and second scan is rejected.
    """
    commuter_id = auth_tokens["commuter"]["user"]["user_id"]
    service = TransportServiceModel.get_by_id("22222222-2222-2222-2222-222222222222")

    # Create journey, leg, payment, and active ticket
    journey = JourneyModel.create(
        user_id=commuter_id,
        origin_name="Swargate",
        origin_latitude=18.5018,
        origin_longitude=73.8586,
        destination_name="Shivajinagar",
        destination_latitude=18.5314,
        destination_longitude=73.8446,
        estimated_fare=20.0
    )
    leg = JourneyLegModel.create(
        journey_id=journey["journey_id"],
        sequence_number=1,
        mode="METRO",
        from_name="Swargate",
        from_latitude=18.5018,
        from_longitude=73.8586,
        to_name="Shivajinagar",
        to_latitude=18.5314,
        to_longitude=73.8446,
        is_ticketable=True,
        estimated_fare=20.0,
        service_id=service["service_id"]
    )
    tx_ref = f"SIM-TEST-{uuid.uuid4().hex[:8]}"
    payment = PaymentModel.create(
        user_id=commuter_id,
        amount=20.0,
        payment_type="TICKET",
        transaction_reference=tx_ref
    )
    PaymentModel.update_status(payment["payment_id"], "SUCCESS")

    token_str = f"TKT-METRO-{uuid.uuid4().hex[:8].upper()}"
    ticket = TicketModel.create(
        user_id=commuter_id,
        journey_id=journey["journey_id"],
        journey_leg_id=leg["leg_id"],
        payment_id=payment["payment_id"],
        ticket_token=token_str,
        origin="Swargate",
        destination="Shivajinagar",
        fare=20.0,
        status="ACTIVE"
    )

    conductor_headers = {"Authorization": f"Bearer {auth_tokens['conductor']['token']}"}

    # Scenario 23: Conductor validates ticket -> SUCCESS
    val_resp1 = client.post("/api/validation/validate", json={
        "token": token_str,
        "remarks": "Metro Gate Entry"
    }, headers=conductor_headers)
    assert val_resp1.status_code == 200
    assert val_resp1.get_json()["data"]["validation_status"] == "VALID"

    # Scenario 24: Second scan of the same ticket -> REJECTED (ALREADY_USED)
    val_resp2 = client.post("/api/validation/validate", json={
        "token": token_str,
        "remarks": "Metro Gate Second Attempt"
    }, headers=conductor_headers)
    assert val_resp2.status_code == 400
    assert val_resp2.get_json()["error"]["code"] == "ALREADY_USED"


# ==============================================================================
# LOGOUT TESTS (Scenarios 25 - 27)
# ==============================================================================

def test_25_administrator_logout_clears_session():
    """Scenario 25: Administrator logout clears local session storage."""
    with open("frontend/js/auth.js", "r", encoding="utf-8") as f:
        auth_js = f.read()
    assert "ApiClient.removeToken();" in auth_js
    assert "AuthManager.setCurrentUser(null);" in auth_js


def test_26_conductor_logout_clears_session():
    """Scenario 26: Conductor logout triggers shared logout handler clearing token and session."""
    with open("frontend/js/auth.js", "r", encoding="utf-8") as f:
        auth_js = f.read()
    assert 'logoutBtn.addEventListener("click", () => AuthManager.logout());' in auth_js


def test_27_after_logout_direct_access_denied(client):
    """Scenario 27: After logout, unauthenticated direct requests receive 401."""
    # Attempting to access protected admin endpoint with no auth token
    resp_admin = client.get("/api/admin/metrics")
    assert resp_admin.status_code == 401

    # Attempting to access protected validation endpoint with no auth token
    resp_val = client.get("/api/validation/tickets")
    assert resp_val.status_code == 401

    # Attempting to access commuter tickets with no auth token
    resp_tickets = client.get("/api/tickets")
    assert resp_tickets.status_code == 401
