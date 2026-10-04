# IntelliTransit — System Feature Verification Matrix

**Project:** IntelliTransit (PMRDA Multimodal Transit System)  
**Verification Scope:** Packages PKG-01 through PKG-13  
**Status:** **100% OPERATIONAL & VERIFIED**

---

| Package | Feature ID | Feature Name | Description | Backend Endpoint | Frontend UI | Status | Evidence / Test |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **PKG-01** | `CFG-01` | Environment Config | Strict 12-factor `.env` loading, debug flags, and secrets. | N/A (App Bootstrap) | N/A | **Verified** | Config module loads cleanly in tests |
| **PKG-01** | `CFG-02` | Dependency Isolation | Lean virtualenv dependencies (12 core libraries, zero Razorpay). | N/A | N/A | **Verified** | `backend/requirements.txt` audit |
| **PKG-02** | `DB-01` | 11 Core Tables | Relational schema with UUIDs, strict types, and checks. | PostgreSQL | N/A | **Verified** | `test_models.py` |
| **PKG-02** | `DB-02` | Connection Pool | Threaded connection pooling (5-20 connections). | `get_db_connection()` | N/A | **Verified** | `test_db_health_check` |
| **PKG-03** | `SEC-01` | OWASP Headers | CSP, HSTS, X-Content-Type-Options, X-Frame-Options. | All endpoints | All pages | **Verified** | `test_security_headers_present` |
| **PKG-03** | `SEC-02` | Rate Limiting | In-memory sliding window rate limiter per client IP. | Middleware | All pages | **Verified** | Middleware unit tests |
| **PKG-04** | `AUTH-01` | User Registration | Commuter registration with bcrypt hashing (work factor 12). | `POST /api/auth/register` | `login.html` | **Verified** | `test_register_and_login_flow` |
| **PKG-04** | `AUTH-02` | JWT Authentication | Stateless HS256 JWT tokens with role claims. | `POST /api/auth/login` | `login.html` | **Verified** | `test_register_and_login_flow` |
| **PKG-04** | `AUTH-03` | Saved Locations | Commuter bookmarks with a 20-location boundary cap. | `GET/POST /api/users/saved-locations`| Profile Modal | **Verified** | `test_saved_locations_api_and_isolation` |
| **PKG-04** | `AUTH-04` | User Preferences | Commuter modal preference & route weight storage. | `GET/PUT /api/users/preferences` | Profile Modal | **Verified** | `test_user_profile_and_preferences_api` |
| **PKG-05** | `ROUT-01` | Boundary Check | Coordinate bounding box filtering for Pune PMRDA. | `POST /api/journeys/plan` | `planner.html` | **Verified** | `test_pune_boundary_check` |
| **PKG-05** | `ROUT-02` | Landmark Geocoding | Autocomplete for 20+ Pune transit landmarks. | Geocoder service | `planner.html` | **Verified** | `test_geocoding_landmark_search` |
| **PKG-05** | `ROUT-03` | OTP Engine Integration| Range RAPTOR & Generalized Cost A* journey routing. | OTP REST Client | `planner.html` | **Verified** | `test_otp_service_trip_planning` |
| **PKG-05** | `ROUT-04` | Offline Pune Fallback | Built-in offline fallback graph when OTP is inactive. | Fallback Routing Engine | `planner.html` | **Verified** | `test_otp_fallback_resilience` |
| **PKG-06** | `INT-01` | Multimodal Pipeline | Orchestration of Bus + Metro + Walk + Taxi journeys. | `POST /api/journeys/plan` | `planner.html` | **Verified** | `test_journey_planning_guest_api` |
| **PKG-06** | `INT-02` | 5 Ranking Profiles | Balanced, Fastest, Cheapest, Min Transfers, Least Walking.| Ranking Engine | `planner.html` | **Verified** | `test_journey_ranking_preferences` |
| **PKG-06** | `INT-03` | Fare Calculator | Dynamic distance/flat fare calculation per leg. | Fare Engine | `planner.html` | **Verified** | `test_journey_and_legs_model` |
| **PKG-06** | `INT-04` | AI Explanations | Natural language journey summaries and advice. | Intelligence Layer | `planner.html` | **Verified** | Browser test & journey schema |
| **PKG-07** | `UI-01` | Responsive MPA | Vanilla HTML5/CSS3/ES6+ UI without frontend framework bloat.| Static HTTP | All pages | **Verified** | Browser verification |
| **PKG-07** | `UI-02` | MapLibre GL Map | Vector/raster tile map with zoom, markers, and fits. | MapLibre GL JS | `planner.html` | **Verified** | Browser verification |
| **PKG-08** | `UI-03` | Route Visualizer | Colored GeoJSON polylines for walking, bus, metro, taxi. | MapLibre layers | `planner.html` | **Verified** | Browser verification |
| **PKG-08** | `UI-04` | Guest Mode Planning | Direct journey calculation without mandatory sign-in. | `POST /api/journeys/plan` | `planner.html` | **Verified** | `test_journey_planning_guest_api` |
| **PKG-09** | `TKT-01` | Leg-Based Ticketing | Individual booking on transit legs (`BUS`, `METRO`). | `POST /api/tickets/book` | `planner.html` | **Verified** | `test_create_ticket_for_metro_leg_and_reject_walk` |
| **PKG-09** | `TKT-02` | Walk Leg Rejection | Refusal to create tickets for pedestrian walking legs. | `POST /api/tickets/book` | `planner.html` | **Verified** | `test_walk_leg_ticket_rejection` |
| **PKG-09** | `TKT-03` | Periodic Passes | Daily, Weekly, and Monthly multi-ride transit passes. | `POST /api/passes/create` | `passes.html` | **Verified** | `test_pass_creation_and_listing` |
| **PKG-10** | `PAY-01` | Simulated Payment Order | Order creation with reference `SIM-PAY-...`. | `POST /api/payments/create-order` | Modal | **Verified** | `test_payment_order_and_simulated_confirmation_for_pass` |
| **PKG-10** | `PAY-02` | Simulated Confirmation | Instant atomic confirmation transitioning tickets to ACTIVE. | `POST /api/payments/simulate-confirm`| Modal | **Verified** | `test_payment_order_and_simulated_confirmation_for_pass` |
| **PKG-10** | `PAY-03` | Double-Payment Defense| Idempotency check rejecting duplicate confirmations. | `POST /api/payments/simulate-confirm`| Modal | **Verified** | `test_duplicate_payment_confirmation_rejected` |
| **PKG-11** | `VAL-01` | QR Code Generation | Scannable QR token generation (`qrcode` + `Pillow`). | `GET /api/tickets/<id>/qr` | `tickets.html` | **Verified** | Browser verification |
| **PKG-11** | `VAL-02` | Conductor Inspection | QR scanning and token validation endpoint. | `POST /api/validation/scan` | `validator.html` | **Verified** | `test_ticket_validation_flow` |
| **PKG-11** | `VAL-03` | Double-Scan Defense | Single-use consumption (status changes to `USED`). | `POST /api/validation/scan` | `validator.html` | **Verified** | `test_ticket_validation_flow` |
| **PKG-12** | `AI-01` | Transit Assistant UI | Conversational UI with dynamic model indicator badge. | `POST /api/ai/chat` | `ai-assistant.html`| **Verified** | Browser verification |
| **PKG-12** | `AI-02` | 6 Authoritative Tools| Live backend tool execution for routes, fares, and status. | Gemini Tool Executor | `ai-assistant.html`| **Verified** | `test_ai_tool_executor` |
| **PKG-12** | `AI-03` | Heuristic Fallback | Rule-based offline transit engine when API key is missing. | Fallback Assistant | `ai-assistant.html`| **Verified** | `test_ai_chat_endpoint_fallback` |
| **PKG-13** | `ADM-01` | Admin Dashboard | KPI cards, simulated revenue counter, active tickets. | `GET /api/admin/metrics` | `admin.html` | **Verified** | `test_admin_metrics_and_overview` |
| **PKG-13** | `ADM-02` | Dynamic Fare Matrix | Real-time updating of base fares and per-km rates. | `PUT /api/admin/fares/<id>` | `admin.html` | **Verified** | `test_admin_services_and_fares` |
| **PKG-13** | `ADM-03` | RBAC Enforcement | Strict blocking of non-admin commuters from `/api/admin`. | Middleware RBAC | `admin.html` | **Verified** | `test_admin_rbac_forbidden_for_commuter` |
