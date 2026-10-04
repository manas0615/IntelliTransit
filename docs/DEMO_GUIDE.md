# IntelliTransit — Live Demonstration Script & Evaluator Guide

**Project:** IntelliTransit (PMRDA Multimodal Journey Planning Platform)  
**Target Duration:** 5 to 8 Minutes  
**Audience:** Project Evaluators, University Examiners, Technical Reviewers  
**Prerequisites:** Backend running on `http://localhost:5000` (`.\venv\Scripts\python backend/run.py` or `start_backend.bat`).

---

## ⏱️ Demonstration Timeline Summary

```
00:00 - 01:00  | Part 1: Introduction & Architecture Overview
01:00 - 02:30  | Part 2: Commuter Journey Planning (MapLibre + OTP Routing)
02:30 - 04:00  | Part 3: Leg-Based Ticketing & Simulated Payment
04:00 - 05:00  | Part 4: Conductor / Turnstile QR Validation
05:00 - 06:00  | Part 5: Conversational Transit AI Companion
06:00 - 07:00  | Part 6: Administrator Control Center & Fare Matrix
07:00 - 07:30  | Part 7: Technical Summary & Conclusion
```

---

## 🎬 Step-by-Step Demonstration Script

### Part 1: Introduction & Architecture Overview (1 Minute)
* **Action:** Open browser at `http://localhost:5000/`.
* **Speaking Points:**
  > "Good morning, respected examiners. Today we present IntelliTransit, an intelligent multimodal journey planning platform specifically built for the Pune Metropolitan Region.
  >
  > Commuters in Pune face fragmented transit networks between PMPML city buses, the new Pune Metro lines, and auto-rickshaws. IntelliTransit solves this by unifying route planning, cost estimation, leg-based ticketing, and AI assistance into a single, cohesive architecture.
  >
  > Architecturally, it utilizes OpenTripPlanner 2 with Generalized Cost A* and Range RAPTOR routing, backed by PostgreSQL, a Python Flask API factory, and a fast, dependency-free vanilla JavaScript and MapLibre GL frontend."

---

### Part 2: Commuter Journey Planning (1.5 Minutes)
* **Action:**
  1. Navigate to **Journey Planner** (`http://localhost:5000/planner.html`).
  2. In Origin, select or type: `Pune Railway Station`.
  3. In Destination, select or type: `Kothrud Depot`.
  4. Select Route Preference: `Balanced`.
  5. Click **"Find Routes"**.
* **Expected UI Behavior:**
  - Origin (green) and Destination (red) markers appear on the MapLibre map.
  - The map auto-fits bounds.
  - Colored polyline routes render smoothly on the map canvas.
  - The left panel displays route itineraries with mode breakdown badges (`WALK`, `METRO`, `BUS`).
  - An intelligent route explanation summary is displayed.
  - Individual transit legs display a **"Book Ticket"** button, while walking legs do not.
* **Speaking Points:**
  > "Notice how our journey orchestrator computes the optimal multimodal path. It connects pedestrian access, Metro Line 2, and connecting bus service with full fare transparency.
  >
  > Our intelligence layer ranks itineraries based on commuter preferences—offering Balanced, Fastest, and Cheapest options. Crucially, the platform enforces our academic transit rule: only mass-transit legs are ticketable, preventing erroneous bookings on pedestrian walk legs."

---

### Part 3: Leg-Based Ticketing & Simulated Payment (1.5 Minutes)
* **Action:**
  1. Click **"Book Ticket"** on the Metro leg (`Pune Station Metro → Garware College`).
  2. If prompted, log in with test commuter credentials:
     - **Email:** `rahul.sharma@example.com`
     - **Password:** `UserPassword123!`
  3. The system creates a ticket in `PENDING` state and displays the Simulated Payment Modal.
  4. Review the modal details: Amount ₹20.00, Payment Type: `TICKET`, Method: `SIMULATED`.
  5. Click **"Confirm Simulated Payment"**.
* **Expected UI Behavior:**
  - Instant modal confirmation with checkmark badge.
  - Automatic redirect to **My Tickets** (`http://localhost:5000/tickets.html`).
  - The newly booked ticket appears with status badge **ACTIVE**.
  - A scannable, high-contrast QR code is rendered alongside validity timestamps.
* **Speaking Points:**
  > "For this demonstration build, we implemented an internal Simulated Payment System. This enables full end-to-end evaluation of the transit ticketing lifecycle without relying on external third-party payment gateway sandboxes or test credit cards.
  >
  > Once payment is simulated, the state machine atomically transitions the ticket from PENDING to ACTIVE, generating a cryptographically secure token and scannable QR code."

---

### Part 4: Conductor / Turnstile QR Validation (1 Minute)
* **Action:**
  1. From the ticket card, copy the `Ticket Token` (e.g., `TKT-A89F...`) or note its QR code.
  2. Open **Conductor Validator** in a new tab: `http://localhost:5000/validator.html`.
  3. Paste the token into the manual entry box (or present the QR).
  4. Click **"Validate Ticket"**.
  5. *Immediate re-test:* Click **"Validate Ticket"** a second time with the same token.
* **Expected UI Behavior:**
  - **First Scan:** Displays a large green **VALID** banner with passenger origin, destination, and boarding authorization. Ticket status transitions to `USED`.
  - **Second Scan:** Displays a red **INVALID / ALREADY USED** rejection banner with timestamp of prior inspection.
* **Speaking Points:**
  > "Here we simulate the conductor or automated metro turnstile validator. On the first scan, the ticket is verified and consumed in the database.
  >
  > If a commuter attempts to use the same ticket twice, our turnstile audit engine instantly flags it as ALREADY USED, preventing transit fraud."

---

### Part 5: Conversational Transit AI Companion (1 Minute)
* **Action:**
  1. Open **AI Assistant** (`http://localhost:5000/ai-assistant.html`).
  2. Point out the model indicator badge in the header:
     - *"Demo AI Mode • Backend-Authoritative Transit Intelligence"*
  3. Type in prompt:
     `"What is the best way to get from Swargate to Pune Airport?"`
  4. Press Enter.
* **Expected UI Behavior:**
  - AI companion executes backend tools and provides a direct, contextual transit recommendation including bus route numbers, metro transfers, and approximate fare.
* **Speaking Points:**
  > "IntelliTransit features a specialized Transit AI Companion. In this demonstration build, it operates in Demo AI Mode using backend-authoritative transit intelligence tools.
  >
  > It directly queries our routing and fare engines, providing commuters with accurate answers regarding routes, schedules, and interchange rules without hallucinating nonexistent routes."

---

### Part 6: Administrator Control Center (1 Minute)
* **Action:**
  1. Log out or open an Incognito window / use Admin session at `http://localhost:5000/admin.html`.
  2. Log in as Administrator:
     - **Email:** `admin@intellitransit.com`
     - **Password:** `AdminPassword123!`
  3. Review the live metrics: Total Users, Journeys Planned, Active Tickets, Simulated Revenue.
  4. Scroll to **Fare Matrix Management**.
  5. Select **Pune Metro** and adjust Base Fare from ₹10.00 to ₹12.00, then click **Save**.
* **Expected UI Behavior:**
  - Real-time aggregation of commuters and revenue.
  - Successful save alert on dynamic fare update.
  - Strict RBAC: Commuters attempting to open `/admin.html` are blocked with HTTP 403 Forbidden.
* **Speaking Points:**
  > "The Administrator Portal gives transit authorities full oversight of the network. Administrators can monitor real-time ridership, inspect simulated revenues, and dynamically adjust fare configurations across PMPML buses and Pune Metro lines."

---

### Part 7: Conclusion & Architecture Recap (30 Seconds)
* **Speaking Points:**
  > "To conclude: IntelliTransit delivers a production-grade, full-stack transit management platform with 50 passing automated tests, 11 PostgreSQL tables, OpenTripPlanner integration, and a complete ticketing and validation lifecycle.
  >
  > We are now ready to take any technical questions from the panel."

---

## 🛡️ Live Demonstration Contingencies & Fallback Procedures

| Scenario | Occurrence Probability | Immediate Fallback Action |
| :--- | :---: | :--- |
| **OpenTripPlanner offline / slow** | Low | The backend automatically activates the internal offline Pune transit graph (`routing_source: "OFFLINE_FALLBACK"`). The demo continues seamlessly. |
| **Token expired during test** | Very Low | Generate a fresh ticket or pass directly from the Journey Planner in under 10 seconds. |
| **Accidental browser cache reload** | Low | Hard refresh (`Ctrl + F5`); all data is persisted in PostgreSQL. |
| **Network disconnection** | None | The platform runs entirely locally on `localhost:5000` with local PostgreSQL and local vector map styling. |
