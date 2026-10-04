# IntelliTransit — Viva Voce Technical Defense Summary

**Degree:** TYBSc Computer Science Final Year Project  
**Project Title:** IntelliTransit — Intelligent Multimodal Transportation and Journey Planning Platform  
**Preparation Target:** Comprehensive Technical Defense & Oral Examination  
**Contents:** 36 Exhaustive Q&A Pairs across 6 Core Engineering Domains  

---

## Domain 1: System Architecture & Engineering Design Decisions

### Q1. Why did you choose a monolithic Multi-Page Application (MPA) with an App Factory over a frontend Single-Page Application (SPA) with React/Vite?
**Answer:**  
For a transportation platform, SEO indexing, fast initial page render, and zero client-side bundling overhead are critical. A modern MPA built with vanilla HTML5, CSS3, and ES6+ modules eliminates large JavaScript bundle hydration penalties, npm dependency vulnerabilities, and build complexity. On the backend, Flask's Application Factory pattern (`create_app`) allows clear blueprint modularization, independent test configuration injection, and thread-safe request isolation without the unnecessary architectural complexity and operational latency of microservices.

### Q2. What architectural pattern governs your Flask backend?
**Answer:**  
We employ the **Application Factory pattern** coupled with **Blueprint-based modular routing** and a **layered service architecture**:
1. *Presentation/Routing Layer:* Blueprints (`auth`, `journeys`, `tickets`, `passes`, `payments`, `validation`, `ai`, `admin`, `health`) validate inputs against JSON schemas and serialize responses.
2. *Service Layer:* Encapsulates business logic (OTP client, fare computation, ranking intelligence, QR generation, AI tool orchestration).
3. *Data Access Layer:* Direct parameterized SQL models with thread-safe connection pooling, avoiding ORM overhead.

### Q3. Why did you choose direct parameterized SQL via psycopg2 instead of an ORM like SQLAlchemy?
**Answer:**  
An ORM introduces significant query abstraction overhead, hidden N+1 query traps, and schema migration impedance. Direct parameterized SQL gives us complete control over query execution plans, enables native PostgreSQL UUID generation via `gen_random_uuid()`, allows fine-tuned composite indexes, and guarantees zero SQL injection risk through parameter substitution at the database protocol level.

### Q4. How does the system handle high-concurrency database requests without leaking connections?
**Answer:**  
We implemented `psycopg2.pool.ThreadedConnectionPool` configured with a minimum of 5 and maximum of 20 connections. Each database interaction uses Python's `try...finally` construct where the connection is acquired via `get_db_connection()` and strictly guaranteed to return to the pool in the `finally` block via `release_db_connection()`, preventing connection leaks even under unhandled exceptions.

### Q5. What is the separation of responsibilities between your frontend and backend?
**Answer:**  
The backend is completely stateless and RESTful, acting as the single source of truth for business rules (fare calculation, ticketability rules, validation, and token generation). The frontend is an interactive presentation client using ES6 modules that consumes backend JSON APIs, renders dynamic map polylines via MapLibre GL JS, and manages client session state via `localStorage` JWT tokens.

### Q6. How does the system ensure resilience against external service outages?
**Answer:**  
IntelliTransit implements circuit-breaker-style defensive fallbacks:
- If OpenTripPlanner 2 is unreachable or times out, the journey planner activates an internal offline Pune multimodal routing graph (`routing_source: "OFFLINE_FALLBACK"`).
- If external LLM API endpoints are unavailable, the AI companion automatically activates a backend-authoritative heuristic transit intelligence engine.

---

## Domain 2: Routing Algorithms, GIS & OpenTripPlanner 2

### Q7. What routing algorithms are utilized in OpenTripPlanner 2?
**Answer:**  
OpenTripPlanner 2 utilizes two core algorithms:
1. **Range RAPTOR (Round-Based Public Transit Routing):** Computes Pareto-optimal transit arrival times across schedules without creating large graph state-space representations.
2. **Generalized Cost A\* (A-Star):** Computes street network walk and bicycle legs using a heuristic distance function penalized by surface type, slope, and street safety.

### Q8. What is Generalized Cost in multimodal routing?
**Answer:**  
Generalized Cost unifies time, monetary expense, and physical discomfort into a single mathematical objective function:
$$\text{Cost} = w_t \cdot t_{\text{transit}} + w_w \cdot t_{\text{walk}} + w_f \cdot \text{Fare} + w_x \cdot N_{\text{transfers}}$$
where $w$ represents weights adjusted according to commuter ranking preferences (`FASTEST`, `CHEAPEST`, `LEAST_WALKING`, `FEWEST_TRANSFERS`, `BALANCED`).

### Q9. How does IntelliTransit prevent out-of-bounds geographic routing queries?
**Answer:**  
Before dispatching any query to OTP or the routing engine, coordinates are verified against the Pune Metropolitan Region Development Authority (PMRDA) geographic bounding box:
- Latitude: $[18.3000^\circ\text{N}, 18.8000^\circ\text{N}]$
- Longitude: $[73.6500^\circ\text{E}, 74.1500^\circ\text{E}]$  
Coordinates outside this envelope are rejected with HTTP 400 `OUT_OF_BOUNDS`.

### Q10. What geographic distance formula is implemented for spatial validation?
**Answer:**  
We implement the **Haversine Formula** to compute great-circle distances over the spherical surface of the Earth:
$$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$
where $r = 6371\text{ km}$. This provides sub-meter precision for walking distance calculations and landmark matching.

### Q11. How does the system handle transit map rendering on the browser?
**Answer:**  
We use **MapLibre GL JS**, an open-source WebGL-accelerated mapping library. It renders vector and raster tiles without proprietary API keys. Route polylines are converted from OpenTripPlanner geometry strings or decoded Google Encoded Polylines into standard GeoJSON FeatureCollections, styled with distinct modal colors:
- Blue: Metro
- Green: PMPML Bus
- Amber/Dashed: Pedestrian Walk
- Orange: Taxi / Auto-Rickshaw

### Q12. How does the offline Pune transit graph fallback work?
**Answer:**  
When OTP 2 is unavailable, an embedded transit graph populated with major Pune transit hubs (e.g., Swargate, Pune Station, Katraj, Hadapsar, Kothrud, Hinjawadi) uses Dijkstra's shortest path algorithm combined with Pune Metro lines 1 & 2 to generate realistic, valid multimodal itineraries.

---

## Domain 3: Database Design, Normalization & Relational Integrity

### Q13. What normal form does the IntelliTransit PostgreSQL database achieve?
**Answer:**  
The database conforms strictly to **Third Normal Form (3NF)**:
1. *1NF:* All attributes are atomic; no repeating groups or arrays stored as text.
2. *2NF:* All non-key attributes are fully functionally dependent on primary keys (no partial key dependencies).
3. *3NF:* No transitive dependencies exist (e.g., fare configuration rates reside in `fare_configurations`, referenced by `service_id`, rather than duplicated across `journey_legs`).

### Q14. Why are UUIDs used as primary keys instead of auto-incrementing integers?
**Answer:**  
UUIDs generated via PostgreSQL's `gen_random_uuid()` provide:
- Immunity against enumeration attacks (attackers guessing sequential `ticket_id=1, 2, 3`).
- Safe distributed generation across services and offline clients without ID collision.
- Secure, cryptographically random reference identifiers for tickets and QR tokens.

### Q15. How is relational integrity enforced between journeys, legs, and tickets?
**Answer:**  
Through relational foreign key constraints and cascade rules:
- `journey_legs` enforces `ON DELETE CASCADE` from `journeys`.
- `tickets` references `journey_leg_id` with `ON DELETE RESTRICT`, preventing a journey leg from being deleted if an active ticket has been purchased for it.
- A unique constraint `(journey_id, sequence_number)` prevents duplicated leg ordering.

### Q16. How does the database enforce that only ticketable legs receive tickets?
**Answer:**  
`journey_legs` contains an `is_ticketable BOOLEAN NOT NULL DEFAULT FALSE` flag. This is evaluated to `TRUE` strictly for `BUS` and `METRO` legs. The ticket booking API verifies this flag before initiating payment; if a commuter attempts to book a `WALK` or non-ticketable leg, the API rejects the request with HTTP 400 `WALK_LEG_NOT_TICKETABLE`.

### Q17. How is database isolation maintained during automated testing?
**Answer:**  
`pytest.ini` specifies an isolated test database connection string `intellitransit_test`. Pytest test fixtures execute schema migration scripts on initialization, run tests in clean transaction contexts, and clean up test rows upon completion, preventing development database pollution.

### Q18. What indexes are implemented, and what is their performance rationale?
**Answer:**  
- `idx_users_email` & `idx_users_phone`: B-Tree indexes for $O(\log n)$ credential lookup during authentication.
- `idx_journeys_user_id` & `idx_journeys_created_at`: For fast retrieval of commuter history sorted by date.
- `idx_tickets_token` & `idx_passes_token`: Unique indexes for sub-millisecond lookup during turnstile QR scans.
- `idx_payments_tx_ref`: For idempotent payment confirmation lookups.

---

## Domain 4: Security, Authentication & Role-Based Access Control

### Q19. How is user authentication implemented?
**Answer:**  
We utilize stateless **JSON Web Tokens (JWT)** signed with HMAC-SHA256 (`HS256`). When a user logs in, their password is verified using `bcrypt` (work factor 12). If valid, a JWT containing claims (`user_id`, `email`, `role`, `exp`, `iat`) is issued with a 24-hour expiration window.

### Q20. How is Role-Based Access Control (RBAC) enforced?
**Answer:**  
The system strictly enforces two roles: `USER` (Commuter) and `ADMIN` (Transit Authority). Role membership is verified at both the database level (`CHECK role IN ('USER', 'ADMIN')`) and via Python decorator `@admin_required`:
```python
@admin_blueprint.route('/metrics')
@jwt_required
@admin_required
def admin_metrics(current_user):
    # Only users with role == 'ADMIN' can access
```
Commuters attempting to access administrative endpoints receive an immediate HTTP 403 Forbidden.

### Q21. How does the platform defend against SQL Injection?
**Answer:**  
All database interactions use psycopg2's parameterized query syntax (`%s` placeholders):
```python
cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
```
User inputs are passed out-of-band to the database query planner as literals, making SQL injection mathematically impossible regardless of input content.

### Q22. What HTTP security headers are configured?
**Answer:**  
Every response includes OWASP-recommended security headers injected via an `@app.after_request` middleware hook:
- `Content-Security-Policy`: Restricts script and style execution to trusted origins and inline nonces.
- `Strict-Transport-Security`: Enforces HTTPS (`max-age=31536000; includeSubDomains`).
- `X-Content-Type-Options`: Prevents MIME-type sniffing (`nosniff`).
- `X-Frame-Options`: Prevents clickjacking attacks (`DENY`).
- `X-XSS-Protection`: Enables legacy browser XSS filters (`1; mode=block`).

### Q23. How does the system defend against brute-force and Denial-of-Service attacks?
**Answer:**  
We implemented an in-memory sliding window rate limiter middleware. It tracks client requests keyed by IP address:
- Authentication endpoints (`/api/auth/*`): 10 requests per minute.
- Journey planning (`/api/journeys/plan`): 30 requests per minute.
- General endpoints: 120 requests per minute.  
Exceeded thresholds return HTTP 429 Too Many Requests with a `Retry-After` header.

### Q24. How are password hashes protected against rainbow table attacks?
**Answer:**  
Passwords are never stored in plain text. They are hashed using **bcrypt** with a cost factor (salt rounds) of 12. Bcrypt automatically generates a cryptographically secure 128-bit salt for every password, ensuring that identical passwords result in completely different hashes and defeating precomputed rainbow tables.

---

## Domain 5: Ticketing Lifecycle, Simulated Payments & QR Verification

### Q25. Why did you choose a Simulated Payment System instead of Razorpay or Stripe?
**Answer:**  
For an academic demonstration, third-party payment gateways introduce real-world dependencies: unstable external sandboxes, required credit card test details, network latency, and test API key deprecation. A simulated payment system models the **exact transactional lifecycle** (Order Creation $\rightarrow$ Pending $\rightarrow$ Confirmation $\rightarrow$ Atomic Activation $\rightarrow$ Ledger Audit) completely on-premises without external point-of-failure risks.

### Q26. Explain the state lifecycle of a transit ticket.
**Answer:**  
A ticket progresses through a strict finite state machine:
$$\text{PENDING} \xrightarrow{\text{Simulated Payment}} \text{ACTIVE} \xrightarrow{\text{Conductor Scan}} \text{USED}$$
- If unused within the validity window: $\text{ACTIVE} \rightarrow \text{EXPIRED}$.
- If user cancels before validity: $\text{PENDING} / \text{ACTIVE} \rightarrow \text{CANCELLED}$.

### Q27. How does the turnstile prevent double-scanning or ticket reuse?
**Answer:**  
When a conductor scans a QR code (`POST /api/validation/scan`):
1. The server looks up the ticket by unique token.
2. If status is `USED`, it immediately rejects the scan as `INVALID - ALREADY USED` and returns the timestamp of the prior scan.
3. If status is `ACTIVE` and current time is within `[valid_from, valid_until]`, it atomically updates status to `USED` and inserts an audit record into `ticket_validations`.

### Q28. How is the QR code generated and formatted?
**Answer:**  
QR codes are generated using Python's `qrcode` library backed by `Pillow`. The payload encoded inside the QR matrix is not plain text; it is a structured, tamper-evident token:
```
TKT-<UUID>-<TIMESTAMP>
```
The endpoint `/api/tickets/<ticket_id>/qr` streams this as an optimized PNG or data URI directly to the frontend.

### Q29. What is the difference between a Ticket and a Pass?
**Answer:**  
- **Ticket:** Leg-specific, single-use, bound to a specific origin and destination on a transit service (e.g., Metro Line 1), transitioning to `USED` upon boarding.
- **Pass:** Periodic (Daily, Weekly, Monthly), multi-ride credential valid across all participating PMPML bus and Pune Metro lines throughout its active duration, remaining `ACTIVE` through multiple validations until `valid_until` expires.

### Q30. How is payment idempotency guaranteed?
**Answer:**  
In `payments.py`, when a payment confirmation request is received, the transaction reference is checked against existing records. If the payment record is already in `SUCCESS` state, the endpoint rejects the duplicate confirmation with an error `ALREADY_PAID`, preventing double processing.

---

## Domain 6: AI Intelligence, Function Calling & Frontend Engineering

### Q31. What is the architecture of the AI Transit Assistant?
**Answer:**  
The AI Assistant acts as a natural language interface to the transit engine. It utilizes an LLM (Gemini 2.5 Flash) with **Function Calling / Tool Calling**. The LLM itself does not calculate fares or routes; instead, it outputs structured tool calls that the backend executes authoritatively.

### Q32. What 6 authoritative tools are registered with the AI assistant?
**Answer:**  
1. `find_transit_routes`: Calls journey orchestrator for origins and destinations.
2. `get_fare_estimate`: Queries fare configurations for distances and modes.
3. `get_service_status`: Checks active transport service operational status.
4. `get_station_information`: Returns landmark coordinates and connecting lines.
5. `explain_route_options`: Generates trade-off summaries between fastest vs cheapest.
6. `recommend_transit_pass`: Recommends Daily vs Monthly passes based on trip frequency.

### Q33. How does the AI Assistant behave in Demo AI Mode without an active Gemini API key?
**Answer:**  
The assistant detects the absence of an API key and seamlessly falls back to an internal **Rule-Based Transit Intelligence Engine**. It parses intent (routing, fare inquiry, pass recommendation), invokes the identical backend tools, and formats structured, accurate responses without external API latency or quota limits.

### Q34. Why did you choose vanilla ES6+ JavaScript modules over a bundled framework?
**Answer:**  
Vanilla ES6 modules (`import` / `export`) are natively supported by all modern browsers. This eliminates the need for Node.js build steps, Webpack/Vite bundlers, and package lockfiles. Code execution is transparent, debuggable directly in browser DevTools, and loads with zero latency.

### Q35. How does the frontend handle responsive UI across mobile and desktop devices?
**Answer:**  
The UI utilizes CSS custom properties (design tokens), responsive CSS Grid (`grid-template-columns`), and flexbox layouts with mobile-first media queries (`@media (max-width: 768px)`). On mobile screens, the journey planner collapses into a tabbed view switching seamlessly between itinerary cards and the full-height MapLibre map.

### Q36. What is the project's academic significance and future scope?
**Answer:**  
*Academic Significance:* It demonstrates the practical realization of a complex, full-stack Distributed Information System combining GIS algorithms (Range RAPTOR/A*), relational database normalization, state machine ticketing, OWASP security, and AI tool calling for an Indian metropolitan context.  
*Future Scope:* Integrating live GTFS-Realtime vehicle tracking streams, integrating Unified Payments Interface (UPI) live production rail, and implementing automated turnstile NFC card emulation.
