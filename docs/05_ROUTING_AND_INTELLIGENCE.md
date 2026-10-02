# IntelliTransit — Routing and Intelligence Specification

**Document:** `05_ROUTING_AND_INTELLIGENCE.md`  
**Project:** IntelliTransit  
**Depends on:** `01_PROJECT_DEFINITION.md`, `02_SYSTEM_ARCHITECTURE.md`, `03_DATABASE_DESIGN.md`, `04_BACKEND_API_SPECIFICATION.md`  
**Status:** ROUTING AND INTELLIGENCE BASELINE

---

# 1. Purpose

This document defines how IntelliTransit performs multimodal journey planning.

It establishes the boundary between:

- user input;
- Flask;
- OpenTripPlanner 2;
- GTFS;
- OpenStreetMap;
- the IntelliTransit Intelligence Layer;
- fare processing;
- user preferences;
- route presentation;
- journey persistence.

The central principle is:

> **OpenTripPlanner calculates candidate journeys. IntelliTransit processes, ranks, explains, and presents those journeys.**

IntelliTransit does not implement its own replacement for OTP's routing engine.

---

# 2. Routing Architecture

The routing pipeline is:

```text
User
  │
  ▼
Frontend
  │
  ▼
Flask Journey API
  │
  ▼
Journey Service
  │
  ▼
OTP Service
  │
  ▼
OpenTripPlanner 2
  │
  ├── OpenStreetMap-derived street/network data
  └── GTFS transit data
  │
  ▼
Candidate Itineraries
  │
  ▼
IntelliTransit Intelligence Layer
  │
  ├── Normalize
  ├── Validate
  ├── Calculate/attach fare
  ├── Apply preferences
  ├── Rank
  └── Prepare explanation
  │
  ▼
Journey API Response
  │
  ├── Route cards
  └── Map visualization
```

---

# 3. Responsibility of OpenTripPlanner

OpenTripPlanner 2 is the **routing engine**.

It is responsible for calculating feasible journeys across supported transportation modes.

It handles the underlying routing problem using its own internal algorithms.

For the project, the important conceptual distinction is:

```text
OTP
=
"How can the user travel from A to B?"

Intelligence Layer
=
"How should IntelliTransit organize and present the available alternatives?"
```

The application does not reimplement OTP's internal routing algorithms.

---

# 4. OTP Algorithm Boundary

OpenTripPlanner internally uses specialized routing techniques for street and transit routing.

For the project viva, the team can state:

> “We use OpenTripPlanner 2 as our routing engine. OTP internally uses specialized routing algorithms, including generalized-cost A* for street-based routing and Range RAPTOR for public-transit routing. We use OTP rather than implementing these routing algorithms ourselves.”

The project code should therefore treat OTP as an external routing subsystem rather than attempting to duplicate these algorithms.

---

# 5. Generalized-Cost A* — Conceptual Role

For street-based access and egress routing, OTP can use generalized-cost path search.

The important idea is that routing cost is not necessarily just physical distance.

A generalized cost can incorporate factors such as:

```text
distance
+
travel time
+
transfer/access penalties
+
mode-specific costs
+
other routing penalties
```

Therefore, the physically shortest path is not automatically the journey with the lowest generalized cost.

IntelliTransit consumes the resulting OTP itinerary rather than implementing this search itself.

---

# 6. RAPTOR — Conceptual Role

Public transit routing requires reasoning about:

- scheduled departures;
- arrival times;
- routes;
- stops;
- transfers;
- transit patterns.

OTP uses transit-specific routing mechanisms including Range RAPTOR.

IntelliTransit does not need to implement RAPTOR.

Instead:

```text
GTFS
 ↓
OTP transit network
 ↓
OTP transit routing
 ↓
Itineraries
 ↓
IntelliTransit
```

---

# 7. Transportation Data Sources

The routing environment uses a hybrid data strategy.

Primary sources:

```text
OpenStreetMap
GTFS / reliable public transit data
Published schedules
Published fare information
Curated Pune transportation data
```

The exact source for each dataset must be documented during deployment.

The system must distinguish between:

```text
SOURCED
CURATED
ESTIMATED
SIMULATED / TEST
```

This prevents demonstration data from being presented as live official data.

---

# 8. OpenStreetMap Role

OpenStreetMap provides geographic/street-network information used by the routing environment.

Conceptually:

```text
OpenStreetMap
      ↓
OTP routing network
      ↓
Walking / street access
      ↓
Candidate journey
```

OpenStreetMap is not the application's user database.

It is not used to store:

- users;
- tickets;
- payments;
- preferences.

---

# 9. GTFS Role

GTFS data represents structured public-transit information where available.

It may contain information such as:

- stops;
- routes;
- trips;
- schedules;
- service calendars;
- stop sequences.

The project should use appropriate Pune transit feeds/data where available.

If a complete structured feed is unavailable for a required service, the project may use a documented curated dataset.

---

# 10. GTFS and PostgreSQL Separation

Do not duplicate the full GTFS network into the IntelliTransit PostgreSQL database.

Correct:

```text
GTFS
 ↓
OTP
 ↓
Routing
```

Separate:

```text
PostgreSQL
 ↓
Application/business data
```

The application may store references or compact summaries where useful.

---

# 11. Journey Request

The journey planner accepts:

### Required

```text
origin
destination
```

### Optional

```text
departure_time
route_preference
max_walking_distance
avoid_taxi
avoid_transfers
preferred_mode
```

Example:

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
  "departure_time": null,
  "preferences": {
    "route_preference": "FASTEST",
    "max_walking_distance_m": 1500,
    "avoid_taxi": false,
    "avoid_transfers": false
  }
}
```

---

# 12. Journey Request Validation

Before calling OTP, Flask validates:

```text
origin exists
destination exists
latitude valid
longitude valid
```

If preferences are supplied:

```text
route_preference valid
max_walking_distance_m valid
avoid_taxi boolean
avoid_transfers boolean
```

The backend should reject malformed requests before sending them to OTP.

---

# 13. Pune Geographic Scope

IntelliTransit is Pune-focused.

The application should avoid pretending to support transportation systems outside the configured operating area.

Coordinates may be validated against the supported geographic area where practical.

However, the geographic validation should not be so rigid that legitimate edge-of-area journeys are incorrectly rejected.

The exact Pune boundary can be defined during deployment/testing.

---

# 14. OTP Request Construction

The OTP service converts the application's normalized request into the format expected by the configured OTP instance.

Conceptually:

```text
IntelliTransit Request
        ↓
otp_service.py
        ↓
OTP-compatible request
        ↓
OpenTripPlanner
```

The rest of the Flask application should not need to know OTP-specific request details.

This keeps OTP integration isolated.

---

# 15. Departure and Arrival Planning

The initial planner should support departure-time journey planning.

Conceptually:

```text
Origin
Destination
Departure Time
       ↓
OTP
       ↓
Itineraries
```

If arrival-time planning is implemented later, it should remain an OTP-service concern and expose a normalized application-level option.

---

# 16. Candidate Itineraries

OTP may return multiple candidate journeys.

Conceptually:

```text
OTP
 │
 ├── Itinerary A
 ├── Itinerary B
 ├── Itinerary C
 └── Itinerary D
```

The Intelligence Layer should normalize these into a consistent internal representation.

---

# 17. Internal Itinerary Representation

Each candidate itinerary should conceptually contain:

```text
route_id
duration
start_time
end_time
walking_distance
transfers
estimated_fare
legs[]
```

Each leg can contain:

```text
mode
start_time
end_time
duration
distance
from
to
route/service information
geometry
stops/stations where applicable
```

The exact Python representation is an implementation detail, but the information must be sufficient for:

- route cards;
- map rendering;
- fare processing;
- ranking;
- journey explanation.

---

# 18. Journey Legs

A multimodal route is represented as a sequence of legs.

Example:

```text
Leg 1
WALK
Pune Railway Station
        ↓
Bus Stop

Leg 2
BUS
Bus Stop
        ↓
Shivajinagar

Leg 3
WALK
Shivajinagar
        ↓
Metro Station

Leg 4
METRO
Shivajinagar
        ↓
Civil Court

Leg 5
WALK
Civil Court Metro
        ↓
Destination
```

This is the structure the frontend ultimately visualizes.

---

# 19. Supported Modes

Initial transportation modes:

```text
BUS
METRO
TAXI
WALK
```

Walking is a transfer/access mode rather than a separate `transport_services` record.

The application may display mode-specific icons and descriptions.

---

# 20. Multimodal Journey

A multimodal journey can combine modes.

Example:

```text
Origin
 ↓ WALK
Bus Stop
 ↓ BUS
Metro Station
 ↓ WALK
Metro Station
 ↓ METRO
Destination Station
 ↓ WALK
Destination
```

The system should treat the complete sequence as one journey.

---

# 21. Route Normalization

OTP output should first be normalized.

Conceptually:

```text
Raw OTP response
       ↓
OTP adapter
       ↓
Normalized itinerary
       ↓
Intelligence Layer
```

Normalization prevents the rest of the application from becoming tightly coupled to raw OTP response structures.

---

# 22. Normalization Goals

The normalized representation should make it easy to determine:

```text
total journey duration
walking distance
number of transfers
modes used
start/end time
fare estimate
leg sequence
route geometry
origin/destination
```

This representation becomes the contract between OTP integration and the rest of IntelliTransit.

---

# 23. Route Feasibility Validation

Before ranking an itinerary, the Intelligence Layer should verify that essential information exists.

For example:

```text
Itinerary exists
AND
duration available
AND
leg sequence valid
AND
origin/destination available
```

If important information is missing, the itinerary can be excluded from presentation or marked as incomplete according to implementation requirements.

The application must not invent missing transportation details.

---

# 24. Fare Architecture

Fare handling is separate from core route calculation.

Conceptually:

```text
OTP itinerary
      ↓
Identify services/modes
      ↓
Fare Service
      ↓
Fare configuration / available fare information
      ↓
Journey fare estimate
```

The fare may be:

```text
SOURCED
ESTIMATED
```

depending on the available data.

The response should retain enough information for the frontend to distinguish an estimate from a verified fare where necessary.

---

# 25. Fare Aggregation

For a multimodal journey:

```text
Total Fare
=
Bus Fare
+
Metro Fare
+
Taxi Fare
+
other applicable components
```

Walking contributes:

```text
₹0
```

unless a future implementation explicitly introduces another charge.

The exact fare rules are defined by the configured fare data.

---

# 26. Fare Service Boundary

Fare logic should be isolated in:

```text
fare_service.py
```

The journey route should not contain scattered fare calculations.

Conceptually:

```text
Journey Service
      ↓
Fare Service
      ↓
Fare Configuration
      ↓
Calculated/estimated fare
```

---

# 27. Route Preferences

The initial supported route preferences are:

```text
FASTEST
CHEAPEST
LEAST_WALKING
FEWEST_TRANSFERS
BALANCED
```

These preferences affect presentation/ranking.

They do not cause the system to invent routes not provided by OTP.

---

# 28. FASTEST

The primary factor is:

```text
total journey duration
```

Shorter journey duration receives stronger preference.

Other constraints may still be considered to prevent obviously unusable itineraries.

---

# 29. CHEAPEST

The primary factor is:

```text
estimated total fare
```

Lower estimated fare receives stronger preference.

If fare data is estimated rather than authoritative, the user-facing interface should communicate that.

---

# 30. LEAST_WALKING

The primary factor is:

```text
total walking distance
```

Routes requiring less walking receive stronger preference.

This is especially relevant for users with a configured maximum walking distance.

---

# 31. FEWEST_TRANSFERS

The primary factor is:

```text
number of transfers
```

A journey with fewer transfers is preferred for this route preference.

A direct journey has:

```text
0 transfers
```

A journey changing from bus to metro has at least:

```text
1 transfer
```

depending on the exact leg structure.

---

# 32. BALANCED

Balanced routing considers multiple factors:

```text
duration
fare
walking
transfers
```

The exact weights must be explicitly defined in code/configuration.

Do not allow arbitrary hidden weights that cannot be explained during a project demonstration.

---

# 33. Ranking Architecture

Conceptual:

```text
Candidate Itineraries
        │
        ▼
Normalize
        │
        ▼
Filter invalid/unusable options
        │
        ▼
Apply hard user constraints
        │
        ▼
Calculate ranking features
        │
        ▼
Apply selected preference
        │
        ▼
Sort candidates
        │
        ▼
Return ranked routes
```

---

# 34. Hard Constraints vs Ranking Preferences

This distinction is important.

## Hard constraint

Example:

```text
avoid_taxi = true
```

A route requiring taxi may be excluded.

## Ranking preference

Example:

```text
route_preference = FASTEST
```

All feasible routes can remain available, but faster routes receive stronger ranking.

---

# 35. Maximum Walking Distance

If:

```text
max_walking_distance_m = 1000
```

then an itinerary requiring substantially more walking can be treated as unsuitable.

The application should define whether the value is:

```text
hard maximum
```

or:

```text
ranking threshold
```

For the initial implementation, a user explicitly setting a maximum should be treated as a hard constraint unless the interface clearly describes it differently.

---

# 36. Avoid Taxi

If:

```text
avoid_taxi = true
```

the Intelligence Layer should exclude candidate itineraries containing taxi legs where alternatives exist.

The system should not replace the taxi leg with a fabricated bus/metro route.

---

# 37. Avoid Transfers

If:

```text
avoid_transfers = true
```

routes with unnecessary transfers can be penalized or excluded according to the final configured rule.

The implementation should distinguish:

```text
hard prohibition
```

from:

```text
strong preference
```

The initial system should use the setting consistently and document the selected behavior.

---

# 38. Ranking Feature Extraction

Each itinerary should expose normalized features:

```text
duration_min
fare
walking_distance_m
transfer_count
mode_count
```

Example:

```text
Route A
duration = 25
fare = 35
walking = 600
transfers = 1

Route B
duration = 31
fare = 20
walking = 300
transfers = 0
```

These values allow different route preferences to be applied.

---

# 39. Normalization for Scoring

Raw values have different scales.

For example:

```text
duration = 25 minutes
fare = ₹35
walking = 600 meters
```

A ranking system should not simply add these raw numbers together.

The Intelligence Layer should normalize relevant features before a composite score is calculated.

Conceptually:

```text
raw features
    ↓
normalization
    ↓
weighted score
    ↓
ranking
```

---

# 40. Composite Ranking Concept

For a balanced preference, a conceptual score can be:

```text
Score =
    W_time      × normalized_time
  + W_fare      × normalized_fare
  + W_walking   × normalized_walking
  + W_transfer  × normalized_transfers
```

Lower cost/score should represent a more desirable candidate if the implementation follows a cost model.

The exact weights must be frozen in implementation/configuration before final evaluation.

---

# 41. Avoiding Ranking Bias

The ranking system should not silently prioritize one transportation mode for all users.

For example:

```text
Metro is not automatically better than bus.
Bus is not automatically better than taxi.
```

Ranking should depend on:

- actual itinerary properties;
- user-selected preference;
- user constraints.

---

# 42. Route Alternatives

The API should return multiple useful alternatives where OTP provides them.

The frontend can display:

```text
Recommended
Fastest
Cheapest
Least Walking
Fewest Transfers
```

These labels should describe the configured ranking/property rather than imply an unsupported claim.

---

# 43. Route Explanation

For each route, the application should provide an understandable summary.

Example:

```text
Walk 400 m to Bus Stop
↓
Take Bus
↓
Get off at Shivajinagar
↓
Walk 250 m to Metro Station
↓
Take Metro to Civil Court
↓
Walk 150 m to destination
```

The explanation should be generated from actual itinerary data.

---

# 44. No Route Hallucination

The Intelligence Layer must never create:

```text
fake bus number
fake station
fake route
fake departure time
fake fare
fake transfer
```

Every displayed transportation fact should originate from:

```text
OTP
configured application data
verified backend calculation
```

or be explicitly marked as estimated/curated.

---

# 45. Map Data Flow

The route geometry should flow through the backend response.

```text
OTP
 ↓
Normalized itinerary
 ↓
Flask API
 ↓
Frontend JavaScript
 ↓
MapLibre
 ↓
Map
```

The map should display the same selected itinerary that the route card describes.

---

# 46. Route Selection

When the user selects a route:

```text
User selects itinerary
       ↓
Frontend identifies route
       ↓
Selected route displayed on map
       ↓
User may save journey
       ↓
Optional ticket purchase
```

The selected route should have a stable application-level identifier for the current response.

---

# 47. Journey Persistence

When a user saves/selects a journey for history:

```text
Selected normalized itinerary
       ↓
Journey Service
       ↓
PostgreSQL journeys
```

Store:

```text
origin
destination
times
duration
walking
fare
route type
OTP itinerary reference
```

Do not store the entire OTP graph.

---

# 48. Route Data Freshness

Transportation information can change.

Therefore, the system should distinguish:

```text
routing result generated now
```

from:

```text
historical journey record
```

A journey history record is a record of what IntelliTransit planned/stored at that time.

It should not automatically be treated as today's live route.

---

# 49. Data Quality Labels

Where useful, route/fare information may include a data-quality classification:

```text
SOURCE
CURATED
ESTIMATED
TEST
```

Example:

```text
Fare: ₹35
Source: ESTIMATED
```

This is preferable to presenting an estimate as an official fare.

---

# 50. Routing Failure Modes

## OTP unavailable

Return:

```text
OTP_UNAVAILABLE
```

Do not fabricate results.

## No route

Return:

```text
NO_ROUTE_FOUND
```

## Invalid coordinates

Return:

```text
VALIDATION_ERROR
```

## Incomplete itinerary

Exclude it from normal presentation or mark it according to implementation.

## Fare unavailable

The journey can still be shown if route information is valid.

Fare should be:

```text
Unavailable
```

rather than invented.

---

# 51. OTP Timeout

If OTP does not respond within the configured timeout:

```text
Cancel/wrap request
 ↓
Log technical failure
 ↓
Return controlled error
```

The frontend should display a user-friendly message.

Do not expose internal timeout configuration or stack traces.

---

# 52. OTP Retry

Automatic retries should be limited.

Do not repeatedly call OTP in a tight loop.

A simple initial strategy is:

```text
Request
 ↓
Short controlled retry if appropriate
 ↓
Failure
```

The exact retry policy can be finalized during implementation/testing.

---

# 53. Routing Performance

The goal is not to create a mathematically optimal global transportation optimizer.

The goal is:

```text
Fast enough
+
Consistent
+
Understandable
+
Correctly sourced
```

The main routing workload remains in OTP.

The Intelligence Layer should remain lightweight.

---

# 54. Caching

Caching is not required for the initial architecture.

Do not introduce Redis or another caching system solely because it is common in production systems.

If repeated identical journey requests become a measurable performance problem, a cache can be considered later.

Any cache must account for:

```text
departure time
transport schedule changes
user preferences
data freshness
```

---

# 55. Personalization

Personalization uses available registered-user data.

Sources:

```text
user_preferences
saved_locations
journeys
```

Examples:

```text
Frequent Home → College journey
Preferred Metro
Avoid Taxi
Maximum walking distance
```

Personalization should adjust route processing/presentation rather than create fictional routes.

---

# 56. AI and Routing Relationship

Gemini is not part of the core route-calculation pipeline.

Correct:

```text
User
 ↓
AI
 ↓
Backend tool
 ↓
Journey Service
 ↓
OTP
 ↓
Intelligence Layer
 ↓
AI explanation
```

Incorrect:

```text
User
 ↓
Gemini
 ↓
Gemini invents route
```

---

# 57. Natural-Language Journey Query

Example:

> “I need the cheapest way from Pune Station to Civil Court.”

AI process:

```text
Understand intent
 ↓
Extract origin
Extract destination
Extract preference = CHEAPEST
 ↓
Call planJourney()
 ↓
OTP
 ↓
Intelligence Layer
 ↓
Return ranked alternatives
 ↓
Gemini explains result
```

The route remains a backend-calculated result.

---

# 58. Contextual Follow-Up

Example:

```text
User:
"Find me a route from A to B."

AI:
"Here are three routes."

User:
"Which one is cheapest?"

```

The conversation layer can retain the relevant route-result context.

It should not require the entire original OTP response to be sent repeatedly if a compact structured context is available.

---

# 59. AI Route Facts

When explaining a route, Gemini should use tool-returned values for:

```text
duration
fare
walking distance
transfers
modes
stops/stations
departure
arrival
```

The AI should not substitute its own remembered transportation information.

---

# 60. Route Ranking Output

A normalized ranking response can conceptually look like:

```json
{
  "route_id": "route-1",
  "rank": 1,
  "score": 0.18,
  "route_type": "MULTIMODAL",
  "duration_min": 25,
  "walking_distance_m": 600,
  "transfers": 1,
  "estimated_fare": 35.0,
  "fare_source": "ESTIMATED",
  "legs": []
}
```

The raw internal score does not necessarily need to be shown to users.

It may be retained for debugging/testing.

---

# 61. Ranking Transparency

The application should be able to explain why a route was presented as recommended.

Example:

```text
Recommended because:
- shortest travel time among feasible routes;
- walking distance below your limit;
- no taxi required.
```

The explanation must be based on actual ranking inputs.

---

# 62. Route Ranking Test Cases

At minimum, test:

### Case 1 — Fastest

```text
Route A = 20 min
Route B = 30 min

FASTEST
→ A ranks higher
```

### Case 2 — Cheapest

```text
Route A = ₹50
Route B = ₹25

CHEAPEST
→ B ranks higher
```

### Case 3 — Least Walking

```text
Route A = 900 m
Route B = 400 m

LEAST_WALKING
→ B ranks higher
```

### Case 4 — Fewest Transfers

```text
Route A = 2 transfers
Route B = 0 transfers

FEWEST_TRANSFERS
→ B ranks higher
```

### Case 5 — Avoid Taxi

```text
Route A = taxi + metro
Route B = bus + metro

avoid_taxi = true
→ A excluded
```

These are implementation tests, not user-facing guarantees.

---

# 63. Ranking Tie-Breakers

When two routes have nearly identical primary scores, a deterministic tie-breaker should be used.

Example:

```text
Primary preference
        ↓
Secondary factor: duration
        ↓
Secondary factor: walking
        ↓
Stable ordering
```

The exact tie-break hierarchy should be documented in implementation.

The important requirement is that ranking should not randomly change between identical requests.

---

# 64. Transportation Mode Presentation

The frontend can use:

```text
WALK
BUS
METRO
TAXI
```

Each leg should identify its mode.

Example:

```text
🚶 Walk
🚌 Bus
🚇 Metro
🚕 Taxi
```

Icons are a frontend presentation concern.

---

# 65. Fare and Route Independence

A route should remain displayable if fare information is unavailable.

Example:

```text
Route found
Fare unavailable
```

is valid.

The system should not turn:

```text
fare unknown
```

into:

```text
fare = ₹0
```

unless ₹0 is actually the configured fare.

---

# 66. Routing Data Source Documentation

The project should maintain a small data-source record documenting:

```text
source name
data type
coverage
last update/check
classification
```

Example:

```text
Pune Metro GTFS
Type: GTFS
Classification: SOURCE

Curated taxi fare configuration
Type: application data
Classification: CURATED
```

This is especially useful for the final project report and viva.

---

# 67. OTP Data Update Principle

When transportation datasets are updated:

```text
New data
 ↓
OTP data/configuration update
 ↓
OTP rebuild/reload as required
 ↓
Routing results use updated network
```

The IntelliTransit application database does not need to replicate the entire dataset.

---

# 68. Intelligence Layer Module Structure

Recommended logical implementation:

```text
services/
├── journey_service.py
├── otp_service.py
├── intelligence_service.py
└── fare_service.py
```

`journey_service.py` orchestrates.

`otp_service.py` communicates with OTP.

`intelligence_service.py` processes/ranks.

`fare_service.py` handles fare logic.

---

# 69. Intelligence Service Pipeline

Conceptually:

```text
def process_itineraries():

    receive OTP itineraries

    normalize

    validate

    apply hard constraints

    calculate fare

    extract ranking features

    apply route preference

    sort

    prepare response
```

This is a conceptual flow, not final production code.

---

# 70. Routing Module Boundary

The routing system should maintain these boundaries:

```text
OTP-specific code
    → otp_service.py

Ranking logic
    → intelligence_service.py

Fare logic
    → fare_service.py

API orchestration
    → journey_service.py

HTTP handling
    → journey_routes.py
```

This separation makes the project easier to debug and demonstrate.

---

# 71. Why IntelliTransit Needs the Intelligence Layer

OTP can calculate candidate journeys.

The project adds an application-level layer that can:

```text
compare candidates
apply user preferences
combine fare information
apply application constraints
rank alternatives
explain route selection
support personalization
```

Therefore, the architecture is:

```text
OTP
+
IntelliTransit Intelligence Layer
=
IntelliTransit journey-planning experience
```

The Intelligence Layer should not be described as replacing OTP.

---

# 72. Core Routing Principle

The most important implementation rule is:

> **Never invent a transportation fact to make a route look complete.**

If the system does not know:

```text
fare
departure time
bus number
station
availability
```

it must report the limitation rather than generate an unsupported value.

---

# 73. Final Routing Pipeline

```text
                 USER REQUEST
                      │
                      ▼
               Request Validation
                      │
                      ▼
                Journey Service
                      │
                      ▼
                  OTP Service
                      │
                      ▼
              OpenTripPlanner 2
                │           │
                ▼           ▼
               OSM         GTFS
                │           │
                └─────┬─────┘
                      ▼
              Candidate Itineraries
                      │
                      ▼
            Normalize + Validate
                      │
                      ▼
              Fare Processing
                      │
                      ▼
             User Constraints
                      │
                      ▼
              Route Ranking
                      │
                      ▼
             Route Explanation
                      │
             ┌────────┴────────┐
             ▼                 ▼
        REST Response       Journey Save
             │                 │
             ▼                 ▼
          Frontend         PostgreSQL
             │
             ▼
          MapLibre
```

---

# 74. Final Routing Rules

1. OTP is the routing engine.
2. OSM provides geographic/street data for the routing environment.
3. GTFS provides structured transit data where available.
4. PostgreSQL does not duplicate the complete transit network.
5. OTP candidate itineraries are normalized before application processing.
6. The Intelligence Layer ranks/processes candidate routes.
7. User preferences affect filtering/ranking.
8. Hard constraints are not silently ignored.
9. Fare processing is separate from route calculation.
10. Missing fare information remains missing/estimated rather than fabricated.
11. Route geometry comes from actual route data.
12. Gemini does not independently calculate routes.
13. AI explanations use backend/tool results.
14. Historical journey records are application records, not live routing truth.
15. External-data quality must be identifiable where relevant.

---

# 75. Relationship to Next Documents

The routing architecture is now defined.

The next document:

`06_FRONTEND_UI_SPECIFICATION.md`

will define how these routing results are presented in the browser, including:

- pages;
- navigation;
- journey planner UI;
- route cards;
- MapLibre integration;
- ticket/pass screens;
- AI chat interface;
- responsive behavior;
- JavaScript module responsibilities.

---

**END OF DOCUMENT**
