# IntelliTransit — System Architecture

**Document:** `02_SYSTEM_ARCHITECTURE.md`  
**Project:** IntelliTransit  
**Depends on:** `01_PROJECT_DEFINITION.md`  
**Status:** ARCHITECTURE BASELINE

---

# 1. Purpose

This document defines the technical architecture of IntelliTransit.

It converts the frozen project decisions from `01_PROJECT_DEFINITION.md` into an implementation-level architecture.

This document defines:

- system components;
- responsibilities of each component;
- communication between components;
- frontend/backend boundaries;
- Flask application structure;
- PostgreSQL boundary;
- OpenTripPlanner integration;
- OpenStreetMap/MapLibre integration;
- Gemini integration;
- Razorpay integration;
- ticket and QR flow;
- authentication flow;
- guest/user/admin boundaries;
- error and dependency boundaries.

This is an academic project architecture.

The architecture must remain understandable and implementable by a TYBSc development team.

---

# 2. Architectural Principles

The following principles are mandatory.

## 2.1 Simplicity First

Use the simplest architecture that can implement the defined requirements.

Do not introduce:

- microservices;
- Kubernetes;
- message brokers;
- unnecessary caching systems;
- Redis unless a later requirement genuinely requires it;
- separate frontend frameworks;
- unnecessary databases;
- Docker as a core dependency.

The initial application is a **single Flask backend + browser frontend + PostgreSQL + external routing/AI/payment services**.

---

## 2.2 Clear Responsibility Boundaries

Each major technology has one primary responsibility.

```text
HTML
    → page structure

CSS
    → visual styling/responsive layout

JavaScript
    → browser interaction/API communication/map interaction

Flask
    → backend/API/application orchestration

PostgreSQL
    → application/business persistence

OpenTripPlanner
    → multimodal journey calculation

IntelliTransit Intelligence Layer
    → route ranking, preferences, fare handling, presentation

OpenStreetMap
    → geographic/street data

MapLibre GL JS
    → map visualization

Gemini 2.5 Flash
    → conversational transportation assistance

Razorpay
    → test payment processing
```

No component should perform another component's primary responsibility without a deliberate architectural reason.

---

# 3. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │       USER          │
                         │ Desktop / Mobile    │
                         │      Browser        │
                         └──────────┬──────────┘
                                    │
                              HTTP / HTTPS
                                    │
                                    ▼
                  ┌─────────────────────────────────┐
                  │       INTELLITRANSIT WEB        │
                  │            FRONTEND             │
                  │                                 │
                  │ HTML + CSS + JavaScript         │
                  │ MapLibre GL JS                  │
                  └────────────────┬────────────────┘
                                   │
                              REST / JSON
                                   │
                                   ▼
                  ┌─────────────────────────────────┐
                  │          FLASK BACKEND          │
                  │                                 │
                  │ Authentication                  │
                  │ Journey API                     │
                  │ User API                        │
                  │ Ticket API                      │
                  │ Pass API                        │
                  │ Payment API                     │
                  │ AI API                          │
                  │ Admin API                       │
                  │ Validation API                  │
                  │                                 │
                  │ IntelliTransit Intelligence     │
                  │ Layer                           │
                  └───────┬─────────┬─────────┬─────┘
                          │         │         │
                          │         │         │
              ┌───────────┘         │         └───────────────┐
              │                     │                         │
              ▼                     ▼                         ▼
      ┌──────────────┐      ┌──────────────┐         ┌──────────────┐
      │ PostgreSQL   │      │ OpenTrip-    │         │ Gemini API   │
      │              │      │ Planner 2    │         │              │
      │ Application  │      │              │         │ Gemini 2.5   │
      │ Data         │      │ Routing      │         │ Flash        │
      └──────────────┘      └──────┬───────┘         └──────────────┘
                                   │
                              OSM + GTFS
                                   │
                                   ▼
                         Transportation Network

                         ┌─────────────────┐
                         │ Razorpay Test   │
                         │ Mode            │
                         └─────────────────┘
```

---

# 4. Major System Components

The system consists of the following logical components.

## 4.1 Browser Frontend

Technology:

- HTML5
- CSS3
- JavaScript ES6+

Responsibilities:

- display application pages;
- collect user input;
- call Flask REST APIs;
- display journey results;
- display maps;
- display route alternatives;
- display tickets and passes;
- display QR codes;
- display user information;
- provide AI chat interface;
- display errors and loading states;
- provide responsive layouts.

The frontend must not contain:

- database credentials;
- Gemini API keys;
- Razorpay secret keys;
- PostgreSQL connection logic;
- direct privileged access to OTP.

The browser communicates with the Flask backend.

---

# 5. Frontend Architecture

The frontend remains framework-free.

Recommended structure:

```text
frontend/
│
├── index.html
├── pages/
│   ├── login.html
│   ├── register.html
│   ├── planner.html
│   ├── journey.html
│   ├── tickets.html
│   ├── passes.html
│   ├── history.html
│   ├── profile.html
│   ├── ai-assistant.html
│   ├── admin.html
│   └── validator.html
│
├── css/
│   ├── main.css
│   ├── layout.css
│   ├── components.css
│   ├── forms.css
│   ├── map.css
│   └── responsive.css
│
├── js/
│   ├── api.js
│   ├── auth.js
│   ├── planner.js
│   ├── journey.js
│   ├── map.js
│   ├── tickets.js
│   ├── passes.js
│   ├── payment.js
│   ├── ai.js
│   ├── profile.js
│   ├── admin.js
│   ├── validator.js
│   └── utils.js
│
└── assets/
    ├── images/
    └── icons/
```

This is a logical organization.

The exact directory structure may be adjusted during implementation if Flask's static/template conventions make another arrangement cleaner.

---

# 6. Flask Backend Architecture

The backend is a single Python Flask application.

Recommended logical structure:

```text
backend/
│
├── app.py
├── config.py
│
├── routes/
│   ├── auth_routes.py
│   ├── journey_routes.py
│   ├── user_routes.py
│   ├── ticket_routes.py
│   ├── pass_routes.py
│   ├── payment_routes.py
│   ├── ai_routes.py
│   ├── admin_routes.py
│   └── validation_routes.py
│
├── services/
│   ├── auth_service.py
│   ├── journey_service.py
│   ├── otp_service.py
│   ├── intelligence_service.py
│   ├── fare_service.py
│   ├── ticket_service.py
│   ├── pass_service.py
│   ├── payment_service.py
│   ├── qr_service.py
│   ├── ai_service.py
│   └── user_service.py
│
├── models/
│   ├── user.py
│   ├── preference.py
│   ├── saved_location.py
│   ├── journey.py
│   ├── transport_service.py
│   ├── fare_configuration.py
│   ├── payment.py
│   ├── ticket.py
│   ├── pass.py
│   └── ticket_validation.py
│
├── middleware/
│   ├── auth.py
│   ├── authorization.py
│   └── error_handler.py
│
├── utils/
│   ├── validators.py
│   ├── responses.py
│   └── security.py
│
└── tests/
```

This is a logical architecture, not a requirement to create every file immediately.

---

# 7. Flask Application Responsibilities

Flask acts as the central backend.

It is responsible for:

1. Receiving frontend requests.
2. Validating request data.
3. Authenticating users.
4. Authorizing protected operations.
5. Calling application services.
6. Communicating with PostgreSQL.
7. Communicating with OpenTripPlanner.
8. Calling the IntelliTransit Intelligence Layer.
9. Calling Gemini when required.
10. Creating/verifying Razorpay orders/payments.
11. Generating and validating QR tokens.
12. Returning structured JSON responses.
13. Handling errors safely.

Flask should not contain large amounts of business logic directly inside route functions.

Routes should delegate to services.

---

# 8. Backend Layering

Use a simple three-level application organization:

```text
Route / API Layer
        ↓
Service Layer
        ↓
Data / External Integration Layer
```

Example:

```text
GET /api/journeys/plan
        ↓
journey_routes.py
        ↓
journey_service.py
        ↓
otp_service.py
        ↓
OpenTripPlanner
```

For database operations:

```text
API Route
   ↓
Service
   ↓
Model / Database access
   ↓
PostgreSQL
```

The purpose is separation, not enterprise-level abstraction.

---

# 9. Authentication Architecture

Authentication uses:

- bcrypt for password hashing;
- JWT for authenticated API access.

Registration:

```text
User
 ↓
Registration form
 ↓
POST /api/auth/register
 ↓
Validate input
 ↓
Hash password with bcrypt
 ↓
Create PostgreSQL user
 ↓
Return registration result
```

Login:

```text
User
 ↓
Email + password
 ↓
POST /api/auth/login
 ↓
Find user
 ↓
Verify bcrypt hash
 ↓
Generate JWT
 ↓
Return authentication response
```

Authenticated request:

```text
Browser
 ↓
JWT
 ↓
Flask authentication middleware
 ↓
Token validation
 ↓
User identity + role
 ↓
Protected endpoint
```

---

# 10. Guest/User/Admin Architecture

## Guest

Allowed:

```text
Journey planning
Route comparison
Map viewing
Basic AI journey assistance
```

No account required.

## USER

Allowed:

```text
All guest functionality
+
Saved locations
Preferences
Journey history
Tickets
Passes
Payments/history
Personalization
```

## ADMIN

Allowed:

```text
All appropriate application functions
+
Transport metadata management
Fare configuration management
Authorized ticket/pass management
Ticket validation functions
```

Authorization must be checked server-side.

The frontend must not be the only security boundary.

---

# 11. Journey Planning Architecture

This is the most important system flow.

```text
User
 ↓
Origin + Destination
 ↓
Optional time/preferences
 ↓
Frontend JavaScript
 ↓
POST /api/journeys/plan
 ↓
Flask
 ↓
Input validation
 ↓
Journey Service
 ↓
OTP Service
 ↓
OpenTripPlanner 2
 ↓
Candidate itineraries
 ↓
IntelliTransit Intelligence Layer
 ↓
Ranking + fare handling + preference processing
 ↓
Journey response
 ↓
Frontend
 ↓
MapLibre + journey cards
```

---

# 12. OpenTripPlanner Boundary

OpenTripPlanner is treated as an external routing engine from the Flask application's perspective.

Flask communicates with OTP through its supported API/interface.

The application must not directly manipulate OTP's internal routing algorithms.

Conceptually:

```text
Flask
  │
  │ Journey request
  ▼
OTP 2
  │
  │ Routing calculation
  ▼
OTP itinerary response
  │
  ▼
Flask
```

OTP uses its own routing algorithms internally.

The application only consumes the resulting itineraries.

---

# 13. OTP Integration Isolation

All OTP communication should be isolated behind:

```text
otp_service.py
```

No frontend code should directly call OTP.

No unrelated Flask route should directly contain OTP-specific HTTP logic.

Example:

```text
journey_routes.py
        ↓
journey_service.py
        ↓
otp_service.py
        ↓
OpenTripPlanner
```

This provides a clean boundary if OTP configuration or integration details need to change later.

---

# 14. IntelliTransit Intelligence Layer

The Intelligence Layer receives candidate journeys from OTP.

Conceptual input:

```text
[
    itinerary_1,
    itinerary_2,
    itinerary_3,
    ...
]
```

The layer can process:

- total duration;
- walking distance;
- transfers;
- estimated fare;
- user preferences;
- route type.

It then produces a user-facing ranking/presentation.

Possible user preferences:

```text
FASTEST
CHEAPEST
LEAST_WALKING
FEWEST_TRANSFERS
BALANCED
```

The exact scoring implementation will be defined in `05_ROUTING_AND_INTELLIGENCE.md`.

The important architectural rule is:

> The Intelligence Layer ranks and processes routes returned by OTP. It does not invent routes.

---

# 15. Map Architecture

Map rendering occurs in the browser.

```text
Flask
 ↓
Journey response
 ↓
Route geometry + stops + journey metadata
 ↓
JavaScript map module
 ↓
MapLibre GL JS
 ↓
Interactive map
```

MapLibre is not responsible for routing.

The map should be able to show:

- origin;
- destination;
- route line;
- walking segments;
- bus segments;
- metro segments;
- transfer locations;
- relevant stops/stations.

---

# 16. Database Architecture

PostgreSQL is the persistent application database.

```text
Flask
  │
  ├── User data
  ├── Preferences
  ├── Saved locations
  ├── Journey summaries
  ├── Payments
  ├── Tickets
  ├── Passes
  ├── Transport metadata
  ├── Fare configurations
  └── Ticket validations
             │
             ▼
        PostgreSQL
```

PostgreSQL does not store the entire OTP transit graph.

---

# 17. Journey Persistence

Not every route-planning request needs permanent storage.

### Guest

Journey planning can remain transient.

### Registered User

A selected/meaningful journey can be stored in `journeys`.

The database stores an application-level journey summary, such as:

- origin;
- destination;
- coordinates;
- departure/arrival;
- duration;
- walking distance;
- estimated fare;
- route type;
- OTP itinerary reference.

It should not duplicate the entire transit network.

---

# 18. AI Architecture

The AI assistant is integrated through Flask.

Correct flow:

```text
User message
 ↓
Frontend
 ↓
POST /api/ai/chat
 ↓
Flask AI service
 ↓
Gemini 2.5 Flash
 ↓
Tool/function request if needed
 ↓
Flask executes approved function
 ↓
OTP / PostgreSQL / application services
 ↓
Tool result
 ↓
Gemini
 ↓
Natural-language response
 ↓
Frontend
```

The API key remains server-side.

---

# 19. AI Tool Boundary

The AI may use backend functions such as:

```text
planJourney(...)
getJourneyDetails(...)
getFareEstimate(...)
getUserPreferences(...)
getJourneyHistory(...)
getActiveTickets(...)
getActivePasses(...)
```

These functions are controlled by Flask.

The LLM does not receive direct database credentials or direct OTP access.

---

# 20. AI Safety and Accuracy Rule

The AI must treat backend/tool results as authoritative.

If a user asks:

> "What bus should I take from A to B?"

The AI should not guess.

It should:

```text
Understand request
 ↓
Call journey planning function
 ↓
Receive actual route result
 ↓
Explain result
```

If the backend cannot provide the information:

```text
AI reports that the information is unavailable/unverified.
```

---

# 21. Ticket Architecture

Ticket creation begins after a user selects a ticketable journey leg within a journey.

```text
Journey + ticketable leg selected
 ↓
Leg fare confirmed
 ↓
Ticket creation request
 ↓
Backend creates pending ticket/payment relationship for that leg
 ↓
Razorpay order
 ↓
Payment
 ↓
Verification
 ↓
That leg's ticket activated
 ↓
Secure ticket token
 ↓
QR generated
 ↓
Ticket displayed
```

Ticket activation must depend on successful backend-side payment verification.

---

# 22. Pass Architecture

Supported pass types:

```text
DAILY
WEEKLY
MONTHLY
```

Flow:

```text
User selects pass
 ↓
Backend creates pending pass/payment relationship
 ↓
Razorpay Test Mode
 ↓
Payment verification
 ↓
Pass activated
 ↓
Pass token generated
 ↓
QR displayed
```

---

# 23. QR Architecture

The QR code is a representation of a secure ticket/pass token.

Conceptual:

```text
Ticket
 ├── ticket_id
 ├── ticket_token
 └── status
       │
       ▼
    QR image
```

The QR must not contain unnecessary personal information.

Validation:

```text
QR scan/input
 ↓
Validator interface
 ↓
POST /api/validation
 ↓
Backend checks token
 ↓
Check ticket status
 ↓
Check validity period
 ↓
Record validation
 ↓
Return VALID / INVALID / EXPIRED / CANCELLED
```

---

# 24. Payment Architecture

Razorpay Test Mode is external to the Flask application.

The backend controls:

- order creation;
- order association;
- payment verification;
- payment status persistence.

The frontend must not decide that a payment is successful merely because the browser reports success.

Conceptual:

```text
Frontend
   ↓
Flask
   ↓
Create Razorpay order
   ↓
Razorpay
   ↓
Checkout
   ↓
Payment result
   ↓
Flask verification
   ↓
PostgreSQL
   ↓
Ticket/pass activation
```

---

# 25. Admin Architecture

The admin interface uses the same Flask backend.

Examples:

```text
Admin Browser
      ↓
JWT + ADMIN role
      ↓
Flask authorization
      ↓
Admin API
      ↓
PostgreSQL
```

Admin capabilities are limited to IntelliTransit application data.

The admin cannot modify real PMPML/Metro infrastructure.

---

# 26. API Communication Standard

Frontend/backend communication uses:

**HTTP/REST + JSON**

Example:

```http
POST /api/journeys/plan
Content-Type: application/json
Authorization: Bearer <JWT-if-authenticated>
```

Example request:

```json
{
  "origin": {
    "name": "Pune Railway Station",
    "latitude": 18.5285,
    "longitude": 73.8743
  },
  "destination": {
    "name": "Civil Court",
    "latitude": 18.5236,
    "longitude": 73.8500
  },
  "preferences": {
    "route_preference": "FASTEST",
    "avoid_taxi": false,
    "avoid_transfers": false
  }
}
```

The exact API contract will be defined in:

`04_BACKEND_API_SPECIFICATION.md`

---

# 27. Standard API Response Concept

Successful responses should use a predictable structure.

Example:

```json
{
  "success": true,
  "data": {},
  "message": "Request completed successfully"
}
```

Error example:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Origin and destination are required."
  }
}
```

The exact response schemas will be finalized in the API specification document.

---

# 28. Error Boundaries

The architecture must distinguish:

### Client errors

Examples:

- invalid form input;
- missing origin;
- missing destination;
- invalid login.

Return appropriate 4xx responses.

### Authentication errors

Examples:

- missing token;
- expired token;
- invalid token.

Return appropriate authentication responses.

### Authorization errors

Examples:

- USER attempting ADMIN operation.

Return forbidden response.

### OTP errors

Examples:

- OTP unavailable;
- invalid routing request;
- no itinerary found.

Return a meaningful journey-planning error.

### Database errors

Do not expose raw SQL/database details to the user.

Log appropriate technical information server-side.

### Gemini errors

If Gemini fails:

```text
Core journey planning remains available.
```

### Razorpay errors

Payment failure must not activate a ticket/pass.

---

# 29. External Dependency Model

External systems:

```text
OpenTripPlanner
OpenStreetMap / tile provider
Gemini API
Razorpay
```

The application should treat them as external dependencies.

External service credentials must be stored securely through environment configuration.

Example conceptual configuration:

```text
DATABASE_URL
JWT_SECRET
GEMINI_API_KEY
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
OTP_BASE_URL
```

Actual environment variable names can be finalized during implementation.

Secrets must not be committed to GitHub.

---

# 30. Development Environment Architecture

Local development:

```text
Windows Computer
│
├── Flask Backend
├── PostgreSQL
├── OpenTripPlanner 2
├── Frontend
└── Browser
```

External:

```text
Internet
│
├── Gemini API
├── Razorpay Test Mode
└── Map tile/data provider as configured
```

The project must remain usable for local demonstration.

---

# 31. Suggested Project Repository Structure

The final repository can use:

```text
intellitransit/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── middleware/
│   ├── utils/
│   └── tests/
│
├── frontend/
│   ├── index.html
│   ├── pages/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── database/
│   ├── schema.sql
│   ├── seed.sql
│   └── migrations/
│
├── otp/
│   ├── config/
│   └── data/
│
├── docs/
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

The actual directory structure may be refined in the implementation plan.

---

# 32. Data Flow: Journey Planning

Complete data flow:

```text
1. User enters origin/destination
            ↓
2. JavaScript validates basic input
            ↓
3. Request sent to Flask
            ↓
4. Flask validates request
            ↓
5. Journey service receives request
            ↓
6. OTP service formats OTP request
            ↓
7. OpenTripPlanner calculates itineraries
            ↓
8. OTP returns candidate journeys
            ↓
9. Intelligence Layer normalizes/processes results
            ↓
10. Preference/ranking logic is applied
            ↓
11. Fare information is attached/estimated
            ↓
12. Flask creates response
            ↓
13. Browser receives JSON
            ↓
14. JavaScript renders journey cards
            ↓
15. MapLibre renders journey geometry
```

---

# 33. Data Flow: Registered User

```text
Browser
 ↓
JWT
 ↓
Flask authentication middleware
 ↓
User service
 ↓
PostgreSQL
 ↓
User-specific result
 ↓
Browser
```

The backend must always determine which user the JWT represents.

The frontend must not be trusted to provide an arbitrary `user_id` for protected operations.

---

# 34. Data Flow: AI Journey Query

Example:

> "I want the fastest route from Pune Station to Civil Court."

```text
User
 ↓
AI chat UI
 ↓
Flask /api/ai/chat
 ↓
Gemini
 ↓
Intent + entities
 ↓
planJourney(...)
 ↓
Journey Service
 ↓
OTP
 ↓
Intelligence Layer
 ↓
Journey result
 ↓
Gemini
 ↓
Natural-language explanation
 ↓
User
```

The AI is therefore an interface over the actual transportation system, not a fictional transportation database.

---

# 35. Data Flow: Ticket Purchase

```text
User
 ↓
Select journey
 ↓
Select ticket
 ↓
Flask ticket endpoint
 ↓
Create pending ticket
 ↓
Create Razorpay Test Mode order
 ↓
Frontend opens checkout
 ↓
Payment
 ↓
Backend verification
 ↓
Payment SUCCESS
 ↓
Ticket ACTIVE
 ↓
QR token
 ↓
QR displayed
```

If payment fails:

```text
Payment FAILED
 ↓
Ticket remains inactive/pending/failed according to implementation state
 ↓
No active ticket is issued
```

---

# 36. Data Flow: QR Validation

```text
Authorized Validator
 ↓
Scan/read QR
 ↓
Extract token
 ↓
Flask validation API
 ↓
Find ticket
 ↓
Check token
 ↓
Check status
 ↓
Check validity period
 ↓
Record validation attempt
 ↓
Return validation result
```

Possible result:

```text
VALID
INVALID
EXPIRED
CANCELLED
```

---

# 37. Architecture Constraints

The following are hard constraints unless explicitly changed:

1. Frontend remains HTML/CSS/JavaScript.
2. Backend remains Python/Flask.
3. PostgreSQL remains the application database.
4. OTP remains the routing engine.
5. AI remains an assistant, not the routing engine.
6. MapLibre remains the map renderer.
7. OpenStreetMap remains the geographic-data source.
8. Razorpay remains the payment gateway.
9. Test Mode remains the payment environment.
10. Pune remains the geographic scope.
11. Native Windows remains the primary development environment.
12. Docker is not a core dependency.
13. No native mobile application.
14. No unnecessary microservices.

---

# 38. Architecture Decision Summary

```text
                   INTELLITRANSIT
                         │
             Responsive Web Application
                         │
              ┌──────────┴──────────┐
              │                     │
       HTML + CSS + JS         Python + Flask
              │                     │
              │                 REST API
              │                     │
              │         ┌───────────┼───────────┐
              │         │           │           │
              │         ▼           ▼           ▼
              │    PostgreSQL     OTP 2      External APIs
              │                      │        ├── Gemini
              │                      │        └── Razorpay
              │                   OSM/GTFS
              │
              ▼
        MapLibre GL JS
```

The architecture is intentionally simple:

> **One frontend, one Flask backend, one PostgreSQL database, one routing engine, and a small number of external services.**

This is the baseline architecture to be implemented.

---

# 39. Relationship to Other Development Documents

This document establishes architecture only.

Detailed decisions belong in later documents:

- `03_DATABASE_DESIGN.md` → database schema and relationships;
- `04_BACKEND_API_SPECIFICATION.md` → exact Flask API contracts;
- `05_ROUTING_AND_INTELLIGENCE.md` → OTP and route-ranking implementation;
- `06_FRONTEND_UI_SPECIFICATION.md` → pages and browser implementation;
- `07_AI_TICKETING_PAYMENT_SPECIFICATION.md` → AI, QR, ticketing and payments;
- `08_SECURITY_TESTING_AND_ERROR_HANDLING.md` → security and testing;
- `09_IMPLEMENTATION_PLAN.md` → actual implementation sequence.

Do not duplicate detailed specifications unnecessarily.

---

**END OF DOCUMENT**
