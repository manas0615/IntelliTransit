# IntelliTransit — Project Definition & Frozen Decisions

**Document:** `01_PROJECT_DEFINITION.md`  
**Project:** IntelliTransit  
**Formal Title:** IntelliTransit: An Intelligent Multimodal Transportation and Journey Planning Platform  
**Academic Context:** T. Y. B. Sc. Computer Science, SPPU  
**Geographic Scope:** Pune, Maharashtra  
**Status:** FROZEN BASELINE

---

## 1. Project Overview

IntelliTransit is a **Pune-focused responsive web application** for intelligent multimodal transportation and journey planning.

The core idea is:

> A user tells IntelliTransit where they are and where they want to go. IntelliTransit determines suitable multimodal journey options and presents them clearly.

A journey may combine:

```text
Point A → Walking → Bus → Transfer → Metro → Walking → Point D
```

or:

```text
Point A → Taxi → Point B → Metro → Point C → Bus → Point D
```

The system combines journey planning, map visualization, personalization, conversational AI, digital ticketing, QR validation, and payment demonstration into one academic web application.

---

## 2. Core Problem

Transportation information is distributed across different services and sources. A commuter may need to determine:

- which bus to take;
- whether metro can be combined with the bus;
- where to transfer;
- how much walking is required;
- how long the journey will take;
- the estimated fare;
- which alternative is more suitable for a preference.

IntelliTransit addresses this fragmentation through one journey-planning interface.

---

## 3. Project Goals

1. Provide multimodal journey planning within Pune.
2. Support bus, metro, taxi, and walking/transfers.
3. Provide alternative journey options.
4. Compare duration, estimated fare, walking distance, and transfers.
5. Display journeys on an interactive map.
6. Provide step-by-step journey guidance.
7. Support saved locations and transportation preferences.
8. Maintain registered-user journey history.
9. Provide a Gemini 2.5 Flash conversational transportation assistant.
10. Provide single-journey tickets.
11. Provide daily, weekly, and monthly passes.
12. Generate QR-based ticket/pass identifiers.
13. Provide authorized online QR validation.
14. Demonstrate payments through Razorpay Test Mode.
15. Provide basic administration of application-level transport metadata and fare configuration.

---

## 4. Explicit Non-Goals

Do **not** implement or claim the following as part of the current project:

- nationwide transportation coverage;
- guaranteed real-time GPS tracking of Pune buses;
- direct government transportation-system integration;
- direct Pune Metro operational-system integration;
- actual operator ticket-validator integration;
- offline QR validation;
- crowd prediction;
- AI traffic prediction;
- dynamic transportation pricing;
- autonomous transportation management;
- production-scale transportation infrastructure;
- replacement of PMPML, Pune Metro, taxi operators, or government systems;
- native Android application;
- native iOS application;
- React/Vite frontend;
- Node.js/Express backend;
- Docker as a core dependency.

---

## 5. Geographic and Mode Scope

**Geography:** Pune only.

**Modes:**
- Bus
- Metro
- Taxi
- Walking/transfers

Taxi information may use configured or estimated values where live operator data is unavailable. Such information must never be presented as guaranteed live data.

---

## 6. Platform

IntelliTransit is a **responsive web application** supporting:

- desktop browsers;
- laptop browsers;
- tablet browsers;
- mobile browsers.

There is no separate native mobile application.

---

# 7. Frozen Technology Stack

## 7.1 Frontend

Use only:

- HTML5
- CSS3
- JavaScript ES6+

Do not introduce React, Vue, Angular, Svelte, JSX, Vite, or another frontend framework unless the architecture is explicitly changed later.

The frontend should use normal JavaScript modules and clear separation of HTML, CSS, and JavaScript.

## 7.2 Backend

Use:

- Python
- Flask

Flask provides the REST API and application orchestration.

Do not introduce Node.js or Express.js.

## 7.3 Database

Use **PostgreSQL**.

PostgreSQL stores IntelliTransit application/business data. It must not become a replacement for the transportation network maintained by OpenTripPlanner/GTFS/OSM.

## 7.4 Authentication

Use:

- JWT
- bcrypt
- role-based authorization

Roles:

```text
USER
ADMIN
```

Guests can plan journeys without an account.

## 7.5 Routing

Use **OpenTripPlanner 2** as the multimodal routing engine.

Do not build a complete multimodal routing engine from scratch.

OTP is responsible for generating transportation itineraries from the available transportation/network data.

## 7.6 IntelliTransit Intelligence Layer

The custom application layer handles:

- route ranking;
- preference handling;
- fare aggregation/estimation;
- walking-distance comparison;
- transfer-aware presentation;
- personalization;
- journey explanation;
- application-level route selection.

It does **not** replace OTP's routing engine.

## 7.7 Geographic Data and Maps

Use:

- **OpenStreetMap** for geographic/street data;
- **MapLibre GL JS** for browser-side map rendering.

MapLibre is responsible for:

- map rendering;
- zoom/pan;
- markers;
- route lines;
- stops/stations;
- map layers;
- journey visualization.

MapLibre does not calculate the journey.

Responsibility:

```text
OpenStreetMap → geographic data
OpenTripPlanner → journey calculation
MapLibre GL JS → map visualization
```

## 7.8 Transit Data

Preferred sources:

1. Reliable official/public transportation data.
2. GTFS data where available.
3. Published schedules and fares.
4. OpenStreetMap geographic data.
5. Curated Pune transportation data when structured data is unavailable.

Data must be distinguishable as:

- sourced;
- curated;
- estimated;
- simulated/test.

## 7.9 AI

Use **Gemini 2.5 Flash**.

The AI is a conversational transportation assistant, not the routing engine.

Correct flow:

```text
User
 ↓
AI Assistant
 ↓
Intent/entity extraction
 ↓
IntelliTransit backend function
 ↓
OTP / PostgreSQL / application service
 ↓
Verified result
 ↓
AI explanation
 ↓
User
```

The AI must never invent bus numbers, stations, timings, fares, routes, ticket status, pass status, or availability.

The Gemini API key must remain on the Flask backend and never appear in frontend JavaScript.

## 7.10 Payments

Use **Razorpay Test Mode**.

Flow:

```text
User selects ticket/pass
 ↓
Flask creates payment order
 ↓
Razorpay Test Checkout
 ↓
Payment result
 ↓
Backend verification
 ↓
Ticket/pass activation
```

Never store card numbers, CVV, UPI credentials, or payment passwords.

Test transactions are demonstrations only.

## 7.11 QR

Use a Python QR-generation library.

QR data should contain a secure random ticket/pass token or identifier, not unnecessary personal information.

Validation is online through the IntelliTransit backend.

---

# 8. User Types

### Guest

Can:
- plan journeys;
- compare routes;
- view time/fare/walking/transfers;
- view maps;
- use basic AI journey assistance.

Guest searches should normally remain transient.

### Registered User

Can additionally:
- save locations;
- save preferences;
- view journey history;
- receive personalization;
- manage tickets;
- manage passes;
- view payment/ticket history.

### Administrator

Can:
- manage application-level transport metadata;
- manage fare configurations;
- perform authorized ticket validation;
- manage relevant ticket/pass records where appropriate;
- maintain application configuration.

The administrator does not control real-world transportation infrastructure.

---

# 9. Core User Flow

```text
Origin + Destination
        ↓
Flask API
        ↓
OpenTripPlanner
        ↓
Candidate multimodal itineraries
        ↓
IntelliTransit Intelligence Layer
        ↓
Route comparison/ranking
        ↓
MapLibre visualization
        ↓
User selects journey
        ↓
Optional ticket/pass purchase
        ↓
Razorpay Test Mode
        ↓
Backend payment verification
        ↓
Active ticket/pass
        ↓
QR display
        ↓
Authorized validation
```

---

# 10. Example Journey

```text
Origin: Point A
Destination: Point D

Point A
  ↓ Taxi
Point B
  ↓ Metro
Point C
  ↓ Bus
Point D
```

The system presents this as one complete journey.

---

# 11. Architecture Principle

Keep the system modular but simple.

```text
Browser
├── HTML
├── CSS
└── JavaScript
        │
        │ REST/HTTP
        ▼
Python + Flask
├── Authentication
├── Journey APIs
├── User APIs
├── Ticket APIs
├── Pass APIs
├── Payment APIs
├── AI APIs
├── Admin APIs
│
├── IntelliTransit Intelligence Layer
├── PostgreSQL
├── OpenTripPlanner
├── Gemini API
└── Razorpay
```

Do not introduce microservices for the academic project.

A single Flask application with clearly separated modules is preferred.

---

# 12. Separation of Responsibilities

| Component | Responsibility |
|---|---|
| HTML | Page structure |
| CSS | Styling and responsive layout |
| JavaScript | Frontend interaction and API calls |
| Flask | Backend/API/application orchestration |
| PostgreSQL | Application/business data |
| OpenTripPlanner 2 | Multimodal journey routing |
| IntelliTransit Intelligence Layer | Ranking, fare handling, preferences, presentation |
| OpenStreetMap | Geographic data |
| MapLibre GL JS | Map visualization |
| Gemini 2.5 Flash | Conversational transportation assistance |
| Razorpay | Test payment processing |
| QR library | QR generation |

No component should silently take over another component's core responsibility.

---

# 13. Database Principle

Use a hybrid data architecture.

### Routing/network data remains primarily in:

- OpenTripPlanner;
- GTFS;
- OpenStreetMap;
- relevant public transportation sources.

### PostgreSQL stores:

- users;
- preferences;
- saved locations;
- journey summaries;
- payments;
- tickets;
- passes;
- transport metadata;
- fare configurations;
- ticket validations.

Do not duplicate the complete GTFS/OTP transportation network inside PostgreSQL.

---

# 14. Core Database Tables

The current database design contains 10 core tables:

1. `users`
2. `user_preferences`
3. `saved_locations`
4. `journeys`
5. `transport_services`
6. `fare_configurations`
7. `payments`
8. `tickets`
9. `passes`
10. `ticket_validations`

The detailed schema belongs in the database-design document.

---

# 15. Development Environment

Development is native on Windows.

Core tools:

- Windows 10/11 64-bit
- Python
- Flask
- pip
- PostgreSQL
- pgAdmin
- psql
- Java/JDK for OpenTripPlanner
- HTML/CSS/JavaScript
- VS Code
- Git/GitHub
- Postman
- modern web browser

Docker is not a core dependency.

---

# 16. Hardware Baseline

Minimum practical:

- 64-bit quad-core CPU;
- 8 GB RAM;
- 10–20 GB free storage;
- stable internet for external services;
- modern browser.

Recommended:

- modern 6-core+ CPU;
- 16 GB RAM;
- SSD;
- stable broadband.

A separate production server is not required for local academic demonstration.

---

# 17. Security Principles

1. Never store plaintext passwords.
2. Hash passwords with bcrypt.
3. Protect authenticated APIs with JWT.
4. Enforce USER/ADMIN authorization.
5. Keep Gemini and Razorpay secrets on the backend.
6. Validate API input.
7. Use safe/parameterized database operations.
8. Do not expose unnecessary personal information in QR codes.
9. Verify payment before activating a ticket/pass.
10. Prevent access to another user's private records.
11. Never trust frontend-only payment or ticket status.

---

# 18. Performance Principles

The target is practical academic responsiveness, not production-scale benchmarking.

- Journey searches should return within a reasonable time under local demonstration conditions.
- The frontend should remain responsive on desktop and mobile browsers.
- Database operations should be reasonably efficient.
- External-service failures should be handled gracefully.
- Core journey planning must continue to work when Gemini is unavailable.

AI is an enhancement, not a dependency for routing.

---

# 19. Failure Handling

### Core routing dependency

OpenTripPlanner is required for actual multimodal route calculation.

### Optional AI dependency

Gemini is not required for basic route planning.

If Gemini is unavailable:

```text
Journey Planning → WORKS
AI Assistant      → UNAVAILABLE / ERROR MESSAGE
```

The application must never fabricate a response to hide an unavailable service.

---

# 20. Development Philosophy

This is a **TYBSc academic project**, not a commercial transportation infrastructure platform.

Therefore:

- prefer simple architecture;
- prefer understandable code;
- prefer maintainable modules;
- avoid unnecessary frameworks;
- avoid microservices;
- avoid premature optimization;
- avoid duplicate transportation datasets;
- keep local development straightforward;
- build incrementally;
- test each module before proceeding;
- document only what is actually implemented.

The objective is a technically credible, demonstrable, and understandable system.

---

# 21. Scope-Control Rule

Every proposed feature must answer:

> Does this directly support IntelliTransit's core journey-planning or required academic functionality?

If not, it should not automatically be added.

Future ideas may be recorded separately without entering the current implementation.

---

# 22. Definition of Done

The core system is complete when this workflow works:

```text
Guest/Registered User
        ↓
Origin + Destination
        ↓
Flask API
        ↓
OpenTripPlanner
        ↓
Multimodal itineraries
        ↓
IntelliTransit ranking/presentation
        ↓
MapLibre visualization
        ↓
Selected journey
        ↓
Optional ticket/pass
        ↓
Razorpay Test Mode
        ↓
Payment verification
        ↓
Active ticket/pass
        ↓
QR
        ↓
Authorized validation
```

Additionally:

- authentication works;
- PostgreSQL persistence works;
- preferences work;
- saved locations work;
- registered-user journey history works;
- AI assistant can call backend functions;
- admin functions work at the defined application level;
- major errors are handled;
- responsive layouts work;
- documentation matches actual implementation.

---

# 23. Frozen Decision Summary

```text
PROJECT
IntelliTransit

FORMAL TITLE
IntelliTransit: An Intelligent Multimodal Transportation and Journey Planning Platform

GEOGRAPHY
Pune only

PLATFORM
Responsive Web Application

FRONTEND
HTML5 + CSS3 + JavaScript ES6+

BACKEND
Python + Flask

DATABASE
PostgreSQL

AUTHENTICATION
JWT + bcrypt

ROUTING
OpenTripPlanner 2

CUSTOM INTELLIGENCE
IntelliTransit Intelligence Layer

MAP DATA
OpenStreetMap

MAP RENDERING
MapLibre GL JS

TRANSIT DATA
GTFS + reliable public/official data + curated fallback

AI
Gemini 2.5 Flash

PAYMENTS
Razorpay Test Mode

TICKETING
Custom IntelliTransit tickets and passes

QR
Backend-generated secure token

USER TYPES
Guest / USER / ADMIN

DEVELOPMENT
Native Windows

DOCKER
Not a core dependency

NATIVE MOBILE APP
Not included

AI ROUTING
AI does not calculate routes

DATABASE PRINCIPLE
Application data in PostgreSQL;
routing/network data remains with OTP/GTFS/OSM
```

---

# 24. Rule for All Future Development Documents

Treat this document as the **baseline architecture and scope**.

If a future development document proposes something that conflicts with this file, explicitly identify the conflict before changing the architecture.

Do not silently reintroduce:

- React
- Vite
- Node.js
- Express.js
- unnecessary frontend frameworks
- unnecessary backend services
- unnecessary microservices
- Docker as a core dependency

The project must remain **simple, understandable, modular, and achievable**.

---

**END OF DOCUMENT**
