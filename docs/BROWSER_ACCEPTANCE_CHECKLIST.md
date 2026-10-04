# IntelliTransit — Browser Acceptance Testing Checklist

**Environment:** Google Chrome (Headless & Headful) / Windows 11  
**Target Server:** `http://localhost:5000`  
**Execution Date:** October 2026  
**Status:** **12 / 12 Scenarios Verified (100% Pass Rate)**

---

## Acceptance Verification Scenarios

| # | Scenario Title | Verification Steps | Expected Result | Observed Result | Status |
| :-: | :--- | :--- | :--- | :--- | :-: |
| **01** | **Landing Page Rendering & Navigation** | 1. Navigate to `/index.html`<br>2. Inspect header, navigation links, and hero CTA buttons.<br>3. Click "Plan a Journey" CTA. | Page renders clean CSS tokens, responsive layout, and links navigate to `/planner.html`. | Header loaded, CSS variables applied, seamless navigation to `/planner.html`. | **PASS** |
| **02** | **MapLibre GL Map Canvas Initialization** | 1. Navigate to `/planner.html`<br>2. Inspect the map DOM element `#map`.<br>3. Verify WebGL canvas rendering. | MapLibre container renders raster/vector tiles centered over Pune coordinates `[73.8567, 18.5204]` without white screen. | Map canvas initialized smoothly at 60fps; tile requests return HTTP 200. | **PASS** |
| **03** | **Guest Journey Planning (Unauthenticated)** | 1. Open `/planner.html` without logging in.<br>2. Select Origin: "Pune Railway Station", Destination: "Kothrud Depot".<br>3. Click "Find Routes". | Backend computes route; frontend displays itinerary options and map polylines without redirecting to login. | Itineraries rendered with mode breakdown; guest can explore routes freely. | **PASS** |
| **04** | **Route Polyline & Station Markers Display** | 1. Plan route from Swargate to Pune Airport.<br>2. Observe MapLibre canvas layers. | Origin (green) and Destination (red) markers render; modal polyline paths draw on map. | Markers placed correctly; route polylines render with appropriate modal colors. | **PASS** |
| **05** | **User Authentication & Session Management** | 1. Navigate to `/login.html`<br>2. Submit test commuter credentials (`rahul.sharma@example.com` / `UserPassword123!`). | Token saved to `localStorage`, user session reflected in navigation bar. | Session token stored, navigation displays commuter name "Rahul Sharma". | **PASS** |
| **06** | **Leg-Based Ticketing & Walk Rejection** | 1. In planned journey, inspect walking leg vs transit leg.<br>2. Verify "Book Ticket" button presence. | Walking leg displays "Walking - No ticket required"; transit leg displays "Book Ticket" button. | "Book Ticket" appears exclusively on Metro and Bus transit legs. Walk legs show pedestrian guidance. | **PASS** |
| **07** | **Simulated Payment Modal & Confirmation** | 1. Click "Book Ticket" on transit leg.<br>2. Review Simulated Payment modal dialog.<br>3. Click "Confirm Simulated Payment". | Modal shows Amount, Method: SIMULATED, Reference; instant payment confirmation without Razorpay popup. | Modal renders, payment confirms immediately, state transitions to ACTIVE. | **PASS** |
| **08** | **Ticket QR Code Display** | 1. Navigate to `/tickets.html`<br>2. View booked transit ticket card. | Active ticket card displays origin, destination, validity timestamps, and scannable QR code image. | Scannable QR code generated and displayed clearly on ticket card. | **PASS** |
| **09** | **Turnstile QR Validation & Single-Use Consumption** | 1. Copy ticket token from `/tickets.html`<br>2. Open `/validator.html`<br>3. Submit token once, then submit again. | 1st scan returns VALID (status transitions to USED); 2nd scan returns INVALID - ALREADY USED. | 1st scan validated with green banner; 2nd scan rejected with red warning banner. | **PASS** |
| **10** | **Transit Passes Booking Lifecycle** | 1. Navigate to `/passes.html`<br>2. Select Daily Pass (₹50.00) and click Buy.<br>3. Complete simulated payment. | Pass booked, activated, and rendered with scannable QR code and 24h validity window. | Daily pass created, payment confirmed, QR rendered in Active Passes. | **PASS** |
| **11** | **Transit AI Assistant & Model Indicator** | 1. Navigate to `/ai-assistant.html`<br>2. Verify header model badge.<br>3. Send transit query: "How to travel from Shivajinagar to Swargate?". | Header displays "Demo AI Mode • Backend-Authoritative Transit Intelligence"; chat returns accurate transit route. | Model badge visible, assistant responds with accurate Pune Metro route. | **PASS** |
| **12** | **Admin Dashboard & Dynamic Fare Configuration** | 1. Log in as `admin@intellitransit.com`<br>2. Navigate to `/admin.html`<br>3. Inspect KPI metrics and update fare matrix. | Dashboard displays metrics; non-admin users blocked; fare update persists. | Metrics loaded, commuter access blocked with 403, fare rates updated. | **PASS** |
