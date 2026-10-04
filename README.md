# IntelliTransit — Intelligent Multimodal Transportation & Journey Planning Platform

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Tests](https://img.shields.io/badge/tests-50%20passed-success)]()
[![Python](https://img.shields.io/badge/python-3.10%2B%20%7C%203.11-blue)]()
[![PostgreSQL](https://img.shields.io/badge/postgresql-14%2B-blue)]()
[![OpenTripPlanner](https://img.shields.io/badge/OpenTripPlanner-2.x-orange)]()
[![Demo AI](https://img.shields.io/badge/AI%20Mode-Demo%20%2B%20Tools-blueviolet)]()

> **IntelliTransit** is an enterprise-grade multimodal journey planning platform and transit intelligence system built specifically for the **Pune Metropolitan Region (PMRDA / PMC / PCMC)**. It seamlessly integrates **PMPML Buses**, **Pune Metro (Line 1 Purple & Line 2 Aqua)**, and **Taxis / Auto-Rickshaws**, providing unified routing, leg-based ticketing, periodic passes, simulated payment processing, QR turnstile validation, and conversational transit AI assistance.

---

## 1. Academic Context

* **Degree:** Third Year Bachelor of Science in Computer Science (TYBSc CS)
* **Project Type:** Final Year Capstone Project
* **Geographic Scope:** Pune Metropolitan Region Development Authority (PMRDA), Maharashtra, India
* **Core Problem Solved:** Pune commuters navigate fragmented public transit options across PMPML municipal buses, MahaMetro rail lines, and intermediate public transport (auto-rickshaws). IntelliTransit unifies transit discovery, timetable scheduling, leg-based ticketing, and validation into a resilient, cohesive platform.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph Frontend["Frontend MPA Layer (Vanilla HTML5 / CSS3 / ES6+ JS)"]
        UI_Home["Landing (index.html)"]
        UI_Planner["Split-Screen Planner (planner.html + MapLibre GL)"]
        UI_Tickets["My Tickets (tickets.html)"]
        UI_Passes["Transit Passes (passes.html)"]
        UI_AI["AI Assistant (ai-assistant.html)"]
        UI_Val["Conductor Validator (validator.html)"]
        UI_Admin["Admin Dashboard (admin.html)"]
    end

    subgraph Backend["Backend Application (Python 3.10+ / Flask App Factory)"]
        MW["Middleware (CORS, Sliding Rate Limiter, CSP/Security Headers)"]
        Auth_SVC["Auth & RBAC (PyJWT + bcrypt)"]
        Journey_SVC["Journey Orchestrator & Intelligence Layer"]
        Fare_SVC["Dynamic Fare Engine (Bus/Metro/Taxi)"]
        Tkt_SVC["Leg-Based Ticketing & Periodic Passes"]
        Pay_SVC["Simulated Payment System (Zero External Dependency)"]
        Val_SVC["QR Generation & Turnstile Validator (qrcode/Pillow)"]
        AI_SVC["Demo AI Mode & Heuristic Transit Engine (6 Tools)"]
        Admin_SVC["Admin Metrics & Dynamic Fare Matrix"]
    end

    subgraph Routing["Routing & Map Engine"]
        OTP["OpenTripPlanner 2 (Range RAPTOR + Generalized Cost A*)"]
        Fallback_Graph["Internal Offline Pune Transit Graph (Automatic Fallback)"]
        Tiles["OpenStreetMap Vector/Raster Tiles (MapLibre GL JS)"]
    end

    subgraph Storage["Persistent Storage"]
        DB[(PostgreSQL 14+ / 11 Authoritative Tables / ThreadedConnectionPool)]
    end

    Frontend -->|REST API / Bearer JWT| Backend
    Journey_SVC -->|HTTP REST| OTP
    Journey_SVC -.->|Fallback on Timeout| Fallback_Graph
    Backend -->|Parameterized SQL / psycopg2| DB
    UI_Planner -->|Tile Rendering| Tiles
```

---

## 3. Architecture Description

IntelliTransit is designed as a **modular monolithic Multi-Page Application (MPA)**:
1. **Frontend Presentation Client:** Fast, lightweight vanilla HTML5, modern CSS3 with custom properties, and native ES6 JavaScript modules (`import`/`export`). Uses MapLibre GL JS for GPU-accelerated mapping with zero npm build step or runtime framework bloat.
2. **Backend Application Layer:** Python 3.10+ with Flask's Application Factory pattern (`create_app`), modular blueprints, schema validation, and middleware security wrappers.
3. **Multimodal Routing Engine:** OpenTripPlanner 2 using Range RAPTOR and Generalized Cost A*, backed by an internal offline Pune transit graph for automatic fallback resilience.
4. **Data Persistence Layer:** PostgreSQL 14+ with 11 normalized relational tables, strict check constraints, UUID primary keys, and thread-safe connection pooling via `psycopg2.pool.ThreadedConnectionPool`.

---

## 4. Key Features

- **Multimodal Routing:** Combines walking, PMPML buses, Pune Metro, and auto-rickshaws into Pareto-optimal itineraries.
- **5 Optimization Profiles:** `BALANCED`, `FASTEST`, `CHEAPEST`, `MIN_TRANSFERS`, and `LEAST_WALKING`.
- **Interactive Mapping:** MapLibre GL JS canvas with modal polyline coloration, landmark markers, and bounds fitting.
- **Leg-Based Ticketing:** Strict transit rules permit ticket bookings on transit legs (`BUS`, `METRO`) while correctly disallowing pedestrian walk legs.
- **Periodic Passes:** Commuters can purchase `DAILY`, `WEEKLY`, and `MONTHLY` passes.
- **Internal Simulated Payments:** Complete transaction lifecycle without external sandbox dependencies or failure points.
- **Turnstile QR Validation:** Generates scannable QR tokens; validates and prevents double-scanning fraud.
- **Transit AI Assistant:** Operates in Demo AI Mode using 6 backend-authoritative transit intelligence tools.
- **Administrator Portal:** Real-time KPI metrics, active tickets, simulated revenues, and dynamic fare configuration.

---

## 5. Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | Vanilla HTML5, CSS3 (Design Tokens), Modern ES6+ JavaScript, MapLibre GL JS 3.x |
| **Backend** | Python 3.10+ / 3.11, Flask 3.0+ (App Factory), PyJWT 2.8+, bcrypt 4.1+, qrcode 7.4+, Pillow 10.x |
| **Database** | PostgreSQL 14+, `psycopg2-binary` (ThreadedConnectionPool), `pgcrypto` |
| **Routing & GIS** | OpenTripPlanner 2.x (Range RAPTOR), OpenStreetMap Pune Extract, PMPML/MahaMetro GTFS |
| **AI Layer** | Demo AI Mode with 6 authoritative backend tools & offline transit heuristics |

---

## 6. 13-Package Implementation Structure

| Package | Name | Description |
| :--- | :--- | :--- |
| **PKG-01** | `Environment & Config` | Configuration loaders, 12-factor `.env`, lean requirements. |
| **PKG-02** | `Database & Schema` | 11 relational tables, constraints, connection pooling, seed records. |
| **PKG-03** | `Flask Foundation` | App factory, error handlers, rate limiter, OWASP security headers. |
| **PKG-04** | `Auth & User Mgmt` | PyJWT auth, bcrypt hashing, commuter preferences, saved bookmarks (max 20). |
| **PKG-05** | `OTP Integration & Geo` | OTP 2 client, Pune bounding box checks, Haversine formula, landmark geocoder. |
| **PKG-06** | `Journey Planning & Engine` | Multimodal routing, fare calculator, 5 ranking profiles, natural language explanations. |
| **PKG-07** | `Frontend Foundation` | Modular CSS tokens, responsive layout, MapLibre GL JS integration. |
| **PKG-08** | `Planner & History UI` | Split-screen journey planner, route preview polylines, guest planning support. |
| **PKG-09** | `Ticketing & Pass Engine` | Leg-based ticketing, periodic passes, finite state machine lifecycle. |
| **PKG-10** | `Simulated Payment System` | Internal simulated payments, order creation, instant atomic confirmation. |
| **PKG-11** | `QR & Validation Engine` | Scannable QR generation (`qrcode`/`Pillow`), conductor validator, anti-fraud defense. |
| **PKG-12** | `AI Assistant Companion` | Conversational companion with dynamic model badge, 6 backend tools, heuristic fallback. |
| **PKG-13** | `Admin & Hardening` | Admin dashboard, live KPI metrics, dynamic fare matrix editor, 50-test suite. |

---

## 7. Prerequisites

Before running IntelliTransit, ensure the following are installed:
1. **Python:** 3.10 or 3.11 (with `pip` and `venv`)
2. **PostgreSQL:** Version 14 or higher (running locally on port 5432)
3. **Java:** Version 17+ or 21+ (Optional, only required if running OpenTripPlanner 2 locally)
4. **Web Browser:** Google Chrome, Firefox, or Edge with WebGL enabled

---

## 8. Quick Start Guide

### Step 1: Clone and Navigate
```powershell
git clone <repository_url>
cd IntelliTransit
```

### Step 2: Virtual Environment Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
```

### Step 3: Environment Configuration
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```

### Step 4: Database Setup
Create the databases in PostgreSQL and run schema/seed scripts:
```powershell
psql -U postgres -c "CREATE DATABASE intellitransit;"
psql -U postgres -c "CREATE DATABASE intellitransit_test;"
psql -U postgres -d intellitransit -f database/schema.sql
psql -U postgres -d intellitransit -f database/seed.sql
```

### Step 5: Start the Application
```powershell
.\start_backend.bat
# Or run:
python backend/run.py
```
Access the application at `http://localhost:5000`.

---

## 9. Database Setup & Architecture

IntelliTransit uses 11 normalized relational tables:
- `users`: Commuters and administrators with strict roles (`USER`, `ADMIN`).
- `user_preferences`: Modal preferences and walking thresholds.
- `saved_locations`: Commuter bookmarks capped at 20 per account.
- `transport_services`: Service registry for PMPML Buses, Metro lines, and Auto-Rickshaws.
- `fare_configurations`: Base fares, per-km rates, and minimum fares.
- `journeys`: Saved journey planning requests and summaries.
- `journey_legs`: Granular route legs with `is_ticketable` enforcement.
- `payments`: Simulated payment transaction records with `SIM-PAY-...` references.
- `tickets`: Scannable leg-based tickets with finite state machine lifecycle.
- `passes`: Periodic multi-ride passes (`DAILY`, `WEEKLY`, `MONTHLY`).
- `ticket_validations`: Immutable audit inspection log for conductor turnstiles.

---

## 10. OpenTripPlanner (OTP) Setup

IntelliTransit is pre-configured to communicate with OpenTripPlanner 2.
1. Place OTP 2 JAR, OSM Pune extract (`pune.pbf`), and GTFS zip files into the `otp/` folder.
2. Build the router graph:
   ```powershell
   java -Xmx4G -jar otp/otp-shaded.jar --build --save otp/
   ```
3. Run the OTP server:
   ```powershell
   .\otp\start_otp.bat
   ```
> **Note:** If OTP is not running, IntelliTransit automatically activates its **Internal Offline Pune Transit Graph**, guaranteeing seamless demonstration and zero downtime.

---

## 11. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `FLASK_ENV` | `development` | Flask runtime environment (`development` / `testing` / `production`). |
| `SECRET_KEY` | `dev-secret-key-32-chars-minimum-length!` | Flask secret session key. |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/intellitransit` | Primary PostgreSQL connection string. |
| `TEST_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/intellitransit_test` | Isolated automated test database. |
| `JWT_SECRET_KEY` | `jwt-secret-key-32-chars-minimum-length!` | HS256 JWT signing secret key. |
| `OTP_BASE_URL` | `http://localhost:8080/otp` | OpenTripPlanner 2 API endpoint. |
| `GEMINI_API_KEY` | `""` (Empty for Demo AI Mode) | Optional Google Gemini API key. |

---

## 12. Running the Application

To start the backend with all static frontend routes active:
```powershell
.\start_backend.bat
```
The server will bind to `http://localhost:5000`. Static files are served directly by Flask.

---

## 13. Running Automated Tests

Run the complete 50-test verification suite using Pytest:
```powershell
.\venv\Scripts\python -m pytest backend/tests -v --durations=0
```
**Expected Output:**
```
======================= 50 passed, 1 warning in 49.38s ========================
```
*Coverage:* 100% pass rate across authentication, RBAC, routing, ticketing, simulated payments, QR validation, AI tools, and admin features.

---

## 14. Demonstration Workflow

For examiners and reviewers, follow the 5–8 minute workflow:
1. **Journey Planning:** Go to `http://localhost:5000/planner.html`. Plan from *Pune Railway Station* to *Kothrud Depot*.
2. **Review Itineraries:** Inspect route cards and MapLibre polyline paths.
3. **Book Ticket:** Click "Book Ticket" on the Metro leg.
4. **Simulate Payment:** Review the simulated payment modal and click "Confirm Simulated Payment".
5. **View Active Ticket:** In `http://localhost:5000/tickets.html`, view the generated QR code.
6. **Validate QR:** In `http://localhost:5000/validator.html`, validate the token. First scan shows **VALID**; second scan shows **ALREADY USED**.
7. **Ask AI:** In `http://localhost:5000/ai-assistant.html`, query transit advice.
8. **Admin Dashboard:** In `http://localhost:5000/admin.html`, review platform KPIs and edit fares.

---

## 15. Default Demonstration Accounts

| Role | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@intellitransit.com` | `AdminPassword123!` | Full Admin Dashboard, Metrics, Fare Matrix |
| **Commuter 1** | `rahul.sharma@example.com` | `UserPassword123!` | Journey Planning, Ticketing, Passes, AI |
| **Commuter 2** | `priya.patil@example.com` | `UserPassword123!` | Journey Planning, Ticketing, Passes, AI |

---

## 16. Key Application URLs

- **Landing Page:** `http://localhost:5000/` or `/index.html`
- **Journey Planner:** `http://localhost:5000/planner.html`
- **My Tickets:** `http://localhost:5000/tickets.html`
- **Transit Passes:** `http://localhost:5000/passes.html`
- **Conductor Validator:** `http://localhost:5000/validator.html`
- **AI Transit Assistant:** `http://localhost:5000/ai-assistant.html`
- **Admin Dashboard:** `http://localhost:5000/admin.html`
- **System Health Check:** `http://localhost:5000/api/health`

---

## 17. Simulated Payment System

To provide an autonomous, reliable demonstration without external payment gateway dependencies, IntelliTransit implements an **Internal Simulated Payment System**:
- Generates unique transaction references formatted as `SIM-PAY-TKT-...` or `SIM-PAY-PASS-...`.
- Renders an in-app confirmation modal with clear pricing and payment type details.
- Transitions ticket status atomically from `PENDING` to `ACTIVE`.
- Idempotently blocks duplicate payment submissions (`ALREADY_PAID`).
- Restricts payment confirmations to the authenticated owner of the booking.

---

## 18. AI Transit Assistant (Demo AI Mode)

The AI Assistant operates with full backend integration:
- **Badge:** Displays *"Demo AI Mode • Backend-Authoritative Transit Intelligence"*.
- **6 Integrated Tools:** `find_transit_routes`, `get_fare_estimate`, `get_service_status`, `get_station_information`, `explain_route_options`, and `recommend_transit_pass`.
- **Heuristic Fallback:** When no external Gemini API key is provided, the backend heuristic engine parses queries and executes tools to return accurate, contextual answers without latency.

---

## 19. Conductor & Turnstile QR Validator

- **Turnstile Mode:** Enter ticket tokens or scan QR codes at `validator.html`.
- **Anti-Fraud Single Use:** Validates tickets and transitions them from `ACTIVE` to `USED`. Subsequent attempts return an instant **ALREADY USED** rejection.
- **Audit Log:** Every inspection is recorded in the `ticket_validations` table with timestamps and validator identity.

---

## 20. Administrator Control Center

- **Live KPIs:** Total registered users, total journeys planned, active tickets, and total simulated revenue.
- **Dynamic Fare Matrix:** Edit base fares and per-km rates for PMPML Buses, Pune Metro, and Taxis with instant recalculation.
- **Role Protection:** Non-admin commuters attempting to access `/admin.html` or `/api/admin/*` receive an HTTP 403 Forbidden response.

---

## 21. Security Hardening

- **Stateless JWT:** HS256 signing with 24-hour expiration windows.
- **Bcrypt Passwords:** Work factor 12 with 128-bit cryptographic salts.
- **Strict RBAC:** Segregation between `USER` and `ADMIN` roles.
- **SQL Injection Defense:** 100% parameterized queries via psycopg2 (`%s`).
- **OWASP Security Headers:** Content-Security-Policy, HSTS, X-Frame-Options, X-Content-Type-Options.
- **Rate Limiting:** In-memory sliding window limiter preventing brute-force abuse.

---

## 22. Known Academic Limitations & Design Decisions

1. **Simulated Payments:** Intentionally replaces external payment gateways (e.g. Razorpay) to guarantee deterministic evaluation.
2. **Demo AI Mode:** Uses backend-authoritative transit heuristics when external LLM API quotas are absent.
3. **Offline Pune Graph:** Provides reliable fallback routing when an external OpenTripPlanner instance is offline.
4. **Software QR Scanning:** Uses browser-based camera inputs and manual token entry for turnstile simulation.

---

## 23. API Summary Table

| Method | Endpoint | Auth | Purpose |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/health` | None | Service, DB, and OTP health status |
| `POST` | `/api/auth/register` | None | Register new commuter account |
| `POST` | `/api/auth/login` | None | Authenticate and obtain JWT token |
| `GET` | `/api/auth/me` | User | Get current commuter session profile |
| `POST` | `/api/journeys/plan` | Optional | Plan multimodal journey (Guest or User) |
| `POST` | `/api/tickets/book` | User | Book ticket for transit leg |
| `GET` | `/api/tickets/<id>/qr` | User | Stream scannable QR code image |
| `POST` | `/api/passes/create` | User | Purchase periodic transit pass |
| `POST` | `/api/payments/create-order`| User | Create simulated payment order |
| `POST` | `/api/payments/simulate-confirm`| User | Confirm simulated payment atomically |
| `POST` | `/api/validation/scan` | Conductor | Validate and consume QR ticket |
| `POST` | `/api/ai/chat` | Optional | Transit companion conversational query |
| `GET` | `/api/admin/metrics` | Admin | Aggregate system KPI metrics |
| `PUT` | `/api/admin/fares/<id>` | Admin | Update dynamic fare matrix |

---

## 24. Database Schema Summary

| Table | Primary Key | Description |
| :--- | :--- | :--- |
| `users` | `user_id` (UUID) | Commuter and admin identities (`role IN ('USER', 'ADMIN')`). |
| `user_preferences` | `preference_id` (UUID) | Personalized mode biases and walking limits. |
| `saved_locations` | `location_id` (UUID) | Bookmarked commuter stops (Home, Work; max 20). |
| `transport_services` | `service_id` (UUID) | PMPML Bus, Metro Line 1 & 2, and Taxi services. |
| `fare_configurations`| `fare_id` (UUID) | Base fares, per-km rates, and minimum fares. |
| `journeys` | `journey_id` (UUID) | Calculated multimodal route itineraries. |
| `journey_legs` | `leg_id` (UUID) | Individual journey segments with `is_ticketable` flag. |
| `payments` | `payment_id` (UUID) | Simulated payment transaction ledger. |
| `tickets` | `ticket_id` (UUID) | Leg-based transit tickets with finite state machine. |
| `passes` | `pass_id` (UUID) | Periodic multi-ride transit passes (`DAILY`, `WEEKLY`, `MONTHLY`). |
| `ticket_validations` | `validation_id` (UUID) | Turnstile and conductor inspection audit history. |

---

## 25. Troubleshooting Guide

- **Database Connection Error:** Verify PostgreSQL is running on port 5432 (`pg_isready`) and the database `intellitransit` exists.
- **Port 5000 Already in Use:** Stop conflicting processes using `netstat -ano | findstr :5000` or specify an alternate port.
- **Map Not Loading:** Ensure your browser has WebGL hardware acceleration enabled and internet access for tile retrieval.
- **Offline Routing Message:** Indicates OpenTripPlanner is not running on port 8080. The application automatically and gracefully uses its built-in Pune offline fallback graph.

---

## 26. Complete Documentation Index

For detailed documentation, refer to the files in the `docs/` directory:
- [Demo Guide](docs/DEMO_GUIDE.md) — Step-by-step 5–8 minute live demonstration script.
- [Viva Technical Summary](docs/VIVA_TECHNICAL_SUMMARY.md) — 36 viva voce technical questions and answers.
- [Feature Matrix](docs/FEATURE_MATRIX.md) — Complete feature and package verification matrix.
- [Database Specification](docs/DATABASE.md) — PostgreSQL ERD, 11 table specifications, and connection pooling details.
- [API Reference](docs/API_REFERENCE.md) — Complete REST API schemas, endpoints, and curl examples.
- [Test Report](docs/TEST_REPORT.md) — Pytest execution report with durations and coverage breakdown.
- [Browser Acceptance Checklist](docs/BROWSER_ACCEPTANCE_CHECKLIST.md) — 12 browser acceptance scenarios.
- [Screenshot Plan](docs/SCREENSHOT_PLAN.md) — 18-point screenshot capture plan for project presentation.

---

## 27. License & Academic Declaration

**Academic Declaration:**  
This project is submitted in partial fulfillment of the requirements for the degree of **Bachelor of Science in Computer Science (TYBSc CS)**. The architecture, software design, implementation, and automated test suite were developed specifically for transit evaluation in the Pune Metropolitan Region.

**License:**  
Released under the MIT License. Copyright © 2026 IntelliTransit Contributors.
