# IntelliTransit — Database Design

**Document:** `03_DATABASE_DESIGN.md`  
**Project:** IntelliTransit  
**Depends on:** `01_PROJECT_DEFINITION.md`, `02_SYSTEM_ARCHITECTURE.md`  
**Status:** DATABASE DESIGN BASELINE — LEG-BASED TICKETING UPDATE

---

# 1. Purpose

This document defines the PostgreSQL database design for IntelliTransit.

The database stores **application and business data** required by IntelliTransit.

It does **not** attempt to replace OpenTripPlanner, GTFS, or OpenStreetMap as the authoritative transportation-network system.

The database is designed around:

- users;
- authentication-related data;
- user preferences;
- saved locations;
- journey summaries;
- journey legs;
- transport-service metadata;
- fare configurations;
- payments;
- tickets;
- passes;
- ticket validation records.

---

# 2. Database Technology

Database:

**PostgreSQL**

Primary responsibility:

```text
Persistent application/business data
```

PostgreSQL does not become the routing engine.

The transportation routing network remains outside the application database and is handled through OpenTripPlanner and its configured data sources.

---

# 3. Database Architecture Principle

The architecture follows this rule:

```text
OTP / GTFS / OSM
        ↓
Transportation network + routing information

PostgreSQL
        ↓
IntelliTransit application + business information
```

Do not create a second complete copy of the GTFS transit graph inside PostgreSQL.

---

# 4. Core Tables

The initial database contains eleven core tables:

```text
1. users
2. user_preferences
3. saved_locations
4. journeys
5. journey_legs
6. transport_services
7. fare_configurations
8. payments
9. tickets
10. passes
11. ticket_validations
```

Relationship overview:

```text
users
 ├── user_preferences
 ├── saved_locations
 ├── journeys
 ├── payments
 ├── tickets
 ├── passes
 └── ticket_validations

journeys
 └── journey_legs
        └── tickets

transport_services
 └── fare_configurations

payments
 ├── tickets (1:1)
 └── passes (1:1)

tickets
 └── ticket_validations

ticket_validations
 └── users (validator)
```

---

# 5. Entity Relationship Diagram

The current ticketing model is leg-based. The overall journey can contain multiple legs, while each ticket is attached to one ticketable leg.

```text
┌──────────────────────┐
│        USERS         │
├──────────────────────┤
│ PK user_id           │
│ full_name            │
│ email                │
│ phone                │
│ password_hash        │
│ role                 │
│ is_active            │
└──────────┬───────────┘
           │
     ┌─────┼───────────────┬──────────────┬──────────────┐
     │     │               │              │              │
     ▼     ▼               ▼              ▼              ▼
  PREFS  SAVED          JOURNEYS       PAYMENTS       TICKETS
  1:1    LOCATIONS         1:N            1:N            1:N
                          │                │              │
                          ▼                │              ▼
                    JOURNEY_LEGS          │        VALIDATIONS
                          │                │
                          └──────┐         │
                                 ▼         ▼
                              TICKETS   PASSES

┌────────────────────────┐
│ TRANSPORT_SERVICES     │
├────────────────────────┤
│ PK service_id          │
│ mode                   │
│ operator_name          │
│ service_name           │
│ external_id            │
│ is_active              │
└──────────┬─────────────┘
           │ 1:N
           ▼
     JOURNEY_LEGS
           │
           │ 1:N ticketable legs
           ▼
        TICKETS

PAYMENTS → TICKETS = 1:1
PAYMENTS → PASSES  = 1:1
```

A walking/transfer leg may exist in `journey_legs` without a ticket.

---

# 6. `users`

Stores registered IntelliTransit users.

## Fields

| Field | Type | Constraints |
|---|---|---|
| user_id | UUID | Primary Key |
| full_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| phone | VARCHAR(15) | UNIQUE |
| password_hash | TEXT | NOT NULL |
| role | VARCHAR(20) | USER / ADMIN |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Purpose

Stores:

- identity;
- login identifier;
- password hash;
- role;
- account status;
- timestamps.

## Security

Never store plaintext passwords.

Store only bcrypt password hashes.

---

# 7. `user_preferences`

Stores one preference record for each registered user.

## Fields

| Field | Type | Constraints |
|---|---|---|
| preference_id | UUID | Primary Key |
| user_id | UUID | FK → users, UNIQUE |
| preferred_mode | VARCHAR(20) | Optional |
| route_preference | VARCHAR(30) | Optional |
| max_walking_distance_m | INTEGER | Optional |
| avoid_taxi | BOOLEAN | DEFAULT FALSE |
| avoid_transfers | BOOLEAN | DEFAULT FALSE |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationship

```text
users 1 ───────── 1 user_preferences
```

`user_id` is unique so one user cannot have multiple preference rows.

---

# 8. `saved_locations`

Stores locations saved by registered users.

Examples:

```text
Home
College
Office
Gym
```

## Fields

| Field | Type | Constraints |
|---|---|---|
| location_id | UUID | Primary Key |
| user_id | UUID | FK → users |
| label | VARCHAR(50) | NOT NULL |
| location_name | VARCHAR(150) | NOT NULL |
| address | TEXT | Optional |
| latitude | DECIMAL(9,6) | NOT NULL |
| longitude | DECIMAL(9,6) | NOT NULL |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationship

```text
users 1 ───────── N saved_locations
```

---

# 9. `journeys`

Stores application-level journey records.

A journey record represents a user's planned/selected journey rather than the entire transportation network.

## Fields

| Field | Type | Constraints |
|---|---|---|
| journey_id | UUID | Primary Key |
| user_id | UUID | FK → users, nullable |
| origin_name | VARCHAR(150) | NOT NULL |
| origin_latitude | DECIMAL(9,6) | NOT NULL |
| origin_longitude | DECIMAL(9,6) | NOT NULL |
| destination_name | VARCHAR(150) | NOT NULL |
| destination_latitude | DECIMAL(9,6) | NOT NULL |
| destination_longitude | DECIMAL(9,6) | NOT NULL |
| departure_time | TIMESTAMP | Optional |
| arrival_time | TIMESTAMP | Optional |
| total_duration_min | INTEGER | Optional |
| walking_distance_m | INTEGER | Optional |
| estimated_fare | DECIMAL(10,2) | Optional |
| route_type | VARCHAR(30) | Optional |
| otp_itinerary_id | VARCHAR(255) | Optional |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationship

```text
users 1 ───────── N journeys
```

`user_id` may be NULL when the system chooses not to persist a guest journey.

---

# 10. `journey_legs`

Stores the individual transportation legs that make up a planned journey.

A journey is the complete A → C trip. A journey may contain multiple legs such as:

```text
A → B   Taxi
B → C   Metro
C → D   Bus
```

Each leg is independently identifiable so that ticketing can be handled per ticketable transportation segment rather than treating the entire multimodal journey as one inseparable ticket.

## Fields

| Field | Type | Constraints |
|---|---|---|
| leg_id | UUID | Primary Key |
| journey_id | UUID | FK → journeys, NOT NULL |
| sequence_number | INTEGER | NOT NULL |
| mode | VARCHAR(20) | NOT NULL |
| service_id | UUID | FK → transport_services, nullable |
| from_name | VARCHAR(150) | NOT NULL |
| from_latitude | DECIMAL(9,6) | NOT NULL |
| from_longitude | DECIMAL(9,6) | NOT NULL |
| to_name | VARCHAR(150) | NOT NULL |
| to_latitude | DECIMAL(9,6) | NOT NULL |
| to_longitude | DECIMAL(9,6) | NOT NULL |
| departure_time | TIMESTAMP | Optional |
| arrival_time | TIMESTAMP | Optional |
| duration_min | INTEGER | Optional |
| walking_distance_m | INTEGER | Optional |
| estimated_fare | DECIMAL(10,2) | Optional |
| is_ticketable | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationship

```text
journeys 1 ───────── N journey_legs
transport_services 1 ── N journey_legs (where applicable)
```

`is_ticketable` distinguishes a leg that can have an IntelliTransit ticket from a transfer/walking leg that does not require a ticket. `sequence_number` must be unique within a journey so that the leg order is deterministic.

## Ticketing Principle

The complete journey remains unified for planning and history, but ticketing operates at the leg level.

Example:

```text
Journey J001: A → C

Leg 1: A → B, Taxi, ticketable, ₹80
Leg 2: B → C, Metro, ticketable, ₹30
```

The user does not need to purchase a ticket for a non-ticketable walking/transfer leg.

---

# 11. Journey Data Boundary

The `journeys` table must not become a duplicate OTP database.

It stores a compact application-level representation such as:

```text
Origin
Destination
Time
Duration
Walking distance
Estimated fare
Route type
OTP itinerary reference
```

It does not store:

```text
Entire GTFS graph
All stops
All transit patterns
All street edges
Entire OTP routing graph
```

Those remain under the routing/data-source architecture.

If exact itinerary reconstruction is later required, a controlled JSONB snapshot or compact itinerary reference can be introduced without redesigning the whole database.

---

# 12. `transport_services`

Stores application-level transportation-service metadata.

## Fields

| Field | Type | Constraints |
|---|---|---|
| service_id | UUID | Primary Key |
| mode | VARCHAR(20) | BUS / METRO / TAXI |
| operator_name | VARCHAR(100) | NOT NULL |
| service_name | VARCHAR(150) | NOT NULL |
| external_id | VARCHAR(100) | Optional |
| description | TEXT | Optional |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Purpose

This table is useful for application-level metadata and configuration.

It does not replace OTP's transit feed.

Example:

```text
mode = METRO
operator_name = Pune Metro
service_name = Pune Metro
```

---

# 13. `fare_configurations`

Stores fare configuration used by IntelliTransit for application-level fare calculation/estimation.

## Fields

| Field | Type | Constraints |
|---|---|---|
| fare_id | UUID | Primary Key |
| service_id | UUID | FK → transport_services |
| fare_type | VARCHAR(30) | NOT NULL |
| base_fare | DECIMAL(10,2) | NOT NULL |
| per_km_rate | DECIMAL(10,2) | Optional |
| minimum_fare | DECIMAL(10,2) | Optional |
| effective_from | TIMESTAMP | NOT NULL |
| effective_until | TIMESTAMP | Optional |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationship

```text
transport_services 1 ───────── N fare_configurations
```

This allows fare configurations to change over time.

---

# 14. `payments`

Stores payment transactions associated with tickets or passes.

## Fields

| Field | Type | Constraints |
|---|---|---|
| payment_id | UUID | Primary Key |
| user_id | UUID | FK → users |
| razorpay_order_id | VARCHAR(100) | UNIQUE |
| razorpay_payment_id | VARCHAR(100) | UNIQUE, nullable |
| amount | DECIMAL(10,2) | NOT NULL |
| currency | CHAR(3) | DEFAULT `INR` |
| payment_type | VARCHAR(20) | TICKET / PASS |
| status | VARCHAR(20) | PENDING / SUCCESS / FAILED / REFUNDED |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationship

```text
users 1 ───────── N payments
```

A payment represents one business-item payment. For the initial implementation:

```text
1 payment → 1 ticket
OR
1 payment → 1 pass
```

The `payment_type` identifies which business item is being paid for. Multiple ticketable legs in one journey therefore result in separate ticket/payment records rather than one combined journey-wide payment.

---

# 15. `tickets`

Stores issued journey tickets.

## Fields

| Field | Type | Constraints |
|---|---|---|
| ticket_id | UUID | Primary Key |
| user_id | UUID | FK → users |
| journey_id | UUID | FK → journeys |
| journey_leg_id | UUID | FK → journey_legs |
| payment_id | UUID | FK → payments, UNIQUE |
| ticket_token | VARCHAR(255) | UNIQUE, NOT NULL |
| status | VARCHAR(20) | PENDING / ACTIVE / USED / EXPIRED / CANCELLED |
| origin | VARCHAR(150) | NOT NULL |
| destination | VARCHAR(150) | NOT NULL |
| fare | DECIMAL(10,2) | NOT NULL |
| valid_from | TIMESTAMP | Optional |
| valid_until | TIMESTAMP | Optional |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationships

```text
users 1 ───────── N tickets

journeys 1 ────── N tickets

journey_legs 1 ── N tickets

payments 1 ────── 1 ticket
```

The historical fields:

```text
origin
destination
fare
```

are intentionally stored on the ticket. They represent the purchased leg, not necessarily the entire journey destination. The ticket also retains both `journey_id` and `journey_leg_id` so the ticket can be traced back to the complete journey and the exact purchased segment.

This means later changes to journey/fare information do not rewrite the historical ticket record.

---

# 16. `passes`

Stores purchased transportation passes.

Supported pass types:

```text
DAILY
WEEKLY
MONTHLY
```

## Fields

| Field | Type | Constraints |
|---|---|---|
| pass_id | UUID | Primary Key |
| user_id | UUID | FK → users |
| payment_id | UUID | FK → payments, UNIQUE |
| pass_type | VARCHAR(20) | DAILY / WEEKLY / MONTHLY |
| pass_token | VARCHAR(255) | UNIQUE |
| status | VARCHAR(20) | PENDING / ACTIVE / EXPIRED / CANCELLED |
| price | DECIMAL(10,2) | NOT NULL |
| valid_from | TIMESTAMP | Optional |
| valid_until | TIMESTAMP | Optional |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationships

```text
users 1 ───────── N passes

payments 1 ────── 1 pass
```

---

# 17. `ticket_validations`

Stores validation attempts/results for tickets.

## Fields

| Field | Type | Constraints |
|---|---|---|
| validation_id | UUID | Primary Key |
| ticket_id | UUID | FK → tickets |
| validator_user_id | UUID | FK → users |
| validation_status | VARCHAR(20) | VALID / INVALID / EXPIRED / CANCELLED |
| validation_time | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| remarks | TEXT | Optional |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |

## Relationships

```text
tickets 1 ───────── N ticket_validations

users 1 ─────────── N ticket_validations
                   (as validator)
```

This preserves a validation history instead of overwriting the previous result.

---

# 18. Complete Relationship Table

| Parent Table | Child Table | Relationship | Foreign Key |
|---|---|---|---|
| users | user_preferences | 1:1 | user_preferences.user_id |
| users | saved_locations | 1:N | saved_locations.user_id |
| users | journeys | 1:N | journeys.user_id |
| users | payments | 1:N | payments.user_id |
| users | tickets | 1:N | tickets.user_id |
| users | passes | 1:N | passes.user_id |
| users | ticket_validations | 1:N | ticket_validations.validator_user_id |
| transport_services | fare_configurations | 1:N | fare_configurations.service_id |
| journeys | journey_legs | 1:N | journey_legs.journey_id |
| transport_services | journey_legs | 1:N | journey_legs.service_id |
| journeys | tickets | 1:N | tickets.journey_id |
| journey_legs | tickets | 1:N | tickets.journey_leg_id |
| payments | tickets | 1:1 | tickets.payment_id |
| payments | passes | 1:1 | passes.payment_id |
| tickets | ticket_validations | 1:N | ticket_validations.ticket_id |

---

# 19. Primary Keys

All core tables use UUID primary keys.

Reason:

- avoids sequential public identifiers;
- provides globally unique application identifiers;
- works well across application components;
- avoids exposing simple record counts through IDs.

Example:

```text
user_id
journey_id
ticket_id
pass_id
payment_id
```

---

# 20. Foreign-Key Rules

Foreign keys enforce relationships.

Examples:

```text
user_preferences.user_id
        → users.user_id

journeys.user_id
        → users.user_id

journey_legs.journey_id
        → journeys.journey_id

journey_legs.service_id
        → transport_services.service_id

tickets.journey_id
        → journeys.journey_id

tickets.journey_leg_id
        → journey_legs.leg_id

tickets.payment_id
        → payments.payment_id

passes.payment_id
        → payments.payment_id

fare_configurations.service_id
        → transport_services.service_id

ticket_validations.ticket_id
        → tickets.ticket_id
```

Foreign-key behavior must prevent orphaned business records.

Deletion behavior should be chosen carefully for each relationship rather than applying blanket cascading deletes.

For example, historical tickets and payment records should not disappear simply because an application account is deactivated.

---

# 21. Important Constraints

## Users

```text
email UNIQUE NOT NULL
phone UNIQUE when provided
role restricted to supported roles
```

## Preferences

```text
user_id UNIQUE
```

## Saved Locations

```text
label NOT NULL
coordinates NOT NULL
```

## Payments

```text
razorpay_order_id UNIQUE
razorpay_payment_id UNIQUE when present
amount NOT NULL
```

## Tickets

- `journey_leg_id` must refer to a leg belonging to the same `journey_id`.
- `payment_id` is UNIQUE so one payment activates at most one ticket.
- A ticket may only be created for a ticketable leg.

```text
ticket_token UNIQUE NOT NULL
fare NOT NULL
```

## Passes

- `payment_id` is UNIQUE so one payment activates at most one pass.

```text
pass_token UNIQUE
price NOT NULL
```

---

# 22. Status Values

Status fields should use controlled values.

## User role

```text
USER
ADMIN
```

## Ticket

```text
PENDING
ACTIVE
USED
EXPIRED
CANCELLED
```

## Pass

```text
PENDING
ACTIVE
EXPIRED
CANCELLED
```

## Payment

```text
PENDING
SUCCESS
FAILED
REFUNDED
```

## Validation

```text
VALID
INVALID
EXPIRED
CANCELLED
```

These values should be validated in the backend and, where appropriate, constrained at the database level.

---

# 23. Transport Mode Values

The initial supported modes are:

```text
BUS
METRO
TAXI
```

Walking is part of journey movement/transfer information and does not require a separate `transport_services` row in the initial schema.

---

# 24. Fare Representation

Fare values use:

```text
DECIMAL(10,2)
```

rather than floating-point numeric types.

This is important for monetary values.

Example:

```text
125.50
```

not:

```text
125.499999...
```

---

# 25. Geographic Coordinates

Latitude and longitude are stored as:

```text
DECIMAL(9,6)
```

This provides sufficient precision for the project's Pune-focused application.

Example:

```text
latitude  = 18.528500
longitude = 73.874300
```

---

# 26. Time Fields

Time-related fields use PostgreSQL timestamp types.

Important fields include:

```text
departure_time
arrival_time
valid_from
valid_until
created_at
updated_at
validation_time
```

Where timezone-aware behavior is required by the implementation, use PostgreSQL timezone-aware timestamp handling consistently.

The application should avoid mixing timezone assumptions.

---

# 27. Indexing Strategy

Primary keys and unique constraints automatically provide important indexes.

Additional indexes should be added for common query patterns.

Likely indexes:

```text
users.email
users.phone

saved_locations.user_id

journeys.user_id
journeys.created_at

payments.user_id
payments.razorpay_order_id
payments.razorpay_payment_id

tickets.user_id
tickets.ticket_token
tickets.status

passes.user_id
passes.pass_token
passes.status

ticket_validations.ticket_id
ticket_validations.validator_user_id
ticket_validations.validation_time

fare_configurations.service_id
fare_configurations.is_active
```

Indexes should be created based on actual query usage rather than indexing every column.

---

# 28. Journey History Queries

A registered user's journey history can be obtained using:

```text
journeys.user_id
```

and ordered by:

```text
created_at DESC
```

This supports:

- recent journeys;
- previous routes;
- frequently used locations;
- future personalization.

---

# 29. Personalization Data

Personalization can initially use:

```text
user_preferences
saved_locations
journeys
```

For example:

```text
User frequently travels:
Home → College
```

The application can identify repeated journey patterns from stored journey records.

A separate recommendation database is not required for the initial project.

---

# 30. Data Ownership

The database should distinguish between application-owned data and externally sourced transportation data.

## IntelliTransit-owned

```text
users
preferences
saved locations
journey history
payments
tickets
passes
validation records
application transport metadata
fare configuration
```

## OTP / transit-data owned

```text
transit network
GTFS schedules
transit stops
routes
patterns
street graph
routing calculations
```

## External service owned

```text
Gemini model processing
Razorpay payment processing
```

---

# 31. Ticket Historical Snapshot Principle

A ticket should retain the information needed to understand what was purchased at the time. Because tickets are leg-based, the snapshot describes the purchased journey leg.

Therefore:

```text
tickets.origin
tickets.destination
tickets.fare
```

are intentionally duplicated from journey/fare information.

This is not an accidental duplication.

It is a historical snapshot.

Example:

```text
Journey estimated fare at purchase = ₹40

Later fare configuration changes = ₹45

Existing ticket record
        ↓
Still shows ₹40
```

---

# 32. Payment-to-Item Principle

The initial system does not implement a shopping cart or a combined journey-wide payment.

A payment is associated with exactly one business item:

```text
Payment
   ├── Ticket for one ticketable journey leg
   OR
   └── Pass
```

The `payment_type` field indicates:

```text
TICKET
PASS
```

For a multimodal journey:

```text
A → B → C

Leg 1: Taxi  ₹80  → Ticket 1 → Payment 1
Leg 2: Metro ₹30  → Ticket 2 → Payment 2
```

This avoids a partial-journey refund problem when a user completes A → B but decides not to continue from B → C. If the second leg has not been purchased, there is nothing to refund. If it has already been purchased, cancellation/refund is handled at the individual ticket level according to the configured cancellation policy.

The user experience may still present the trip as one journey; the payment model remains leg-based.

---

# 33. Ticket Validation Principle

Ticket validation creates a separate record.

Do not overwrite the ticket itself with every scan.

Instead:

```text
Ticket
  │
  ├── Validation 1
  ├── Validation 2
  ├── Validation 3
  └── ...
```

This provides a history of validation attempts.

---

# 34. Guest Data Principle

Guest users do not need permanent accounts for basic journey planning.

Therefore:

```text
Guest
  ↓
Plan journey
  ↓
Receive route
  ↓
No permanent user record required
```

Registration is required for features such as:

- saved locations;
- journey history;
- tickets;
- passes;
- payment history;

Ticket purchases are made against a selected ticketable journey leg.
- personalized preferences.

---

# 35. Database Security

Database credentials must never be placed in:

```text
HTML
CSS
JavaScript
GitHub source code
```

Use server-side environment configuration.

The browser communicates with Flask.

Only Flask communicates with PostgreSQL.

```text
Browser
   X
   │
   │ no direct database access
   X
PostgreSQL

Browser
   ↓
Flask
   ↓
PostgreSQL
```

---

# 36. Database Backup Consideration

During development, database backups should be performed before major schema changes.

Recommended development artifacts:

```text
schema.sql
seed.sql
```

The project should be reproducible from a clean PostgreSQL database.

---

# 37. Seed Data

Development seed data may include:

- sample users;
- sample transport services;
- sample fare configurations;
- sample application configuration.

Seed data must be clearly identified as development/demo data.

Real credentials and real payment information must never be included.

---

# 38. Migration Strategy

Database changes should be version-controlled.

Recommended concept:

```text
database/
└── migrations/
    ├── 001_initial_schema
    ├── 002_add_preferences
    └── ...
```

The exact migration tool can be selected during backend implementation.

Do not manually modify production/demo databases without recording the schema change.

---

# 39. Database Transaction Principles

Transactions should be used where multiple related operations must succeed together.

Example ticket purchase flow:

```text
Create payment record
        +
Create pending ticket
```

Payment verification and ticket activation must be handled consistently.

A successful payment must not result in an incompletely persisted ticket.

---

# 40. Example Ticket Purchase Data Relationship

```text
USER
 │
 └── JOURNEY
       │
       └── JOURNEY_LEG
              │
              └── TICKET
                    │
                    └── PAYMENT
```

Example:

```text
User:
Manas

Journey:
Pune Station → Hinjawadi

Leg 1:
Pune Station → Shivajinagar
Metro
Ticketable = TRUE

Payment 1:
₹30
Status = SUCCESS

Ticket 1:
Pune Station → Shivajinagar
Fare = ₹30
Status = ACTIVE
```

If the same journey contains another ticketable leg:

```text
Leg 2:
Shivajinagar → Hinjawadi
Bus
Ticketable = TRUE

Payment 2:
separate payment

Ticket 2:
separate ticket
```

---

# 41. Database Design Rules

The implementation must follow these rules:

1. Use PostgreSQL.
2. Use UUID primary keys.
3. Enforce foreign-key relationships.
4. Use unique constraints where required.
5. Use DECIMAL for money.
6. Validate status values.
7. Never store plaintext passwords.
8. Never store card/UPI credentials.
9. Do not duplicate the entire OTP transit graph.
10. Preserve historical ticket information.
11. Keep guest journey planning possible.
12. Model journey legs separately from the overall journey.
13. Ticket only ticketable legs.
14. Use one payment per ticket/pass business item.
15. Keep application data separate from routing data.
16. Use indexes for real query patterns.
17. Use migrations for schema changes.
18. Keep demo/seed data separate from production-like secrets.

---

# 42. Final Schema Summary

```text
USERS
 ├── USER_PREFERENCES
 ├── SAVED_LOCATIONS
 ├── JOURNEYS
 │     └── JOURNEY_LEGS
 ├── PAYMENTS
 │     ├── TICKETS
 │     └── PASSES
 ├── TICKETS
 │     └── TICKET_VALIDATIONS
 ├── PASSES
 └── TICKET_VALIDATIONS

TRANSPORT_SERVICES
 └── FARE_CONFIGURATIONS
```

Core database purpose:

> **Persist IntelliTransit's users, application state, journey history, payment records, ticket/pass lifecycle, fare configuration, and validation history without attempting to reproduce the external transportation-routing infrastructure.**

---

# 43. Relationship to Next Documents

This database design is the baseline for:

`04_BACKEND_API_SPECIFICATION.md`

The API specification must use these entities and relationships rather than inventing a separate data model.

The later routing document will explain how OTP results map into `journeys`.

The ticket/payment document will explain how `journeys`, `journey_legs`, `payments`, `tickets`, `passes`, and `ticket_validations` participate in the leg-based ticketing workflow.

---

**END OF DOCUMENT**
