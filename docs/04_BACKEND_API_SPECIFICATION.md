# IntelliTransit — Backend API Specification

**Document:** `04_BACKEND_API_SPECIFICATION.md`  
**Project:** IntelliTransit  
**Depends on:** `01_PROJECT_DEFINITION.md`, `02_SYSTEM_ARCHITECTURE.md`, `03_DATABASE_DESIGN.md`  
**Status:** BACKEND API BASELINE — LEG-BASED TICKETING UPDATE

---

# 1. Purpose

This document defines the REST API architecture for the IntelliTransit Flask backend.

It specifies:

- API organization;
- endpoint naming;
- authentication;
- authorization;
- request/response conventions;
- validation;
- journey-planning APIs;
- user APIs;
- ticket/pass APIs;
- payment APIs;
- AI APIs;
- admin APIs;
- validation APIs;
- HTTP status conventions;
- error handling;
- backend responsibility boundaries.

The document defines the contract between the plain JavaScript frontend and the Flask backend.

---

# 2. API Architecture

The backend exposes a REST-style JSON API.

```text
Browser
   │
   │ HTTP/HTTPS + JSON
   ▼
Flask API
   │
   ├── Authentication
   ├── Users
   ├── Preferences
   ├── Saved Locations
   ├── Journeys
   ├── Tickets
   ├── Passes
   ├── Payments
   ├── AI
   ├── Admin
   └── Validation
```

The frontend does not communicate directly with:

- PostgreSQL;
- OpenTripPlanner;
- Gemini;
- Razorpay secret APIs.

All privileged operations pass through Flask.

---

# 3. Base API Path

All application APIs should use:

```text
/api
```

Example:

```text
/api/auth/login
/api/journeys/plan
/api/tickets
/api/payments/create-order
```

Versioning is not required for the initial academic project.

If versioning becomes necessary later, the base can be changed to:

```text
/api/v1
```

without changing the logical service boundaries.

---

# 4. HTTP Methods

Use standard HTTP methods.

| Method | Purpose |
|---|---|
| GET | Retrieve data |
| POST | Create/execute an operation |
| PUT | Replace/update a resource |
| PATCH | Partially update a resource |
| DELETE | Remove a resource where appropriate |

Not every business operation needs to be implemented as CRUD.

For example:

```text
POST /api/journeys/plan
```

is appropriate because route planning is an operation rather than simple database retrieval.

---

# 5. Authentication Model

Authentication:

```text
JWT
```

Password storage:

```text
bcrypt
```

Authentication flow:

```text
POST /api/auth/login
        ↓
Validate credentials
        ↓
Verify bcrypt password hash
        ↓
Generate JWT
        ↓
Return token
```

Protected requests use:

```http
Authorization: Bearer <JWT>
```

The server validates the JWT before executing protected operations.

---

# 6. Authorization Model

Roles:

```text
USER
ADMIN
```

The authenticated user's role is obtained from the validated server-side identity/token.

The backend must not trust:

```json
{
  "role": "ADMIN"
}
```

sent by the browser.

Role-sensitive operations must be protected with backend authorization.

---

# 7. API Response Convention

Successful response:

```json
{
  "success": true,
  "data": {},
  "message": "Request completed successfully"
}
```

Error response:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  }
}
```

For validation errors, additional field information may be included:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "One or more fields are invalid.",
    "fields": {
      "email": "Invalid email address"
    }
  }
}
```

The exact response shape should remain consistent throughout the backend.

---

# 8. HTTP Status Conventions

Use conventional HTTP statuses.

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 204 | Successful request with no response body |
| 400 | Invalid request |
| 401 | Authentication required/invalid |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Semantically invalid input, where appropriate |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 502 | External dependency failure, where appropriate |
| 503 | Service temporarily unavailable |

The backend should not expose stack traces to normal API consumers.

---

# 9. API Module Structure

Recommended Flask route modules:

```text
routes/
├── auth_routes.py
├── journey_routes.py
├── user_routes.py
├── ticket_routes.py
├── pass_routes.py
├── payment_routes.py
├── ai_routes.py
├── admin_routes.py
└── validation_routes.py
```

Service modules:

```text
services/
├── auth_service.py
├── journey_service.py
├── otp_service.py
├── intelligence_service.py
├── fare_service.py
├── ticket_service.py
├── pass_service.py
├── payment_service.py
├── qr_service.py
├── ai_service.py
└── user_service.py
```

Route functions should remain thin.

---

# 10. Authentication Endpoints

## 10.1 Register

```http
POST /api/auth/register
```

Purpose:

Create a new USER account.

Authentication:

```text
Public
```

Request:

```json
{
  "full_name": "Example User",
  "email": "user@example.com",
  "phone": "9876543210",
  "password": "secure-password"
}
```

Backend process:

```text
Validate fields
 ↓
Check email uniqueness
 ↓
Check phone uniqueness if supplied
 ↓
Hash password using bcrypt
 ↓
Create users record
 ↓
Create user_preferences record if required
 ↓
Return result
```

Response:

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "full_name": "Example User",
    "email": "user@example.com",
    "role": "USER"
  },
  "message": "Registration successful."
}
```

Do not return:

```text
password
password_hash
```

---

# 11. Login

```http
POST /api/auth/login
```

Authentication:

```text
Public
```

Request:

```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

Process:

```text
Find user
 ↓
Check active status
 ↓
Verify bcrypt password
 ↓
Generate JWT
 ↓
Return token + basic user identity
```

Response:

```json
{
  "success": true,
  "data": {
    "access_token": "<JWT>",
    "token_type": "Bearer",
    "user": {
      "user_id": "uuid",
      "full_name": "Example User",
      "email": "user@example.com",
      "role": "USER"
    }
  },
  "message": "Login successful."
}
```

---

# 12. Current User

```http
GET /api/auth/me
```

Authentication:

```text
Required
```

Purpose:

Return the currently authenticated user's basic profile.

Response:

```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "full_name": "Example User",
    "email": "user@example.com",
    "phone": "9876543210",
    "role": "USER",
    "is_active": true
  }
}
```

The server obtains the user identity from the JWT.

---

# 13. Logout

JWT logout can be handled initially on the client by removing the stored access token.

```http
POST /api/auth/logout
```

The endpoint may be provided for a consistent application flow, but server-side JWT revocation is not required for the initial implementation unless the chosen JWT strategy needs it.

Frontend behavior:

```text
Logout
 ↓
Remove token
 ↓
Return to public state
```

---

# 14. Journey Planning API

## 14.1 Plan Journey

```http
POST /api/journeys/plan
```

Authentication:

```text
Optional
```

Purpose:

Calculate multimodal journeys between origin and destination.

Request:

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

Backend flow:

```text
Validate origin
Validate destination
Validate coordinates
        ↓
Apply authenticated user's preferences if available
        ↓
Journey Service
        ↓
OTP Service
        ↓
OpenTripPlanner
        ↓
Candidate itineraries
        ↓
Intelligence Layer
        ↓
Fare processing
        ↓
Response normalization
```

Response concept:

```json
{
  "success": true,
  "data": {
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
    "routes": [
      {
        "route_id": "route-1",
        "rank": 1,
        "route_type": "MULTIMODAL",
        "duration_min": 25,
        "walking_distance_m": 600,
        "estimated_fare": 35.00,
        "transfers": 1,
        "legs": []
      }
    ]
  }
}
```

The detailed itinerary/leg structure is represented in the application as journey legs. Ticketable legs are the only legs eligible for ticket purchase.

---

# 15. Journey History

## 15.1 List User Journeys

```http
GET /api/journeys
```

Authentication:

```text
Required
```

Returns the authenticated user's stored journey history.

Query parameters may include:

```text
page
limit
from
to
```

Initial implementation may use:

```text
page
limit
```

only.

Response:

```json
{
  "success": true,
  "data": {
    "journeys": [],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 0
    }
  }
}
```

The server determines `user_id` from the JWT.

---

# 16. Journey Details

```http
GET /api/journeys/<journey_id>
```

Authentication:

```text
Required
```

Rules:

- USER can access their own journey.
- ADMIN may access according to administrative requirements.
- A USER cannot retrieve another user's journey by changing the URL.

---

# 17. Save Journey

A planning request does not necessarily have to create a permanent journey record.

A selected journey may be saved through:

```http
POST /api/journeys
```

Authentication:

```text
Required
```

Request:

```json
{
  "origin_name": "Pune Railway Station",
  "origin_latitude": 18.5285,
  "origin_longitude": 73.8743,
  "destination_name": "Civil Court",
  "destination_latitude": 18.5236,
  "destination_longitude": 73.8500,
  "departure_time": null,
  "arrival_time": null,
  "total_duration_min": 25,
  "walking_distance_m": 600,
  "estimated_fare": 35.00,
  "route_type": "MULTIMODAL",
  "otp_itinerary_id": "otp-reference"
}
```

The backend should not blindly accept arbitrary historical values if they can be derived from a verified planning response.

---

# 18. User Profile Endpoints

## Get Profile

```http
GET /api/users/me
```

Authentication:

```text
Required
```

## Update Profile

```http
PATCH /api/users/me
```

Request example:

```json
{
  "full_name": "Updated Name",
  "phone": "9876543210"
}
```

Password changes should use a dedicated endpoint rather than accepting a new password through a generic profile update.

---

# 19. User Preferences

## Get Preferences

```http
GET /api/users/me/preferences
```

## Update Preferences

```http
PUT /api/users/me/preferences
```

Example:

```json
{
  "preferred_mode": "METRO",
  "route_preference": "LEAST_WALKING",
  "max_walking_distance_m": 1000,
  "avoid_taxi": true,
  "avoid_transfers": false
}
```

The backend validates allowed values.

---

# 20. Saved Locations

## List Saved Locations

```http
GET /api/users/me/saved-locations
```

## Create Saved Location

```http
POST /api/users/me/saved-locations
```

Request:

```json
{
  "label": "College",
  "location_name": "MMCC",
  "address": "Pune",
  "latitude": 18.51,
  "longitude": 73.84
}
```

## Update Saved Location

```http
PATCH /api/users/me/saved-locations/<location_id>
```

## Delete Saved Location

```http
DELETE /api/users/me/saved-locations/<location_id>
```

The backend must verify ownership.

---

# 21. Ticket Endpoints

## List Tickets

```http
GET /api/tickets
```

Authentication:

```text
Required
```

Returns the authenticated user's tickets.

Optional query parameters:

```text
status
page
limit
```

---

# 22. Ticket Details

```http
GET /api/tickets/<ticket_id>
```

Authentication:

```text
Required
```

Ownership must be checked.

---

# 22.1 Ticket Leg Context

Ticket details should expose the purchased journey leg and enough parent-journey context for the UI:

```json
{
  "ticket_id": "uuid",
  "journey_id": "uuid",
  "journey_leg_id": "uuid",
  "origin": "A",
  "destination": "B",
  "mode": "METRO",
  "fare": 30.00,
  "status": "ACTIVE"
}
```

The ticket represents A → B, not automatically the entire A → C journey.

---

# 23. Create Ticket

```http
POST /api/tickets
```

Authentication:

```text
Required
```

Purpose:

Create a pending ticket for one selected **ticketable journey leg** before payment completion. A journey may contain multiple ticketable legs, and each purchased leg has its own ticket and payment.

Request concept:

```json
{
  "journey_id": "uuid",
  "journey_leg_id": "uuid"
}
```

Backend:

```text
Validate journey ownership
 ↓
Validate journey_leg belongs to journey
 ↓
Validate leg is ticketable
 ↓
Determine authoritative fare for the leg
 ↓
Create pending ticket
 ↓
Create one pending payment for that ticket
 ↓
Create Razorpay order
```

A walking/transfer leg with `is_ticketable = false` cannot be purchased as a ticket.

The exact leg-level payment flow is defined further in `07_AI_TICKETING_PAYMENT_SPECIFICATION.md`.

---

# 23.1 Cancel Ticket

```http
POST /api/tickets/<ticket_id>/cancel
```

Authentication:

```text
Required
```

Purpose:

Cancel a purchased ticket at the individual journey-leg level.

Backend flow:

```text
Verify ownership
 ↓
Check ticket status
 ↓
Check cancellation/refund eligibility
 ↓
If eligible, request/record refund through the configured payment flow
 ↓
Mark ticket CANCELLED
 ↓
Record payment REFUNDED when a refund is actually completed
```

A ticket that has already passed its validity start is normally non-refundable under the initial policy. The backend must never promise an external operator refund that IntelliTransit cannot actually execute.

---

# 24. Ticket QR

```http
GET /api/tickets/<ticket_id>/qr
```

Authentication:

```text
Required
```

Purpose:

Return or generate the QR representation for an active ticket.

The backend must verify ticket ownership.

QR generation should be based on the secure ticket token.

---

# 25. Pass Endpoints

## List Passes

```http
GET /api/passes
```

Authentication:

```text
Required
```

## Pass Details

```http
GET /api/passes/<pass_id>
```

Authentication:

```text
Required
```

## Create Pass

```http
POST /api/passes
```

Authentication:

```text
Required
```

Request:

```json
{
  "pass_type": "WEEKLY"
}
```

The backend determines the configured price and validity rules.

The client must not be trusted to supply an arbitrary pass price.

---

# 26. Pass QR

```http
GET /api/passes/<pass_id>/qr
```

Authentication:

```text
Required
```

Only valid/appropriate passes should receive an active QR representation.

---

# 27. Payment APIs

Payment processing is backend-controlled.

## Create Razorpay Order

```http
POST /api/payments/create-order
```

Authentication:

```text
Required
```

Request:

```json
{
  "payment_type": "TICKET",
  "ticket_id": "uuid",
  "reference_id": "ticket-or-business-reference"
}
```

Backend:

```text
Validate business item
 ↓
Calculate authoritative amount
 ↓
Create local payment record
 ↓
Create Razorpay Test Mode order
 ↓
Store Razorpay order ID
 ↓
Return checkout information
```

The frontend must not choose the final amount.

---

# 28. Payment Verification

```http
POST /api/payments/verify
```

Authentication:

```text
Required
```

Request may contain Razorpay's client-returned identifiers/signature data required for server verification.

Conceptually:

```json
{
  "razorpay_order_id": "order_xxx",
  "razorpay_payment_id": "pay_xxx",
  "razorpay_signature": "signature"
}
```

Backend:

```text
Find local payment
 ↓
Verify Razorpay response/signature
 ↓
Confirm amount/order relationship
 ↓
Update payment status
 ↓
Activate corresponding ticket/pass
```

A browser-side success message alone must never activate a ticket.

---

# 29. Payment History

```http
GET /api/payments
```

Authentication:

```text
Required
```

Returns the authenticated user's payment records.

The response should avoid exposing unnecessary third-party payment details.

---

# 30. Razorpay Webhook

If webhook verification is implemented:

```http
POST /api/payments/webhook
```

Authentication:

```text
Razorpay webhook verification
```

The exact webhook implementation depends on the selected Razorpay integration approach.

The webhook must not trust arbitrary requests.

---

# 31. AI Chat API

```http
POST /api/ai/chat
```

Authentication:

```text
Optional
```

Guest users can use basic journey assistance.

Authenticated users can receive context-aware assistance using permitted user data.

Request:

```json
{
  "message": "Find the fastest route from Pune Railway Station to Civil Court.",
  "conversation_id": null
}
```

Response:

```json
{
  "success": true,
  "data": {
    "message": "I found a route from Pune Railway Station to Civil Court...",
    "conversation_id": "conversation-id",
    "actions": []
  }
}
```

The AI service may call backend tools.

---

# 32. AI Tool Execution Boundary

Gemini must not receive direct access to:

```text
PostgreSQL
OpenTripPlanner
Razorpay
```

Instead:

```text
Gemini
   ↓
Tool/function request
   ↓
Flask AI service
   ↓
Approved backend function
   ↓
Actual system/service
   ↓
Tool result
   ↓
Gemini
```

Examples:

```text
plan_journey
get_user_preferences
get_journey_history
get_active_tickets
get_active_passes
```

The exact tool definitions will be finalized in `07_AI_TICKETING_PAYMENT_SPECIFICATION.md`.

---

# 33. Admin API

Admin endpoints must require:

```text
JWT
+
ADMIN role
```

Example endpoint groups:

```text
/api/admin/transport-services
/api/admin/fares
/api/admin/tickets
/api/admin/passes
```

---

# 34. Transport Service Admin APIs

## List Services

```http
GET /api/admin/transport-services
```

## Create Service

```http
POST /api/admin/transport-services
```

## Update Service

```http
PATCH /api/admin/transport-services/<service_id>
```

## Disable/Enable Service

```http
PATCH /api/admin/transport-services/<service_id>/status
```

These operate on IntelliTransit application metadata.

They do not directly modify OTP's underlying network.

---

# 35. Fare Configuration Admin APIs

## List Fare Configurations

```http
GET /api/admin/fares
```

## Create Fare Configuration

```http
POST /api/admin/fares
```

## Update Fare Configuration

```http
PATCH /api/admin/fares/<fare_id>
```

The backend should preserve effective dates and avoid corrupting historical ticket records.

---

# 36. Ticket Validation API

Validation is restricted to authorized validators/admins according to the final access model.

```http
POST /api/validation/tickets
```

Request:

```json
{
  "ticket_token": "secure-token"
}
```

Backend process:

```text
Authenticate validator
 ↓
Read token
 ↓
Find ticket
 ↓
Check token validity
 ↓
Check ticket status
 ↓
Check current time against validity period
 ↓
Create validation record
 ↓
Return result
```

Response:

```json
{
  "success": true,
  "data": {
    "validation_status": "VALID",
    "ticket_id": "uuid",
    "origin": "Pune Railway Station",
    "destination": "Civil Court",
    "validation_time": "timestamp"
  }
}
```

---

# 37. Validation Rules

A ticket may be considered valid only when required conditions are satisfied.

Conceptually:

```text
Ticket exists
AND
Token matches
AND
Status is ACTIVE
AND
Current time >= valid_from
AND
Current time <= valid_until
```

Otherwise return the appropriate state.

The validation result must not be based solely on QR decoding.

The QR provides the identifier; the backend determines validity.

---

# 38. Error Codes

Recommended application-level error codes:

```text
INVALID_REQUEST
VALIDATION_ERROR
UNAUTHORIZED
FORBIDDEN
USER_NOT_FOUND
INVALID_CREDENTIALS
ACCOUNT_INACTIVE
RESOURCE_NOT_FOUND
RESOURCE_CONFLICT

JOURNEY_INVALID
NO_ROUTE_FOUND
OTP_UNAVAILABLE
OTP_ERROR

TICKET_NOT_FOUND
TICKET_NOT_ACTIVE
TICKET_EXPIRED
TICKET_CANCELLED

PASS_NOT_FOUND
PASS_NOT_ACTIVE
PASS_EXPIRED

PAYMENT_NOT_FOUND
PAYMENT_FAILED
PAYMENT_VERIFICATION_FAILED

AI_UNAVAILABLE
AI_REQUEST_INVALID

EXTERNAL_SERVICE_ERROR
INTERNAL_ERROR
```

The exact list can grow during implementation.

---

# 39. Input Validation

Backend validation is mandatory even if frontend validation exists.

Validate:

### Strings

- required/optional;
- length;
- allowed characters where appropriate.

### Email

Use appropriate email-format validation.

### Phone

Validate expected Indian phone format where phone numbers are accepted.

### Coordinates

Latitude:

```text
-90 to +90
```

Longitude:

```text
-180 to +180
```

For IntelliTransit, coordinates should also be checked against the supported Pune operating area when that validation is implemented.

### Numeric values

Reject:

- negative fares;
- negative walking distances;
- invalid pagination;
- impossible IDs.

### Enumerations

Validate:

```text
role
mode
route_preference
status
payment_type
pass_type
```

---

# 40. Authorization Rules

The following ownership rules are mandatory.

## User data

A USER can access:

```text
their own profile
their own preferences
their own saved locations
their own journeys
their own payments
their own tickets
their own passes
```

## Ticket validation

Only authorized validators/admins can perform validation.

## Admin data

Only ADMIN can access administrative configuration APIs.

---

# 41. User ID Security Rule

Never design protected endpoints around a client-supplied user ID such as:

```http
GET /api/users/123/tickets
```

for normal user operations.

Prefer:

```http
GET /api/tickets
```

with:

```text
Authorization: Bearer <JWT>
```

The backend derives the user ID from the authenticated token.

This prevents a user from changing an ID and attempting to access another user's records.

---

# 42. Pagination

List endpoints should support pagination when the dataset can grow.

Recommended parameters:

```text
page=1
limit=20
```

The backend should enforce a maximum limit.

Example:

```text
GET /api/tickets?page=1&limit=20
```

Response:

```json
{
  "success": true,
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 0,
      "pages": 0
    }
  }
}
```

---

# 43. Journey Planning Failure

If OTP is unavailable:

```json
{
  "success": false,
  "error": {
    "code": "OTP_UNAVAILABLE",
    "message": "Journey planning is temporarily unavailable."
  }
}
```

Do not return a fabricated route.

If OTP responds but no itinerary exists:

```json
{
  "success": false,
  "error": {
    "code": "NO_ROUTE_FOUND",
    "message": "No suitable route was found for the selected journey."
  }
}
```

---

# 44. AI Failure

If Gemini is unavailable:

```json
{
  "success": false,
  "error": {
    "code": "AI_UNAVAILABLE",
    "message": "The AI assistant is temporarily unavailable."
  }
}
```

Core route planning must continue to function independently.

The AI is not a dependency for:

```text
route calculation
ticket validation
payment verification
database access
```

---

# 45. External Service Failure

The backend should isolate external failures.

Example:

```text
Razorpay unavailable
       ↓
Payment creation fails
       ↓
No ticket activation
       ↓
Clear user-facing error
```

Example:

```text
Gemini unavailable
       ↓
AI request fails
       ↓
Journey planner remains functional
```

Example:

```text
OTP unavailable
       ↓
Journey planning fails
       ↓
Other account/ticket functions remain available
```

---

# 46. Logging

Backend logs should record useful technical information such as:

```text
timestamp
request method
endpoint
request correlation/reference ID where useful
authenticated user ID where appropriate
service failure
exception category
```

Do not log:

```text
passwords
JWT secrets
Gemini API keys
Razorpay secret keys
payment credentials
unnecessary personal information
```

---

# 47. CORS

If frontend and Flask are served from different origins during development, configure CORS explicitly.

Do not use unrestricted production-style CORS such as:

```text
Allow-Origin: *
```

for authenticated sensitive APIs unless there is a deliberate reason.

Development configuration can be more permissive but should still be controlled.

---

# 48. Request Flow Example

Example:

```text
POST /api/journeys/plan
```

Full backend sequence:

```text
1. Flask receives request
2. Parse JSON
3. Validate request
4. Identify user if JWT exists
5. Load user preferences if applicable
6. Call Journey Service
7. Journey Service calls OTP Service
8. OTP returns candidate itineraries
9. Intelligence Service processes candidates
10. Fare Service calculates/attaches fare information
11. Journey Service builds normalized response
12. Flask returns JSON
```

---

# 49. Route Ranking Example

The API should not ask Gemini:

```text
"Which route is best?"
```

Instead:

```text
OTP
 ↓
Candidate routes
 ↓
Intelligence Layer
 ↓
Application ranking
 ↓
API response
```

Gemini may then explain the already-computed result in natural language.

---

# 50. Ticket Purchase Request Flow

```text
POST /api/tickets
        ↓
Authenticate USER
        ↓
Validate journey ownership
        ↓
Calculate authoritative fare
        ↓
Create ticket PENDING
        ↓
Create payment PENDING
        ↓
Create Razorpay order
        ↓
Return payment information
```

After payment:

```text
POST /api/payments/verify
        ↓
Verify payment
        ↓
SUCCESS?
   ┌────┴────┐
  YES        NO
   │          │
Activate    Keep inactive
ticket      /failed
```

---

# 51. API Security Rules

The backend must:

1. Hash passwords with bcrypt.
2. Verify JWT signatures.
3. Validate JWT expiry.
4. Enforce authorization.
5. Validate all input server-side.
6. Use parameterized database operations/ORM safely.
7. Keep secrets in environment configuration.
8. Never expose database credentials.
9. Never expose third-party secret keys.
10. Never trust client-supplied prices.
11. Never trust client-supplied roles.
12. Never trust client-side payment success alone.
13. Never trust QR data as proof of ticket validity.
14. Avoid exposing internal exception details.

---

# 52. API-to-Database Mapping

| API Area | Primary Tables |
|---|---|
| Authentication | users |
| Profile | users |
| Preferences | user_preferences |
| Saved Locations | saved_locations |
| Journey Planning | journeys |
| Journey History | journeys |
| Transport Admin | transport_services |
| Fare Admin | fare_configurations |
| Payments | payments |
| Tickets | tickets |
| Passes | passes |
| Ticket Validation | ticket_validations |
| AI | backend tools + relevant user/application data |

---

# 53. Backend Responsibility Matrix

| Function | Flask | PostgreSQL | OTP | Intelligence Layer | Gemini | Razorpay |
|---|---:|---:|---:|---:|---:|---:|
| Authentication | ✓ | ✓ | | | | |
| User data | ✓ | ✓ | | | | |
| Route calculation | ✓ | | ✓ | | | |
| Route ranking | ✓ | | | ✓ | | |
| Fare processing | ✓ | ✓ | | ✓ | | |
| Map rendering | | | | | | |
| AI conversation | ✓ | | | | ✓ | |
| Payment processing | ✓ | ✓ | | | | ✓ |
| Ticket lifecycle | ✓ | ✓ | | | | |
| QR generation | ✓ | ✓ | | | | |
| Ticket validation | ✓ | ✓ | | | | |

Map rendering is performed by the frontend using MapLibre GL JS.

---

# 54. Recommended Flask Blueprints

Flask Blueprints can organize route modules:

```text
auth_bp
journey_bp
user_bp
ticket_bp
pass_bp
payment_bp
ai_bp
admin_bp
validation_bp
```

Conceptually:

```python
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(journey_bp, url_prefix="/api/journeys")
```

The exact implementation is left for coding.

---

# 55. Service Layer Rule

A route should generally look conceptually like:

```text
receive request
    ↓
validate input
    ↓
call service
    ↓
return response
```

Avoid putting all business logic directly inside:

```text
@app.route(...)
```

For example, `journey_routes.py` should not contain the full OTP request-building, route ranking, fare calculation, and database logic.

Those responsibilities belong to services.

---

# 56. Database Access Rule

Do not write raw database queries throughout route files.

Prefer:

```text
Route
 ↓
Service
 ↓
Model/repository/database layer
 ↓
PostgreSQL
```

This keeps the API layer readable and makes later testing easier.

---

# 57. API Documentation

During implementation, the team should maintain:

```text
docs/api/
```

for finalized endpoint examples if required.

Postman should be used to test:

- authentication;
- journey APIs;
- user APIs;
- tickets;
- passes;
- payments;
- AI;
- admin;
- validation.

---

# 58. Minimum API Set for Functional Demo

The following endpoints form the minimum complete application path:

```text
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

POST /api/journeys/plan

GET  /api/journeys

GET  /api/users/me/preferences
PUT  /api/users/me/preferences

GET  /api/users/me/saved-locations
POST /api/users/me/saved-locations

POST /api/tickets
GET  /api/tickets
GET  /api/tickets/<ticket_id>
POST /api/tickets/<ticket_id>/cancel

POST /api/passes
GET  /api/passes

POST /api/payments/create-order
POST /api/payments/verify

POST /api/ai/chat

POST /api/validation/tickets
```

Administrative endpoints can then be added around the core application.

---

# 59. API Implementation Order

Backend implementation should proceed approximately in this order:

```text
1. Flask application setup
2. Configuration/environment
3. PostgreSQL connection
4. Models/schema integration
5. Authentication
6. User/preferences
7. Journey service
8. OTP service
9. Intelligence Layer
10. Journey API
11. Saved locations/history
12. Ticket/pass services
13. Payment integration
14. QR generation
15. Validation API
16. AI service
17. Admin APIs
18. Error handling
19. Testing
```

The exact implementation schedule is defined in:

`09_IMPLEMENTATION_PLAN.md`

---

# 60. API Contract Rules

The implementation must preserve these principles:

1. JSON is the primary API format.
2. Authentication uses JWT.
3. Passwords use bcrypt hashes.
4. Protected resources use server-derived user identity.
5. Admin operations require ADMIN authorization.
6. Route planning goes through OTP.
7. Route ranking goes through the IntelliTransit Intelligence Layer.
8. AI does not calculate transportation routes itself.
9. Payment amounts are determined by the backend.
10. Payment success is verified server-side.
11. QR codes identify tickets/passes but do not independently prove validity.
12. PostgreSQL stores application data, not the entire routing graph.
13. External service failures must produce controlled errors.
14. Core route planning must not depend on Gemini.
15. API responses should remain predictable and consistent.

---

# 61. Final Backend Architecture

```text
                         FRONTEND
                            │
                       REST / JSON
                            │
                            ▼
                    ┌───────────────┐
                    │ FLASK ROUTES  │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │   SERVICES    │
                    └───────┬───────┘
                            │
          ┌─────────────────┼──────────────────┐
          │                 │                  │
          ▼                 ▼                  ▼
     PostgreSQL       External Services   Intelligence
                            │                  │
                 ┌──────────┼──────────┐       │
                 │          │          │       │
                 ▼          ▼          ▼       ▼
                OTP       Gemini    Razorpay  Ranking
```

The backend therefore acts as the controlled integration and business-logic layer between the browser, application database, routing engine, AI service, payment provider, and ticketing system.

---

# 62. Relationship to Next Documents

This document defines the API boundary.

Next:

`05_ROUTING_AND_INTELLIGENCE.md`

will define in detail:

- OTP request construction;
- OTP response handling;
- GTFS/OSM relationship;
- itinerary normalization;
- route-leg representation;
- multimodal route processing;
- route ranking;
- preference scoring;
- fare aggregation;
- walking-distance handling;
- transfer handling;
- selected-route persistence.

The routing document must use the API and database boundaries established here.

---

**END OF DOCUMENT**
