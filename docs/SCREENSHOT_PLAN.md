# IntelliTransit — Demonstration Screenshot & Evidence Plan

This document establishes the official 18-point screenshot capture plan for academic report inclusion, presentation slides, and submission evidence packages.

---

## Screenshot Inventory & Capture Specifications

| Screenshot ID | Page / Route | View / State | Verification Purpose | Key Elements to Capture |
| :--- | :--- | :--- | :--- | :--- |
| `SCR-01` | `/index.html` | Hero Landing | Visual styling & responsive header | Hero headline, feature cards, navigation links, theme styles. |
| `SCR-02` | `/planner.html` | Empty State | Map canvas initialization | MapLibre canvas centered on Pune, origin/destination inputs, search CTA. |
| `SCR-03` | `/planner.html` | Planned Route | Guest journey calculation | Multi-leg route card, duration (28 min), fare (₹25), ranking profile badge. |
| `SCR-04` | `/planner.html` | Map Polyline | GeoJSON map rendering | Colored polyline paths (Metro Blue, Bus Green, Walk Dashed), station pins. |
| `SCR-05` | `/planner.html` | Leg Breakdown | Modal leg discrimination | Walk leg ("No ticket required") vs Transit leg with "Book Ticket" CTA. |
| `SCR-06` | `/login.html` | Authentication | Commuter sign-in interface | Email and password inputs, error/success validation banners. |
| `SCR-07` | `/planner.html` | Modal Opened | Simulated Payment Initiation | Modal showing Amount (₹20.00), Payment Method (`SIMULATED`), Reference ID. |
| `SCR-08` | `/planner.html` | Modal Success | Payment confirmation | Green checkmark confirmation badge, automatic redirect countdown. |
| `SCR-09` | `/tickets.html` | My Tickets | Active ticket inventory | Active ticket card with origin, destination, validity timestamps. |
| `SCR-10` | `/tickets.html` | Ticket QR | Scannable QR token display | High-contrast QR code image rendered for conductor turnstile inspection. |
| `SCR-11` | `/passes.html` | Pass Options | Periodic transit passes | Daily (₹50), Weekly (₹300), and Monthly (₹1000) pass selection cards. |
| `SCR-12` | `/passes.html` | Active Pass | Activated transit pass QR | Active Pass badge, validity countdown, passenger details, QR token. |
| `SCR-13` | `/validator.html` | Inspector Empty | Conductor turnstile portal | Token input field, QR scanner viewport, validation history table. |
| `SCR-14` | `/validator.html` | Valid Scan | Successful ticket validation | Prominent green "VALID" banner, commuter authorization, boarding clearance. |
| `SCR-15` | `/validator.html` | Second Scan | Anti-fraud reuse detection | Prominent red "INVALID / ALREADY USED" banner, timestamp of first scan. |
| `SCR-16` | `/ai-assistant.html`| Model Badge | AI Companion header | "Demo AI Mode • Backend-Authoritative Transit Intelligence" indicator badge. |
| `SCR-17` | `/ai-assistant.html`| Chat Query | Transit tool query response | Commuter question and AI response showing transit route, fare, and duration. |
| `SCR-18` | `/admin.html` | Admin Center | KPI metrics & fare matrix | KPI cards (Users, Journeys, Tickets, Simulated Revenue), Fare Matrix table. |

---

## Capture Guidelines for Report Authors
- **Resolution:** Capture at standard 1920x1080 (1080p) or 1440x900 viewport for crisp text rendering.
- **Color Fidelity:** Ensure MapLibre tiles and status badges (Green for Active/Valid, Amber for Pending, Red for Used/Expired) have proper contrast.
- **Cropping:** Maintain full context of the browser window or use consistent clean crops focused on the main content containers.
