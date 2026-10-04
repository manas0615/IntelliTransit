# IntelliTransit — REST API Reference Specification

**Base URL:** `http://localhost:5000/api`  
**Authentication Scheme:** `Bearer <JWT_TOKEN>` (issued by `/api/auth/login`)  
**Standard Response Envelope:**  
All endpoints return JSON. Successful responses contain `{"status": "success", "data": ...}`. Error responses contain `{"status": "error", "error": {"code": "...", "message": "..."}}`.

---

## 1. System & Health

### 1.1 Health Check & Subsystem Status
- **Method:** `GET`
- **Path:** `/health`
- **Auth:** None
- **Query Parameters:** None
- **Success Response (200):**
```json
{
  "status": "healthy",
  "database": "connected",
  "otp": "ONLINE",
  "timestamp": "2026-10-04T09:15:00.000Z",
  "version": "1.0.0"
}
```
- **Example cURL:**
```bash
curl -X GET http://localhost:5000/api/health
```

---

## 2. Authentication & Identity (`/api/auth`)

### 2.1 User Registration
- **Method:** `POST`
- **Path:** `/auth/register`
- **Auth:** None
- **Request Body:**
```json
{
  "full_name": "Rahul Sharma",
  "email": "rahul@example.com",
  "phone": "9876543210",
  "password": "SecurePassword123!"
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "data": {
    "user_id": "8f39b672-...",
    "email": "rahul@example.com",
    "role": "USER",
    "token": "eyJhbGciOiJIUzI1Ni..."
  }
}
```
- **Error Codes:** `VALIDATION_ERROR` (400), `EMAIL_ALREADY_EXISTS` (409).

### 2.2 User Login
- **Method:** `POST`
- **Path:** `/auth/login`
- **Auth:** None
- **Request Body:**
```json
{
  "email": "rahul@example.com",
  "password": "SecurePassword123!"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "user_id": "8f39b672-...",
    "full_name": "Rahul Sharma",
    "email": "rahul@example.com",
    "role": "USER",
    "token": "eyJhbGciOiJIUzI1Ni..."
  }
}
```
- **Error Codes:** `INVALID_CREDENTIALS` (401).

### 2.3 Current Session Profile
- **Method:** `GET`
- **Path:** `/auth/me`
- **Auth:** Commuter (`USER`) or Administrator (`ADMIN`)
- **Headers:** `Authorization: Bearer <token>`
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "user_id": "8f39b672-...",
    "full_name": "Rahul Sharma",
    "email": "rahul@example.com",
    "phone": "9876543210",
    "role": "USER"
  }
}
```

---

## 3. User Preferences & Bookmarks (`/api/users`)

### 3.1 Get Preferences
- **Method:** `GET`
- **Path:** `/users/preferences`
- **Auth:** `USER` / `ADMIN`
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "preferred_mode": "METRO",
    "route_preference": "BALANCED",
    "max_walking_distance_m": 1200,
    "avoid_taxi": false,
    "avoid_transfers": false
  }
}
```

### 3.2 Update Preferences
- **Method:** `PUT`
- **Path:** `/users/preferences`
- **Auth:** `USER` / `ADMIN`
- **Request Body:**
```json
{
  "preferred_mode": "BUS",
  "route_preference": "CHEAPEST",
  "max_walking_distance_m": 1500
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": { "message": "Preferences updated successfully" }
}
```

### 3.3 Saved Locations List & Creation
- **Method:** `GET` | `POST`
- **Path:** `/users/saved-locations`
- **Auth:** `USER` / `ADMIN`
- **POST Request Body:**
```json
{
  "label": "Home",
  "location_name": "Kothrud Depot",
  "latitude": 18.5074,
  "longitude": 73.8077
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "data": { "location_id": "...", "label": "Home" }
}
```
- **Error Codes:** `LIMIT_EXCEEDED` (400 if user reaches 20 saved locations).

---

## 4. Journey Planning & Multimodal Routing (`/api/journeys`)

### 4.1 Plan Multimodal Journey
- **Method:** `POST`
- **Path:** `/journeys/plan`
- **Auth:** Optional (Available to Guests and Authenticated Users)
- **Request Body:**
```json
{
  "origin_latitude": 18.5204,
  "origin_longitude": 73.8567,
  "destination_latitude": 18.5074,
  "destination_longitude": 73.8077,
  "origin_name": "Pune Railway Station",
  "destination_name": "Kothrud Depot",
  "route_preference": "BALANCED"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "routing_source": "OTP",
    "itineraries": [
      {
        "itinerary_id": "itin-0",
        "ranking_profile": "BALANCED",
        "total_duration_min": 28,
        "walking_distance_m": 350,
        "estimated_fare": 25.00,
        "legs": [
          {
            "sequence_number": 1,
            "mode": "WALK",
            "from_name": "Pune Railway Station",
            "to_name": "Pune Station Metro",
            "duration_min": 4,
            "walking_distance_m": 250,
            "estimated_fare": 0.00,
            "is_ticketable": false,
            "polyline": "..."
          },
          {
            "sequence_number": 2,
            "mode": "METRO",
            "service_name": "Line 2 Aqua",
            "from_name": "Pune Station Metro",
            "to_name": "Garware College",
            "duration_min": 14,
            "estimated_fare": 20.00,
            "is_ticketable": true,
            "polyline": "..."
          }
        ],
        "explanation": "Balanced route combining short walking with Metro Aqua Line."
      }
    ]
  }
}
```
- **Error Codes:** `OUT_OF_BOUNDS` (400 if coordinates fall outside PMRDA boundary).

### 4.2 Journey History
- **Method:** `GET`
- **Path:** `/journeys/history`
- **Auth:** `USER` / `ADMIN`
- **Success Response (200):** Array of previously saved user journeys and legs.

---

## 5. Ticketing & Passes (`/api/tickets`, `/api/passes`)

### 5.1 Book Leg-Based Ticket
- **Method:** `POST`
- **Path:** `/tickets/book`
- **Auth:** `USER` / `ADMIN`
- **Request Body:**
```json
{
  "journey_id": "...",
  "journey_leg_id": "..."
}
```
- **Success Response (201):**
```json
{
  "status": "success",
  "data": {
    "ticket_id": "...",
    "ticket_token": "TKT-...",
    "fare": 20.00,
    "status": "PENDING",
    "origin": "Pune Station Metro",
    "destination": "Garware College"
  }
}
```
- **Error Codes:** `WALK_LEG_NOT_TICKETABLE` (400 if commuter attempts booking a walk leg).

### 5.2 Get Ticket QR Code
- **Method:** `GET`
- **Path:** `/tickets/<ticket_id>/qr`
- **Auth:** `USER` / `ADMIN`
- **Response:** Scannable PNG Image or Base64 data representation.

### 5.3 Purchase Transit Pass
- **Method:** `POST`
- **Path:** `/passes/create`
- **Auth:** `USER` / `ADMIN`
- **Request Body:**
```json
{
  "pass_type": "DAILY"
}
```
- **Success Response (201):** Pass created with status `PENDING`, price ₹50.00.

---

## 6. Simulated Payment System (`/api/payments`)

### 6.1 Create Payment Order
- **Method:** `POST`
- **Path:** `/payments/create-order`
- **Auth:** `USER` / `ADMIN`
- **Request Body:**
```json
{
  "payment_type": "TICKET",
  "item_id": "<ticket_id>"
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "payment_id": "...",
    "amount": 20.00,
    "currency": "INR",
    "payment_method": "SIMULATED",
    "transaction_reference": "SIM-PAY-TKT-179110...",
    "status": "PENDING"
  }
}
```

### 6.2 Simulate Confirm Payment
- **Method:** `POST`
- **Path:** `/payments/simulate-confirm`
- **Auth:** `USER` / `ADMIN`
- **Request Body:**
```json
{
  "payment_id": "...",
  "transaction_reference": "SIM-PAY-TKT-179110..."
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "payment_id": "...",
    "status": "SUCCESS",
    "item_status": "ACTIVE",
    "message": "Simulated payment processed successfully"
  }
}
```
- **Error Codes:** `ALREADY_PAID` (400 on duplicate submission), `UNAUTHORIZED` (403 for cross-user payment).

---

## 7. Turnstile & Conductor Validation (`/api/validation`)

### 7.1 Inspect & Validate Scanned Token
- **Method:** `POST`
- **Path:** `/validation/scan`
- **Auth:** None / Commuter / Admin (Conductor Portal)
- **Request Body:**
```json
{
  "token": "TKT-A89F-...",
  "service_id": "..."
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "validation_status": "VALID",
    "ticket_id": "...",
    "origin": "Pune Station Metro",
    "destination": "Garware College",
    "timestamp": "2026-10-04T09:20:00.000Z",
    "message": "Valid ticket. Commuter allowed to board."
  }
}
```
- **Error Response (200 / 400):** Returns `validation_status: "INVALID"` or `"EXPIRED"` with detailed reason (e.g., "Ticket has already been used").

---

## 8. Conversational Transit AI (`/api/ai`)

### 8.1 Conversational Chat Companion
- **Method:** `POST`
- **Path:** `/ai/chat`
- **Auth:** Optional
- **Request Body:**
```json
{
  "message": "How do I travel from Shivajinagar to Swargate?",
  "history": []
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "reply": "You can take the Pune Metro Line 1 (Purple) directly from Shivajinagar to Swargate in approximately 12 minutes for ₹20.00.",
    "tools_executed": ["find_transit_routes"]
  }
}
```

---

## 9. Administrator Portal (`/api/admin`)

### 9.1 Platform KPIs & Metrics
- **Method:** `GET`
- **Path:** `/admin/metrics`
- **Auth:** `ADMIN`
- **Success Response (200):**
```json
{
  "status": "success",
  "data": {
    "total_users": 142,
    "total_journeys_planned": 583,
    "active_tickets": 28,
    "simulated_revenue_inr": 4820.00,
    "otp_status": "ONLINE"
  }
}
```
- **Error Codes:** `FORBIDDEN` (403 if commuter token is supplied).

### 9.2 Update Dynamic Fare Configuration
- **Method:** `PUT`
- **Path:** `/admin/fares/<fare_id>`
- **Auth:** `ADMIN`
- **Request Body:**
```json
{
  "base_fare": 6.00,
  "per_km_rate": 2.50
}
```
- **Success Response (200):**
```json
{
  "status": "success",
  "data": { "message": "Fare configuration updated" }
}
```
