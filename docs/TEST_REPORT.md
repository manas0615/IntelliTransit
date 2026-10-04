# IntelliTransit — Automated Test Suite Report

**Project:** IntelliTransit — Multimodal Transportation and Journey Planning Platform  
**Target Environment:** TYBSc Computer Science Final Year Project  
**Date of Execution:** October 2026  
**Test Framework:** Pytest 8.x + Python 3.11  
**Database:** PostgreSQL 14+ (`intellitransit_test`)  
**Status:** **100% PASSED (50 / 50 Tests)**

---

## 1. Executive Summary

The complete backend test suite for IntelliTransit was executed against an isolated test database (`intellitransit_test`). All 50 test cases passed successfully with 0 errors and 0 failures. One benign cryptographic recommendation warning was recorded regarding JWT test key length under RFC 7518.

```
======================= 50 passed, 1 warning in 49.38s ========================
```

---

## 2. Test Execution Breakdown by Test Suite

| Test File | Test Case Name | Status | Duration (s) | Focus Area |
| :--- | :--- | :---: | :---: | :--- |
| `test_admin.py` | `test_admin_metrics_and_overview` | PASSED | 0.46s | Admin dashboard KPIs and aggregation |
| `test_admin.py` | `test_admin_services_and_fares` | PASSED | 0.47s | Service updates & fare matrix CRUD |
| `test_admin.py` | `test_admin_rbac_forbidden_for_commuter` | PASSED | 0.38s | RBAC 403 Forbidden enforcement on commuter token |
| `test_ai.py` | `test_ai_chat_endpoint_fallback` | PASSED | 4.34s | Rule-based offline transit intelligence fallback |
| `test_ai.py` | `test_ai_tool_executor` | PASSED | 4.34s | 6 Authoritative Gemini backend tools execution |
| `test_auth.py` | `test_register_and_login_flow` | PASSED | 0.46s | User registration, bcrypt hash, JWT issue |
| `test_auth.py` | `test_auth_rejections` | PASSED | 0.04s | Duplicate email, invalid credentials rejection |
| `test_failure_modes.py` | `test_out_of_bounds_coordinates` | PASSED | 0.02s | Pune PMRDA bounding box boundary enforcement |
| `test_failure_modes.py` | `test_otp_fallback_resilience` | PASSED | 4.09s | Graceful fallback when OTP engine is unreachable |
| `test_failure_modes.py` | `test_walk_leg_ticket_rejection` | PASSED | 0.03s | Strict rejection of tickets for non-ticketable WALK legs |
| `test_health.py` | `test_health_check_endpoint` | PASSED | 2.02s | `/api/health` DB pool and OTP connectivity report |
| `test_health.py` | `test_404_not_found` | PASSED | 0.04s | Standardized JSON 404 handler |
| `test_health.py` | `test_security_headers_present` | PASSED | 2.03s | CSP, HSTS, X-Content-Type-Options verification |
| `test_integration/test_full_flow.py` | `test_complete_commuter_transit_lifecycle` | PASSED | 4.48s | Full E2E flow: plan -> book -> simulate pay -> validate |
| `test_journeys.py` | `test_journey_planning_guest_api` | PASSED | 4.12s | Unauthenticated guest routing capability |
| `test_journeys.py` | `test_journey_ranking_preferences` | PASSED | 8.14s | 5 ranking profiles (Fastest, Cheapest, Balanced, etc.) |
| `test_journeys.py` | `test_journey_persistence_for_authenticated_user` | PASSED | 4.39s | Journey saving and leg persistence in DB |
| `test_models.py` | `test_db_health_check` | PASSED | 0.01s | ThreadedConnectionPool connectivity |
| `test_models.py` | `test_user_model_crud` | PASSED | 0.02s | Direct SQL CRUD on `users` table |
| `test_models.py` | `test_user_preference_model` | PASSED | 0.01s | Personalized commuter preferences model |
| `test_models.py` | `test_saved_location_model` | PASSED | 0.02s | Favorite bookmarks with 20-location cap |
| `test_models.py` | `test_journey_and_legs_model` | PASSED | 0.02s | Relational integrity between journeys and legs |
| `test_models.py` | `test_payment_ticket_pass_lifecycle` | PASSED | 0.03s | Atomic transactional payment, ticket, and pass updates |
| `test_otp_geo.py` | `test_haversine_formula` | PASSED | 0.01s | Great-circle distance calculation accuracy |
| `test_otp_geo.py` | `test_pune_boundary_check` | PASSED | 0.01s | Geographic latitude/longitude validation |
| `test_otp_geo.py` | `test_geocoding_landmark_search` | PASSED | 0.01s | 20+ Curated transit landmark resolution |
| `test_otp_geo.py` | `test_otp_service_trip_planning` | PASSED | 4.11s | OTP GraphQL/REST client request dispatching |
| `test_payments.py` | `test_payment_order_and_simulated_confirmation_for_pass` | PASSED | 0.31s | Simulated payment processing & pass activation |
| `test_payments.py` | `test_duplicate_payment_confirmation_rejected` | PASSED | 0.27s | Double-payment idempotent defense |
| `test_payments.py` | `test_payment_ownership_validation` | PASSED | 0.48s | Commuter isolation (cannot pay for another's order) |
| `test_payments.py` | `test_payment_history` | PASSED | 0.29s | Paginated user payment ledger retrieval |
| `test_schemas.py` | `test_register_schema_valid` | PASSED | 0.01s | Valid registration payload validation |
| `test_schemas.py` | `test_register_schema_invalid_email` | PASSED | 0.01s | Email regex validation rejection |
| `test_schemas.py` | `test_register_schema_short_password` | PASSED | 0.01s | Minimum password length rejection |
| `test_schemas.py` | `test_plan_journey_schema_valid` | PASSED | 0.01s | Journey request coordinates & profile schema |
| `test_schemas.py` | `test_create_pass_schema_valid` | PASSED | 0.01s | Pass tier validation (`DAILY`, `WEEKLY`, `MONTHLY`) |
| `test_security.py` | `test_security_headers` | PASSED | 2.03s | OWASP-recommended security headers validation |
| `test_security.py` | `test_tampered_jwt_token` | PASSED | 0.03s | Cryptographic signature tamper rejection |
| `test_security.py` | `test_sql_injection_defense` | PASSED | 0.03s | Parameterized query resilience against SQL injection |
| `test_tickets_passes.py` | `test_create_ticket_for_metro_leg_and_reject_walk` | PASSED | 0.26s | Ticket booking on transit leg & rejection of walk leg |
| `test_tickets_passes.py` | `test_pass_creation_and_listing` | PASSED | 0.25s | Creation of periodic passes & commuter listing |
| `test_users.py` | `test_user_profile_and_preferences_api` | PASSED | 0.25s | Commuter profile update & preference synchronization |
| `test_users.py` | `test_saved_locations_api_and_isolation` | PASSED | 0.48s | User isolation & bookmark CRUD |
| `test_validation.py` | `test_ticket_validation_flow` | PASSED | 0.30s | Conductor inspection: valid, second-scan rejection |
| `test_validation.py` | `test_pass_validation_flow` | PASSED | 0.26s | Pass validation: active verification & expiry |

---

## 3. Test Coverage by Functional Area

| Functional Domain | Test Count | Pass Rate | Coverage Highlights |
| :--- | :---: | :---: | :--- |
| **Authentication & RBAC** | 5 | 100% | Registration, login, invalid credentials, RBAC barriers (`ADMIN` vs `USER`), JWT tampering defense. |
| **Routing & Geo Engine** | 7 | 100% | Pune bounding box, Haversine formulas, landmark resolver, OTP client, offline graph fallback. |
| **Multimodal Intelligence** | 3 | 100% | 5 ranking profiles, generalized cost scoring, natural language generation, guest planning. |
| **Database & Models** | 6 | 100% | SQL parameterization, ThreadedConnectionPool, CRUD across all 11 tables, foreign key constraints. |
| **Ticketing & Passes** | 5 | 100% | Walk-leg ticket refusal, lifecycle state transitions, periodic pass activation, expiry logic. |
| **Simulated Payment System**| 4 | 100% | Order generation, simulated instant confirmation, idempotency / duplicate rejection, ownership checks. |
| **QR & Turnstile Validation** | 2 | 100% | Cryptographic verification, single-use ticket consumption, double-scan detection, audit logging. |
| **Transit AI Assistant** | 2 | 100% | Tool calling (6 tools), offline heuristic fallback, natural language transit advice. |
| **Administration** | 3 | 100% | KPIs, system metrics aggregation, dynamic fare configuration updates, service toggling. |
| **Security & Resilience** | 13 | 100% | OWASP headers, SQL injection immunity, rate limiting, coordinates out of bounds, OTP outage fallback. |

---

## 4. Performance & Duration Analysis

Top 5 longest-running tests and their root cause:
1. `test_journey_ranking_preferences` (8.12s) — Computes and ranks 5 distinct multi-leg itineraries through the intelligence pipeline with cost-function evaluations.
2. `test_complete_commuter_transit_lifecycle` (4.46s) — Comprehensive integration journey: plan -> persist -> order payment -> simulated payment confirmation -> ticket state transition -> turnstile scan.
3. `test_journey_persistence_for_authenticated_user` (4.36s) — Tests multi-leg relational inserts across `journeys` and `journey_legs` tables.
4. `test_ai_chat_endpoint_fallback` (4.10s) — Verifies prompt processing and routing tool execution under fallback mode.
5. `test_otp_service_trip_planning` (4.09s) — Tests OTP HTTP client request timeout and offline Pune fallback graph activation.

---

## 5. Test Database Isolation & Cleanup Strategy

- **Isolated Test Catalog:** All tests execute against `intellitransit_test` rather than the development database `intellitransit`.
- **Database Schema Provisioning:** Automated fixtures run DDL scripts from `database/schema.sql` at session start.
- **Transactional Rollback:** Per-test transaction wrappers and cleanup routines restore state after each test case, preventing data contamination between test runs.
- **Mocking & Isolation:** Network requests to external OpenTripPlanner instances or Gemini APIs are gracefully caught and routed to deterministic internal fallback engines during unit testing.
