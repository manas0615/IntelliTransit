# IntelliTransit — Frontend UI Specification

**Document:** `06_FRONTEND_UI_SPECIFICATION.md`  
**Project:** IntelliTransit  
**Depends on:** `01_PROJECT_DEFINITION.md`, `02_SYSTEM_ARCHITECTURE.md`, `03_DATABASE_DESIGN.md`, `04_BACKEND_API_SPECIFICATION.md`, `05_ROUTING_AND_INTELLIGENCE.md`  
**Status:** FRONTEND UI BASELINE

---

# 1. Purpose

This document defines the browser-based frontend architecture for IntelliTransit.

The frontend is intentionally built using:

- HTML5
- CSS3
- JavaScript ES6+
- MapLibre GL JS

No React, Vite, JSX, or Node.js frontend runtime is required.

The frontend communicates with the Flask backend through REST APIs.

---

# 2. Frontend Responsibility

The frontend is responsible for:

- presenting the user interface;
- collecting user input;
- performing basic client-side validation;
- communicating with Flask APIs;
- displaying journey results;
- rendering maps;
- displaying route alternatives;
- handling login/register state;
- displaying tickets and passes;
- initiating Razorpay checkout;
- displaying QR codes;
- providing the AI chat interface;
- displaying user preferences/history;
- providing administrative screens;
- displaying loading, empty, and error states.

The frontend is not responsible for authoritative business decisions.

---

# 3. Frontend Architecture

```text
                    BROWSER
                       │
        ┌──────────────┴──────────────┐
        │                             │
      HTML                           CSS
        │                             │
        └──────────────┬──────────────┘
                       │
                  JavaScript
                       │
       ┌───────────────┼────────────────┐
       │               │                │
       ▼               ▼                ▼
   Flask REST       MapLibre         Razorpay
      API              GL JS          Checkout
       │
       ▼
  Application Data
```

The browser is the presentation layer.

---

# 4. Design Principles

The UI should be:

- responsive;
- readable;
- simple;
- transportation-focused;
- consistent across pages;
- usable on desktop and mobile browsers;
- clear about loading and error states;
- careful not to present estimates as verified facts.

Avoid unnecessary visual complexity.

The application should prioritize the primary user task:

> Enter where you are and where you want to go.

---

# 5. Recommended Page Structure

The initial frontend contains these logical pages:

```text
index.html
login.html
register.html
planner.html
journey.html
tickets.html
passes.html
history.html
profile.html
ai-assistant.html
admin.html
validator.html
```

Some pages can later be combined if a cleaner implementation is found.

The logical page responsibilities remain the same.

---

# 6. Public vs Authenticated Pages

## Public

```text
Home
Planner
Login
Register
AI Assistant basic access
```

## Registered User

```text
Planner
Journey Results
Tickets
Passes
History
Profile
Preferences
AI Assistant
```

## Admin

```text
Admin Dashboard
Transport Services
Fare Configurations
Ticket/Pass management where authorized
```

## Validator

```text
Ticket Validation
```

---

# 7. Global Navigation

Desktop navigation can contain:

```text
IntelliTransit
│
├── Plan Journey
├── My Journeys
├── Tickets
├── Passes
├── AI Assistant
├── Profile
└── Logout
```

For guest users:

```text
IntelliTransit
│
├── Plan Journey
├── AI Assistant
├── Login
└── Register
```

Admin users can receive an additional:

```text
Admin
```

navigation entry.

---

# 8. Home Page

Purpose:

Introduce the product and immediately expose journey planning.

Primary content:

```text
IntelliTransit
Intelligent Multimodal Transportation and Journey Planning
```

Primary planner:

```text
From
[ Search location ]

To
[ Search destination ]

[ Plan Journey ]
```

Optional quick actions:

```text
Use saved location
Recent journey
AI Assistant
```

The home page should not overwhelm the user with technical details.

---

# 9. Journey Planner Page

This is the core page.

Suggested layout:

```text
┌───────────────────────────────────────────────┐
│ IntelliTransit                               │
├───────────────────────────────────────────────┤
│                                               │
│ From                                          │
│ [ Pune Railway Station                    ]   │
│                                               │
│ To                                            │
│ [ Civil Court                              ]   │
│                                               │
│ Departure                                     │
│ [ Now ▼ ]                                     │
│                                               │
│ Preferences                                   │
│ [ Fastest ▼ ]                                 │
│                                               │
│ [ Plan Journey ]                              │
│                                               │
└───────────────────────────────────────────────┘
```

For authenticated users, saved locations can appear as suggestions.

---

# 10. Origin/Destination Input

Each location input should support:

- typed location;
- selected suggestion;
- saved locations for authenticated users;
- coordinates associated with the selected location.

The frontend should not assume that a text string alone is enough for routing.

The final request should contain:

```text
name
latitude
longitude
```

---

# 11. Location Selection

The location selection system may use:

- configured geocoding/search capability;
- curated location data;
- map selection where implemented.

The architecture must preserve:

```text
human-readable name
+
coordinates
```

before journey planning is requested.

If the frontend cannot obtain valid coordinates, it should not submit a route request.

---

# 12. Swap Origin and Destination

The planner should provide a simple swap action:

```text
[ ⇅ ]
```

Behavior:

```text
Origin ←→ Destination
```

No new backend request is required until the user presses Plan Journey.

---

# 13. Journey Preferences UI

The initial preference controls can include:

```text
Route preference
[ Fastest ▼ ]

Maximum walking distance
[ 1500 m ]

Avoid taxi
[ toggle ]

Avoid transfers
[ toggle ]
```

The interface should use understandable labels.

Internal values such as:

```text
FASTEST
LEAST_WALKING
```

are implementation values, not necessarily user-facing text.

---

# 14. Route Preference Options

User-facing options:

```text
Fastest
Cheapest
Least Walking
Fewest Transfers
Balanced
```

The backend remains responsible for the actual ranking.

The frontend only communicates the selected preference.

---

# 15. Loading State

When the user presses Plan Journey:

```text
Plan Journey
      ↓
Loading state
```

Example:

```text
Finding routes...
```

The interface should prevent accidental repeated submissions while the request is active.

A loading indicator should be visible without blocking the entire browser unnecessarily.

---

# 16. Journey Results Page

The results page should combine:

```text
Route alternatives
+
Map
```

Recommended desktop structure:

```text
┌───────────────────────┬────────────────────────┐
│ ROUTE OPTIONS         │                        │
│                       │                        │
│ Route 1               │                        │
│ 25 min • ₹35          │        MAP             │
│ 600 m walking         │                        │
│ 1 transfer            │                        │
│                       │                        │
│ Route 2               │                        │
│ 31 min • ₹20          │                        │
│ 300 m walking         │                        │
│ 0 transfers           │                        │
│                       │                        │
└───────────────────────┴────────────────────────┘
```

On mobile:

```text
Route cards
   ↓
Map
```

or:

```text
Map
 ↓
Route cards
```

depending on the final responsive layout.

---

# 17. Route Card

Each route card should show:

```text
Route label
Total duration
Estimated fare
Walking distance
Transfer count
Modes used
Departure time
Arrival time
```

Example:

```text
Recommended

25 min
₹35 estimated

🚶 Walk → 🚌 Bus → 🚇 Metro → 🚶 Walk

600 m walking
1 transfer

08:30 → 08:55

[ View Journey ]
```

Do not display unsupported values.

---

# 18. Route Data Labels

Where fare/data quality matters, show:

```text
₹35 estimated
```

rather than:

```text
₹35
```

if the value is an estimate.

The frontend should honor the backend's data-quality indicator.

---

# 19. Route Selection

When a user selects a route:

```text
Route card selected
      ↓
Map updates
      ↓
Detailed journey panel opens
```

Only the selected route should be visually emphasized on the map.

---

# 20. Detailed Journey View

The detailed route view should display the itinerary as a timeline.

Example:

```text
08:30
🚶 Walk 400 m
Pune Railway Station
       │
       ▼
08:36
🚌 Bus
Pune Station → Shivajinagar
       │
       ▼
08:48
🚶 Walk 200 m
Shivajinagar Metro
       │
       ▼
08:50
🚇 Metro
Shivajinagar → Civil Court
       │
       ▼
08:55
🚶 Walk 150 m
Destination
```

The actual content comes from the backend itinerary.

---

# 21. Leg Details

Each journey leg can display:

```text
Mode
Start
End
Departure
Arrival
Duration
Distance
Service/operator if available
Stop/station information if available
```

For example:

```text
METRO

Shivajinagar
→
Civil Court

08:50 – 08:54
4 min
```

Do not invent service numbers or station information.

---

# 22. MapLibre Integration

MapLibre GL JS is responsible for rendering the map.

Frontend responsibilities:

```text
Initialize map
Load configured map style
Add origin marker
Add destination marker
Draw route geometry
Highlight selected route
Display relevant stops/stations
Adjust viewport
```

MapLibre does not calculate the journey.

---

# 23. Map Data Flow

```text
OTP
 ↓
Flask
 ↓
Normalized route geometry
 ↓
JSON response
 ↓
JavaScript map.js
 ↓
MapLibre GL JS
 ↓
Map
```

The browser should not independently calculate a second route that could differ from the journey card.

---

# 24. Map Components

Recommended map module responsibilities:

```text
map.js

initializeMap()
showOrigin()
showDestination()
drawRoute()
clearRoutes()
highlightRoute()
fitToRoute()
addStopMarker()
```

The exact function names may change during implementation.

---

# 25. Map Error State

If map tiles cannot load:

```text
Route information remains available.
```

Example:

```text
Map unavailable

Your route details are still available below.
```

The map should not become a single point of failure for journey information.

---

# 26. Empty Route State

If no route is found:

```text
No suitable route found.

Try:
• a different destination
• a different departure time
• allowing more walking
• allowing additional transportation modes
```

The frontend must not fabricate alternatives.

---

# 27. Error States

The frontend should handle at least:

```text
Network error
Authentication error
No route found
OTP unavailable
AI unavailable
Payment failed
Ticket unavailable
Pass unavailable
Validation failed
Server error
```

Messages should be user-friendly.

Technical error codes can be logged/debugged without necessarily being displayed verbatim.

---

# 28. Authentication UI

## Login

Fields:

```text
Email
Password
```

Actions:

```text
[ Login ]
[ Create account ]
```

## Register

Fields:

```text
Full Name
Email
Phone
Password
Confirm Password
```

Client-side validation should occur before the request.

Backend validation remains authoritative.

---

# 29. Authentication State

The frontend needs a small authentication utility.

Recommended:

```text
auth.js
```

Responsibilities:

```text
saveToken()
getToken()
removeToken()
isAuthenticated()
getCurrentUser()
logout()
```

The implementation should choose an appropriate browser storage strategy.

Security-sensitive token handling must be considered carefully during implementation.

---

# 30. API Utility Module

Recommended:

```text
api.js
```

Responsibilities:

```text
base API URL
GET requests
POST requests
PUT requests
PATCH requests
DELETE requests
Authorization header
JSON parsing
common error handling
```

Example conceptual call:

```text
api.post("/journeys/plan", requestData)
```

The exact implementation is decided during coding.

---

# 31. Profile Page

The profile page should show:

```text
Name
Email
Phone
Role
Account status
```

Actions:

```text
Edit Profile
Preferences
Logout
```

Do not display:

```text
password hash
JWT
secret keys
payment credentials
```

---

# 32. Preferences Page

Show controls for:

```text
Preferred mode
Route preference
Maximum walking distance
Avoid taxi
Avoid transfers
```

Example:

```text
Journey Preferences

Preferred mode:
[ Metro ▼ ]

Route preference:
[ Fastest ▼ ]

Maximum walking:
[ 1000 m ]

Avoid taxi:
[ ON ]

Avoid transfers:
[ OFF ]

[ Save Preferences ]
```

---

# 33. Saved Locations

The UI should allow:

```text
Add location
Edit location
Delete location
```

Example:

```text
Saved Locations

🏠 Home
MMCC

🎓 College
Marathwada Mitra Mandal's College of Commerce

[ + Add Location ]
```

Selecting a saved location can populate the journey planner.

---

# 34. Journey History Page

Display:

```text
Recent journeys
```

Each entry:

```text
Pune Railway Station
→
Civil Court

25 min
₹35 estimated
Date/time
```

Actions:

```text
View
Plan Again
```

“Plan Again” should create a new current journey-planning request rather than blindly treating historical data as current routing truth.

---

# 35. Ticket Page

The ticket page should show:

```text
Ticket status
Origin
Destination
Fare
Valid from
Valid until
QR code
```

Example:

```text
ACTIVE

Pune Railway Station
↓
Civil Court

₹35

Valid:
08:30 – 10:00

[ QR CODE ]
```

---

# 36. Ticket Status Presentation

Use clear status labels:

```text
Pending
Active
Used
Expired
Cancelled
```

The status comes from the backend.

The frontend must not locally change an active ticket to “used” without backend validation.

---

# 37. Pass Page

Pass display:

```text
WEEKLY PASS

Status: ACTIVE

Valid:
01 Sep 2026
→
07 Sep 2026

Price:
₹XXX

[ QR CODE ]
```

The actual price comes from the backend.

---

# 38. Purchase Flow UI

For a ticket:

```text
Select journey
 ↓
Review ticket
 ↓
Show fare
 ↓
[ Pay ]
 ↓
Razorpay checkout
 ↓
Backend verification
 ↓
Ticket active
 ↓
QR shown
```

The frontend should not declare payment success before backend confirmation.

---

# 39. Razorpay Checkout

The frontend can open the configured Razorpay checkout interface after receiving the appropriate order information from Flask.

Conceptually:

```text
Frontend
 ↓
POST /api/payments/create-order
 ↓
Flask
 ↓
Razorpay order
 ↓
Frontend receives order details
 ↓
Razorpay checkout
```

The secret Razorpay key remains server-side.

---

# 40. Payment Failure UI

If payment fails:

```text
Payment was not completed.

Your ticket has not been activated.
```

Actions:

```text
[ Try Again ]
[ Back to Journey ]
```

Do not display a ticket as active merely because checkout was opened.

---

# 41. QR Display

QR code should be visually prominent.

Example:

```text
┌─────────────────────┐
│                     │
│       QR CODE       │
│                     │
└─────────────────────┘

Ticket ID: •••••123
Status: ACTIVE
```

Avoid exposing the entire internal secure token as normal visible text unless required for debugging.

---

# 42. AI Assistant Page

The AI assistant should use a simple conversational layout.

```text
┌─────────────────────────────────────────────┐
│ IntelliTransit AI                           │
├─────────────────────────────────────────────┤
│                                             │
│ User: Find the fastest route to Civil Court │
│                                             │
│ AI: I found three routes...                 │
│                                             │
│ [ Type your message...                 ]    │
│                              [ Send ]       │
└─────────────────────────────────────────────┘
```

---

# 43. AI Suggested Actions

Where useful, AI responses can contain structured actions.

Example:

```text
I found a 25-minute route using bus + metro.

[ View Route ]
```

The action should link to actual application state rather than generate an independent route.

---

# 44. AI Context

For authenticated users, the AI may use:

```text
saved locations
preferences
recent journeys
active tickets/passes
```

only through authorized backend functions.

The frontend does not send arbitrary private database records directly to Gemini.

---

# 45. AI Error State

If AI is unavailable:

```text
The AI assistant is temporarily unavailable.

You can still use the normal journey planner.
```

The normal planner remains usable.

---

# 46. Admin Dashboard

The admin dashboard should remain functional and simple.

Possible sections:

```text
Dashboard
Transport Services
Fare Configurations
Tickets
Passes
Validation
```

Only authorized ADMIN users can access admin APIs.

---

# 47. Transport Services Admin UI

Display:

```text
Service
Mode
Operator
Status
```

Actions:

```text
Add
Edit
Enable/Disable
```

Example:

```text
Pune Metro
METRO
Pune Metro
ACTIVE
```

---

# 48. Fare Configuration Admin UI

Display:

```text
Service
Fare type
Base fare
Per-km rate
Minimum fare
Effective from
Effective until
Status
```

Actions:

```text
Add
Edit
Enable/Disable
```

Historical ticket prices must not be changed retroactively.

---

# 49. Validator Interface

The validator page should prioritize speed.

```text
Ticket Validation

[ Enter/Scan QR Token ]

[ Validate ]
```

Result:

```text
✓ VALID

Pune Railway Station
→
Civil Court

Active
Valid until 10:00
```

or:

```text
✕ INVALID / EXPIRED
```

The result comes from the backend.

---

# 50. Responsive Design

The application must support:

```text
Desktop
Tablet
Mobile browser
```

The frontend should not require a native mobile app.

---

# 51. Desktop Layout

For wide screens:

```text
Navigation
──────────────────────────

Planner / Route List | Map
```

Journey results can use a two-column layout.

---

# 52. Mobile Layout

For smaller screens:

```text
Navigation
↓
Planner
↓
Route summary
↓
Map
↓
Detailed itinerary
```

Controls should remain touch-friendly.

Avoid very small buttons.

---

# 53. CSS Architecture

Recommended:

```text
css/
├── main.css
├── layout.css
├── components.css
├── forms.css
├── map.css
└── responsive.css
```

Responsibilities:

### main.css

Global:

```text
body
typography
variables
base elements
```

### layout.css

```text
containers
grids
navigation
sections
```

### components.css

```text
cards
buttons
badges
modals
alerts
```

### forms.css

```text
inputs
selects
validation
form layouts
```

### map.css

```text
map container
map controls
route panels
```

### responsive.css

```text
mobile/tablet breakpoints
```

---

# 54. JavaScript Architecture

Recommended modules:

```text
js/
├── api.js
├── auth.js
├── planner.js
├── journey.js
├── map.js
├── tickets.js
├── passes.js
├── payment.js
├── ai.js
├── profile.js
├── admin.js
├── validator.js
└── utils.js
```

---

# 55. `planner.js`

Responsibilities:

```text
read origin
read destination
read preferences
validate input
call journey API
handle loading
handle errors
redirect/display results
```

---

# 56. `journey.js`

Responsibilities:

```text
render route cards
render itinerary
select route
display fare
display walking distance
display transfers
display mode sequence
trigger map selection
save journey
start ticket purchase
```

---

# 57. `map.js`

Responsibilities:

```text
initialize MapLibre
draw routes
highlight selected route
show markers
fit bounds
clear map
```

It should not call OTP directly.

---

# 58. `tickets.js`

Responsibilities:

```text
load tickets
render ticket list
load ticket details
request QR
show ticket status
```

---

# 59. `passes.js`

Responsibilities:

```text
load passes
display pass details
start pass purchase
display QR
```

---

# 60. `payment.js`

Responsibilities:

```text
create backend order
open Razorpay checkout
handle checkout result
send verification request
display verified payment state
```

The module must not independently mark a payment as successful.

---

# 61. `ai.js`

Responsibilities:

```text
send chat messages
render responses
show loading state
display structured actions
handle AI errors
```

It does not directly call Gemini.

It calls:

```text
/api/ai/chat
```

---

# 62. `admin.js`

Responsibilities:

```text
load admin data
render services
edit service
render fare configurations
edit fare configuration
handle admin API errors
```

The backend remains responsible for authorization.

---

# 63. `validator.js`

Responsibilities:

```text
read QR/token
send validation request
display result
show ticket summary
```

The frontend does not determine ticket validity.

---

# 64. `utils.js`

Potential shared utilities:

```text
formatCurrency()
formatDate()
formatTime()
escapeHTML()
showToast()
showError()
showLoading()
debounce()
```

The exact functions may evolve during implementation.

---

# 65. API Security from Frontend

The frontend must assume:

```text
Everything sent by the browser can be modified by the user.
```

Therefore:

```text
Frontend validation
       ↓
UX improvement

Backend validation
       ↓
Security + correctness
```

Do not rely on JavaScript validation for security.

---

# 66. Token Handling

The chosen JWT storage strategy should minimize unnecessary exposure to browser-side attacks.

The implementation must consider:

- XSS;
- token lifetime;
- logout behavior;
- accidental token leakage;
- HTTPS deployment.

The final storage approach should be documented before implementation.

---

# 67. HTML Security

When displaying dynamic content:

```text
User names
Location names
AI messages
Route descriptions
```

the frontend must avoid unsafe HTML injection.

Prefer:

```text
textContent
```

or safe DOM APIs for untrusted strings.

---

# 68. Accessibility

The UI should include:

- labels for form inputs;
- readable contrast;
- keyboard-accessible controls;
- meaningful button text;
- alternative text for important images;
- logical heading hierarchy;
- visible focus states.

The map should not be the only way to understand a journey.

---

# 69. Loading and Empty States

Every data-driven page should have a state for:

```text
Loading
Success
Empty
Error
```

Examples:

### Tickets

```text
Loading tickets...
```

```text
No tickets yet.
```

### Journey history

```text
No previous journeys.
```

### AI

```text
Thinking...
```

### Admin

```text
No fare configurations found.
```

---

# 70. Notifications

Use consistent notifications for:

```text
Success
Warning
Error
Information
```

Examples:

```text
Preferences saved.
Ticket activated.
Payment failed.
No route found.
```

Avoid excessive notifications.

---

# 71. Navigation Protection

Authenticated pages should verify login state before displaying protected data.

If the user is not authenticated:

```text
Protected page
 ↓
Redirect to login
```

However, backend authorization remains mandatory.

---

# 72. Admin Page Protection

If a normal USER attempts to access the admin page:

```text
Frontend may redirect
+
Backend returns 403 if API is called
```

The frontend must never rely only on hiding the navigation item.

---

# 73. Guest Journey Planning

Guest journey planning should work without login.

Flow:

```text
Guest
 ↓
Planner
 ↓
Route results
 ↓
Map
```

If the guest selects:

```text
Save Journey
Buy Ticket
Save Location
```

the application can request authentication.

Example:

```text
Login required to save this journey.
```

---

# 74. Journey-to-Ticket UI Flow

```text
Planner
 ↓
Route results
 ↓
Select route
 ↓
Journey details
 ↓
[ Buy Ticket ]
 ↓
Ticket review
 ↓
[ Pay ]
 ↓
Razorpay
 ↓
Backend verification
 ↓
Ticket page
 ↓
QR
```

---

# 75. Journey-to-AI Flow

```text
Planner
 ↓
AI Assistant
 ↓
Natural-language request
 ↓
Backend
 ↓
Actual journey planning
 ↓
AI explanation
 ↓
[ View Route ]
 ↓
Journey results
```

The user should be able to move naturally from AI assistance to the standard planner.

---

# 76. Frontend Failure Isolation

The frontend should isolate failures.

Examples:

```text
Map failure
    ↓
Route cards still usable

AI failure
    ↓
Normal planner still usable

Payment failure
    ↓
Journey information still available

History failure
    ↓
Current journey planner still usable
```

---

# 77. Performance Principles

The frontend should:

- avoid unnecessary API calls;
- debounce location search where applicable;
- prevent repeated route submissions;
- lazy-load nonessential pages/modules where useful;
- avoid rendering huge DOM trees;
- keep map layers manageable;
- show loading feedback.

No frontend framework is required to achieve the initial performance goals.

---

# 78. Frontend Data Ownership

Frontend state should contain only what is required for presentation and interaction.

Example:

```text
selected route
current form values
UI loading state
authentication state
current page state
```

Persistent authoritative business state remains in Flask/PostgreSQL.

---

# 79. Frontend Does Not Calculate Fare

The browser should display:

```text
fare received from backend
```

It should not independently calculate:

```text
ticket price
pass price
payment amount
```

This prevents client-side manipulation.

---

# 80. Frontend Does Not Validate Tickets

The browser can:

```text
scan/read QR
send token
display result
```

The backend determines:

```text
VALID
INVALID
EXPIRED
CANCELLED
```

---

# 81. Frontend Does Not Calculate Routes

The frontend can:

```text
collect coordinates
send request
display route
```

It must not become a second routing engine.

---

# 82. UI Data Source Rules

Display priority:

```text
Backend result
    ↓
Configured application data
    ↓
Explicitly labeled estimate
```

Do not fill missing values with guesses.

For example:

```text
Fare unavailable
```

is preferable to:

```text
₹20
```

without a source.

---

# 83. Core User Journey

The primary user journey should remain short:

```text
Open IntelliTransit
       ↓
Enter From
       ↓
Enter To
       ↓
Choose preference
       ↓
Plan Journey
       ↓
Compare routes
       ↓
Select route
       ↓
View map + steps
```

For registered users:

```text
       ↓
Save journey / buy ticket
```

---

# 84. UI Implementation Priority

Build in this order:

```text
1. Global layout/navigation
2. Home/planner
3. API utility
4. Journey results
5. MapLibre
6. Detailed itinerary
7. Login/register
8. User profile/preferences
9. Journey history
10. Tickets
11. Passes
12. Razorpay checkout
13. QR display
14. AI assistant
15. Admin
16. Validator
17. Responsive refinement
18. Accessibility refinement
```

---

# 85. Frontend Acceptance Criteria

The frontend is considered functionally complete when:

### Planner

- origin can be entered;
- destination can be entered;
- preferences can be selected;
- journey request can be submitted;
- loading state works;
- errors are displayed.

### Results

- multiple routes can be displayed;
- duration is displayed;
- fare is displayed;
- walking distance is displayed;
- transfers are displayed;
- route legs are displayed;
- selected route appears on map.

### Authentication

- registration works;
- login works;
- logout works;
- protected pages behave correctly.

### User

- preferences work;
- saved locations work;
- journey history works.

### Ticketing

- ticket purchase flow can be started;
- payment state is displayed correctly;
- QR is displayed for active tickets.

### AI

- user can send a message;
- backend response is displayed;
- tool-backed route responses can be opened.

### Admin/Validation

- authorized admin interface works;
- ticket validation result is displayed.

---

# 86. Frontend Architecture Summary

```text
                    INTELLITRANSIT UI
                           │
          ┌────────────────┼────────────────┐
          │                │                │
         HTML             CSS          JavaScript
                                           │
                    ┌──────────────────────┼───────────────────┐
                    │                      │                   │
                  Flask                 MapLibre           Razorpay
                   API                    GL JS              Checkout
                    │
       ┌────────────┼─────────────┐
       │            │             │
    Journey       User         Ticket/Pass
       │            │             │
       └────────────┼─────────────┘
                    │
                  AI API
```

The browser remains a thin presentation and interaction layer.

---

# 87. Final Frontend Rules

1. Use HTML5, CSS3, and JavaScript ES6+.
2. Do not introduce React/Vite unless architecture is explicitly changed.
3. Use MapLibre GL JS for map rendering.
4. Communicate with Flask through REST APIs.
5. Never expose backend secrets.
6. Never calculate authoritative fares in the browser.
7. Never calculate authoritative routes in the browser.
8. Never determine ticket validity in the browser.
9. Display estimates as estimates.
10. Provide loading, empty, and error states.
11. Keep guest journey planning available.
12. Protect authenticated and admin screens.
13. Keep the map synchronized with the selected backend route.
14. Make the interface responsive.
15. Keep accessibility in scope.
16. Do not allow AI output to bypass the normal backend architecture.

---

# 88. Relationship to Next Documents

The next document:

`07_AI_TICKETING_PAYMENT_SPECIFICATION.md`

will define in detail:

- Gemini 2.5 Flash integration;
- function/tool calling;
- AI context;
- AI guardrails;
- ticket lifecycle;
- pass lifecycle;
- QR generation;
- Razorpay Test Mode;
- payment verification;
- ticket/pass activation.

This frontend specification provides the UI boundaries that those services must support.

---

**END OF DOCUMENT**
