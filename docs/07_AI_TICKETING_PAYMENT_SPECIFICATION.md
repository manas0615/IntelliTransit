# IntelliTransit — AI, Ticketing and Payment Specification

**Document:** `07_AI_TICKETING_PAYMENT_SPECIFICATION.md`  
**Project:** IntelliTransit  
**Depends on:** `01_PROJECT_DEFINITION.md`, `02_SYSTEM_ARCHITECTURE.md`, `03_DATABASE_DESIGN.md`, `04_BACKEND_API_SPECIFICATION.md`, `05_ROUTING_AND_INTELLIGENCE.md`, `06_FRONTEND_UI_SPECIFICATION.md`  
**Status:** AI, TICKETING AND PAYMENT BASELINE — LEG-BASED TICKETING UPDATE

---

# 1. Purpose

This document defines three connected but separately controlled subsystems:

1. **Gemini 2.5 Flash AI transportation assistant**
2. **Digital ticket/pass lifecycle**
3. **Razorpay Test Mode payment processing**

It also defines QR generation and backend validation.

The central architectural rule is:

> **AI assists the user, OTP calculates journeys, Flask controls business logic, PostgreSQL stores application state, and Razorpay processes payments.**

No subsystem is allowed to silently replace another subsystem's responsibility.

---

# 2. AI Architecture

The AI assistant uses:

**Gemini 2.5 Flash**

The integration is backend-only.

```text
Browser
   │
   │ POST /api/ai/chat
   ▼
Flask AI Service
   │
   ▼
Gemini 2.5 Flash
   │
   ├── direct conversational response
   │
   └── tool/function request
          │
          ▼
      Flask Tool Layer
          │
          ├── Journey Service
          ├── User/Preference Service
          ├── Journey History
          ├── Ticket Service
          └── Pass Service
```

The browser never receives the Gemini API key.

---

# 3. AI's Role

Gemini can help the user:

- understand transportation options;
- formulate journey requests;
- ask natural-language questions;
- interpret route results;
- explain an existing journey;
- answer contextual follow-up questions;
- access authorized user-specific information through backend tools;
- guide users through ticket/pass-related information.

Gemini is **not** the routing engine.

---

# 4. AI Non-Responsibilities

Gemini must not independently determine:

- actual bus routes;
- actual metro routes;
- official departure times;
- official arrival times;
- ticket status;
- pass status;
- payment success;
- fare values when authoritative backend data is available;
- QR validity;
- user authorization;
- database records.

For these facts, the AI must use backend-provided information.

---

# 5. AI Request Flow

Basic conversation:

```text
User
 ↓
AI Assistant UI
 ↓
POST /api/ai/chat
 ↓
Flask AI Service
 ↓
Gemini
 ↓
Response
 ↓
Browser
```

Tool-backed conversation:

```text
User
 ↓
Flask
 ↓
Gemini
 ↓
Tool request
 ↓
Flask validates/executes tool
 ↓
Actual application service
 ↓
Tool result
 ↓
Gemini
 ↓
Response
 ↓
User
```

---

# 6. Natural-Language Journey Planning

Example:

> "Find me the fastest way from Pune Railway Station to Civil Court."

The AI should identify:

```text
Intent:
PLAN_JOURNEY

Origin:
Pune Railway Station

Destination:
Civil Court

Preference:
FASTEST
```

Then call the backend journey-planning function.

```text
Gemini
 ↓
planJourney()
 ↓
Journey Service
 ↓
OTP
 ↓
Intelligence Layer
 ↓
Ranked itineraries
 ↓
Gemini
 ↓
Explanation
```

The AI does not invent the route.

---

# 7. AI Function/Tool Calling

Recommended initial tools:

```text
plan_journey
get_journey_details
get_user_preferences
get_journey_history
get_active_tickets
get_active_passes
```

Additional tools can be introduced only when a concrete requirement exists.

---

# 8. `plan_journey`

Purpose:

Calculate an actual journey using the normal IntelliTransit routing pipeline.

Conceptual input:

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
  "route_preference": "FASTEST"
}
```

The function calls the same journey service used by the normal planner.

It must not implement a separate AI-only routing system.

---

# 9. `get_journey_details`

Purpose:

Retrieve details for a journey already known to the application.

Possible information:

```text
origin
destination
duration
fare
walking distance
transfers
legs
route type
```

Authorization is required when the journey is private/user-owned.

---

# 10. `get_user_preferences`

Purpose:

Retrieve the authenticated user's configured transportation preferences.

Examples:

```text
preferred mode
route preference
maximum walking distance
avoid taxi
avoid transfers
```

The AI should use this information only when the user is authenticated and authorized.

---

# 11. `get_journey_history`

Purpose:

Retrieve relevant previous journeys for an authenticated user.

Example:

```text
User:
"How did I travel to college last week?"
```

The AI can call the history tool and summarize actual stored records.

It must not claim a trip occurred if no matching record exists.

---

# 12. `get_active_tickets`

Purpose:

Retrieve currently available user ticket information.

Possible information:

```text
ticket status
origin
destination
fare
valid_from
valid_until
```

The AI must not change ticket status through this read-only tool.

---

# 13. `get_active_passes`

Purpose:

Retrieve active pass information.

Possible information:

```text
pass type
status
price
valid_from
valid_until
```

Again, the AI does not independently determine validity.

---

# 14. AI Authorization Boundary

For user-specific tools:

```text
AI request
 ↓
Authenticated user context
 ↓
Flask
 ↓
Tool receives server-derived user_id
 ↓
Database query
```

Do not allow the model to supply an arbitrary:

```json
{
  "user_id": "another-user"
}
```

for protected operations.

The server determines the authenticated user.

---

# 15. AI Tool Result Principle

Tool results should be structured.

Example:

```json
{
  "success": true,
  "journey": {
    "duration_min": 25,
    "walking_distance_m": 600,
    "estimated_fare": 35.0,
    "fare_source": "ESTIMATED",
    "transfers": 1
  }
}
```

Gemini can then convert this into natural language.

---

# 16. AI Hallucination Prevention

The AI system should follow these rules:

```text
If data exists:
    use tool/backend data.

If data is unavailable:
    say it is unavailable.

If data is estimated:
    say it is estimated.

If data is ambiguous:
    ask for clarification.

Never invent:
    route
    fare
    timing
    ticket state
    pass state
```

---

# 17. AI Context Management

Conversation context should be kept compact.

For a follow-up such as:

```text
User:
Find the fastest route from A to B.

AI:
Route 1 takes 25 minutes...
```

then:

```text
User:
What about the cheapest one?
```

the system can retain a compact structured context such as:

```text
origin
destination
candidate route IDs
route metrics
selected preference
```

It should not repeatedly send the entire raw OTP response to Gemini.

---

# 18. AI Conversation Identifier

The frontend may maintain:

```text
conversation_id
```

The backend can use it to associate conversation context.

The exact persistence strategy is intentionally lightweight for the initial project.

A dedicated conversation database is not required by the current core schema.

---

# 19. AI Error Handling

If Gemini is unavailable:

```text
AI_UNAVAILABLE
```

The user should see:

```text
The AI assistant is temporarily unavailable.
You can still use the normal journey planner.
```

The routing system remains independent.

---

# 20. AI API Security

The Gemini API key must be stored in backend environment configuration.

Example conceptual configuration:

```text
GEMINI_API_KEY=<secret>
```

Never place it in:

```text
HTML
JavaScript
CSS
Git repository
API response
```

---

# 21. AI Rate/Abuse Protection

The backend may apply basic rate limiting to AI requests if needed.

The objective is to prevent accidental or malicious excessive API usage.

Do not make AI rate limits a dependency for the core transportation planner.

---

# 22. Ticketing Architecture

Tickets represent purchases for **individual ticketable journey legs**. A journey remains a unified planning object, but it may contain several independently ticketed legs.

Example:

```text
Journey: A → C

Leg 1: A → B, Taxi, ticketable
Leg 2: B → C, Metro, ticketable

Ticket 1 + Payment 1 → Leg 1
Ticket 2 + Payment 2 → Leg 2
```

Walking or transfer legs can remain part of the journey without requiring a ticket.

Ticket lifecycle:

```text
PENDING
   ↓
ACTIVE
   ↓
USED

or

PENDING
   ↓
NOT ACTIVATED / FAILED

or

ACTIVE
   ↓
EXPIRED

or

ACTIVE
   ↓
CANCELLED
```

The exact transition rules are enforced by the backend.

---

# 23. Ticket Creation

A ticket begins with a selected **ticketable journey leg**, not automatically with the entire journey.

```text
User selects journey
 ↓
User selects ticketable leg
 ↓
Buy Ticket
 ↓
POST /api/tickets
 ↓
Backend validates journey + leg
 ↓
Authoritative leg fare determined
 ↓
Ticket created as PENDING
 ↓
One payment created for that ticket
 ↓
Payment process begins
```

The ticket should not become ACTIVE before successful payment verification.

---

# 24. Ticket Data

The ticket stores:

```text
ticket_id
user_id
journey_id
journey_leg_id
payment_id
ticket_token
status
origin
destination
fare
valid_from
valid_until
created_at
```

The origin, destination, and fare are historical snapshot values for the purchased leg.

---

# 25. Ticket Validity

An active ticket may have:

```text
valid_from
valid_until
```

The backend uses these fields during validation.

Conceptually:

```text
Current time
      │
      ├── before valid_from → not yet valid
      ├── within validity → valid
      └── after valid_until → expired
```

The final exact validity duration should be configured consistently during implementation.

---

# 25.1 Leg-Level Cancellation and Refund Principle

Cancellation is handled per ticketable leg.

Example:

```text
A → B → C

Leg 1: A → B = purchased/used
Leg 2: B → C = not purchased
```

If the user stops at B, there is no unused portion of a combined A → C ticket to calculate because Leg 2 was never purchased.

If Leg 2 was already purchased, any refund is evaluated for **that ticket only** according to the configured cancellation policy.

The initial implementation should use a simple, explicit policy rather than attempting dynamic partial-fare refunds across multiple operators.

Recommended initial policy: a ticket may be cancelled/refunded before its validity begins, subject to the configured policy; once validity has begun, it is normally non-refundable unless an explicit supported exception is implemented.

IntelliTransit does not automatically promise refunds from external transportation operators.

---

# 26. Ticket Activation

Activation occurs after successful payment verification.

```text
Ticket PENDING
       │
       ▼
Payment verification
       │
       ├── SUCCESS → ACTIVE
       │
       └── FAILED  → remains inactive/failed according to state handling
```

The frontend must not perform this transition.

---

# 27. Ticket Token

Each ticket receives a unique secure token.

The token should be generated using a cryptographically secure random mechanism.

It should not simply be:

```text
ticket_id
```

or:

```text
user_id + timestamp
```

The token acts as the backend lookup/validation identifier.

---

# 28. QR Generation

The QR represents the secure ticket token.

Conceptually:

```text
Secure Ticket Token
        ↓
Python QR generation library
        ↓
QR image
        ↓
Frontend display
```

The QR should contain only the information required for validation.

Do not encode unnecessary personal data.

---

# 29. QR Validation

Validation flow:

```text
Validator
 ↓
Scan/read QR
 ↓
Extract ticket token
 ↓
POST /api/validation/tickets
 ↓
Flask
 ↓
Find ticket
 ↓
Check status
 ↓
Check validity period
 ↓
Record validation
 ↓
Return result
```

---

# 30. Validation Results

Supported validation states:

```text
VALID
INVALID
EXPIRED
CANCELLED
```

The backend determines the result.

The QR itself does not contain enough authority to declare a ticket valid.

---

# 31. Validation History

Every validation attempt can create a row in:

```text
ticket_validations
```

This preserves:

```text
ticket
validator
result
time
remarks
```

Multiple validation records can exist for the same ticket.

---

# 32. Ticket Used State

If the project uses a single-use ticket model, a successful validation can transition:

```text
ACTIVE
   ↓
USED
```

The exact single-use rule should be defined consistently before implementation.

If multiple validations are allowed during a validity window, the ticket can remain ACTIVE while each validation is recorded.

The chosen behavior must be documented in the final implementation.

---

# 33. Pass Architecture

Supported passes:

```text
DAILY
WEEKLY
MONTHLY
```

Pass lifecycle:

```text
PENDING
   ↓
ACTIVE
   ↓
EXPIRED
```

Cancellation may produce:

```text
CANCELLED
```

---

# 34. Pass Purchase

Flow:

```text
User selects pass
 ↓
POST /api/passes
 ↓
Backend determines pass price
 ↓
Pass created PENDING
 ↓
Payment order created
 ↓
Razorpay checkout
 ↓
Backend verifies payment
 ↓
Pass ACTIVE
```

The frontend does not determine the price.

---

# 35. Pass Validity

The backend calculates:

```text
valid_from
valid_until
```

according to:

```text
DAILY
WEEKLY
MONTHLY
```

The exact calendar/time rules should be centralized in the pass service.

Avoid duplicating validity calculations in JavaScript.

---

# 36. Pass Token and QR

A pass receives:

```text
pass_token
```

The token can be represented as a QR code.

Validation behavior for passes can be implemented later if required by the final demonstration scope.

The core schema supports the pass token.

---

# 37. Payment Architecture

Payment provider:

**Razorpay Test Mode**

The application uses Razorpay for demonstration/testing.

No real transportation payment settlement is implied by the academic project.

---

# 38. Payment Responsibility

Razorpay handles:

```text
payment checkout
payment processing in test environment
payment identifiers
```

Flask handles:

```text
business item
amount
local payment record
order creation
verification
ticket/pass activation
```

PostgreSQL stores the application-side payment record.

---

# 39. Payment Flow

Complete flow:

```text
User
 ↓
Select Ticketable Leg or Pass
 ↓
Flask creates business item
 ↓
Flask calculates authoritative amount
 ↓
Flask creates one local payment PENDING
 ↓
Flask creates Razorpay order
 ↓
Frontend opens checkout
 ↓
User completes test payment
 ↓
Razorpay returns payment information
 ↓
Frontend sends verification data to Flask
 ↓
Flask verifies payment
 ↓
Payment SUCCESS?
    │
    ├── YES → Activate that ticket/pass only
    │
    └── NO  → Do not activate
```

---

# 40. Backend-Authoritative Amount

The frontend must never be trusted to set:

```text
ticket price
pass price
payment amount
```

For example, this request must not be authoritative:

```json
{
  "amount": 1
}
```

The backend determines the amount from:

```text
selected journey/fare
or
configured pass price
```

---

# 41. Local Payment Record

Before checkout, create a local record:

```text
payment_id
user_id
amount
currency
payment_type
status = PENDING
razorpay_order_id
```

This creates an application-side link between the business item and Razorpay order.

---

# 42. Razorpay Order

The backend creates the Razorpay order.

Conceptually:

```text
Ticket/Pass
     ↓
Authoritative amount
     ↓
Razorpay order
     ↓
order_id
```

The order ID is stored in:

```text
payments.razorpay_order_id
```

---

# 43. Payment Verification

Verification request may contain:

```text
razorpay_order_id
razorpay_payment_id
razorpay_signature
```

The backend verifies the payment using the appropriate Razorpay verification mechanism.

Only after verification:

```text
payments.status = SUCCESS
```

and:

```text
ticket.status = ACTIVE
```

or:

```text
pass.status = ACTIVE
```

---

# 44.1 Ticket Cancellation and Refund Flow

When a user cancels a ticket, cancellation is evaluated for that ticketable leg only.

```text
User requests cancellation
 ↓
Backend checks ticket ownership/status
 ↓
Check cancellation eligibility
 ↓
Eligible?
 ├── NO → keep ticket active/unchanged and report policy result
 └── YES
       ↓
   initiate configured refund
       ↓
   refund confirmed
       ↓
   payment = REFUNDED
       ↓
   ticket = CANCELLED
```

For the academic Test Mode implementation, the refund operation may be implemented against the supported Razorpay Test Mode workflow or represented as a controlled simulated refund if the exact provider flow is not required for the demonstration. The application must clearly distinguish a simulated refund from a provider-confirmed refund.

A user who stops at B in an A → B → C journey does not need a refund for B → C if that second leg was never purchased.

---

# 44. Payment Failure

If verification fails:

```text
payments.status = FAILED
```

or an appropriate pending/retry state may be maintained depending on the exact failure.

The important rule:

```text
FAILED PAYMENT
      ≠
ACTIVE TICKET
```

---

# 45. Duplicate Payment Handling

The backend should prevent a single business item from being accidentally activated multiple times.

Before activating:

```text
Check current payment/business-item state
```

If already successfully activated:

```text
Do not create another active ticket/pass unintentionally.
```

---

# 46. Payment Amount Verification

During verification, the backend should confirm that the payment corresponds to:

```text
expected order
+
expected business item
+
expected amount
```

Do not rely only on the presence of a payment ID.

---

# 47. Payment Webhook

If webhook integration is used:

```text
Razorpay
 ↓
POST /api/payments/webhook
 ↓
Verify webhook authenticity
 ↓
Update local payment state
```

The webhook must be treated as an external request and verified before changing business state.

---

# 48. Payment Idempotency

Payment operations should be designed so that repeated verification requests do not create duplicate activation.

Example:

```text
verify payment
 ↓
already SUCCESS?
 ↓
return existing success
```

rather than:

```text
verify payment
 ↓
activate again
```

---

# 49. Ticket/Payment Relationship

The database relationship is:

```text
USER
 │
 └── JOURNEY
       │
       └── JOURNEY_LEG
              │
              └── TICKET ─── PAYMENT
```

A ticket is associated with:

```text
user
journey
journey_leg
payment
```

For the initial implementation:

```text
1 ticketable leg → 1 ticket → 1 payment
```

Multiple ticketable legs therefore create separate ticket/payment pairs.

---

# 50. Pass/Payment Relationship

```text
USER
 │
 ├── PAYMENT
 │      │
 │      └── PASS
 │
 └── PASS
```

The pass is associated with:

```text
user
payment
```

For the initial implementation:

```text
1 pass → 1 payment
```

---

# 51. Payment Status Values

Supported initial values:

```text
PENDING
SUCCESS
FAILED
REFUNDED
```

The backend must control status transitions.

---

# 52. Ticket Status Values

Supported:

```text
PENDING
ACTIVE
USED
EXPIRED
CANCELLED
```

The exact transition rules should be implemented centrally in `ticket_service.py`.

---

# 53. Pass Status Values

Supported:

```text
PENDING
ACTIVE
EXPIRED
CANCELLED
```

---

# 54. QR Security Rules

The QR system must:

1. use unpredictable tokens;
2. avoid unnecessary personal information;
3. validate through the backend;
4. check ticket/pass state;
5. check validity period;
6. record validation where applicable;
7. never rely on visual QR appearance alone.

No offline validation is required.

---

# 55. QR Does Not Equal Authorization

A valid-looking QR image is not enough.

The validator must obtain the token and ask the backend.

```text
QR
 ↓
Token
 ↓
Backend
 ↓
Database
 ↓
Validation decision
```

---

# 56. AI + Ticketing Boundary

Gemini may answer:

> "Is my ticket active?"

Correct:

```text
Gemini
 ↓
get_active_tickets()
 ↓
Backend
 ↓
Actual ticket state
 ↓
Gemini explanation
```

Incorrect:

```text
Gemini guesses ticket status from conversation.
```

---

# 57. AI + Payment Boundary

Gemini may explain:

```text
"Your payment is marked successful."
```

only if the backend tool returns:

```text
SUCCESS
```

Gemini must not:

- initiate arbitrary payment changes;
- declare payment successful without backend verification;
- modify payment status.

---

# 58. AI + Pass Boundary

For:

> "When does my weekly pass expire?"

The AI should call:

```text
get_active_passes()
```

and use:

```text
valid_until
```

from the backend.

---

# 59. AI + Route + Ticket Flow

A complete conversational flow can be:

```text
User:
"Find the cheapest way to Civil Court."

        ↓

Gemini
        ↓
plan_journey()

        ↓

OTP
        ↓
Intelligence Layer
        ↓
Cheapest route

        ↓

Gemini:
"Route A costs approximately ₹X..."

        ↓

User:
"Buy a ticket."

        ↓

Frontend/Backend ticket flow
        ↓

Razorpay Test Mode
        ↓

Verification
        ↓

ACTIVE ticket
        ↓

QR
```

The AI can guide the workflow, but backend services remain authoritative.

---

# 60. AI Tool Failure

If a tool fails:

```text
Tool error
 ↓
Return structured failure
 ↓
Gemini explains limitation
```

Example:

```text
I couldn't retrieve your active tickets right now.
```

Do not fabricate a result.

---

# 61. AI Tool Permission Matrix

| Tool | Guest | USER | ADMIN |
|---|---:|---:|---:|
| plan_journey | ✓ | ✓ | ✓ |
| get_journey_details | Public/current or authorized | Own data | Authorized |
| get_user_preferences | | Own data | Authorized |
| get_journey_history | | Own data | Authorized |
| get_active_tickets | | Own data | Authorized |
| get_active_passes | | Own data | Authorized |

The backend determines actual authorization.

---

# 62. Ticket Purchase Security

The ticket purchase process must verify:

```text
Authenticated user
+
Valid journey
+
Authoritative fare
+
Valid payment
```

Only then:

```text
ACTIVE ticket
```

---

# 63. Pass Purchase Security

The pass purchase process must verify:

```text
Authenticated user
+
Valid pass type
+
Authoritative price
+
Valid payment
```

Only then:

```text
ACTIVE pass
```

---

# 64. Payment and Database Transaction Boundary

Where possible, related local database changes should be handled atomically.

Example:

```text
Successful verified payment
        ↓
Update payment = SUCCESS
        ↓
Activate ticket
```

The implementation must prevent a state where:

```text
payment = SUCCESS
ticket = accidentally still pending
```

without a recoverable reconciliation path.

---

# 65. Payment Reconciliation

If an external payment event succeeds but the local update fails:

```text
Razorpay = SUCCESS
PostgreSQL = not updated
```

the system should provide a controlled reconciliation mechanism.

For the academic implementation, this can be handled through:

- verified payment lookup;
- webhook processing;
- admin reconciliation;
- safe re-verification.

Do not silently issue another payment.

---

# 66. Test Mode Rules

Razorpay must remain in Test Mode for the project demonstration.

The project should clearly state:

```text
Payment Gateway:
Razorpay Test Mode
```

This means:

- no real payment settlement is required;
- test credentials are used;
- test transactions demonstrate the integration flow.

---

# 67. Secret Management

Secrets must be stored outside source code.

Example:

```text
GEMINI_API_KEY
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
JWT_SECRET
DATABASE_URL
```

Use:

```text
.env
```

locally and:

```text
.env.example
```

for repository documentation.

`.env` must be excluded from Git.

---

# 68. No Sensitive Payment Storage

Do not store:

```text
card number
CVV
UPI PIN
bank credentials
```

The project stores only the application-level payment identifiers/status needed for its workflow.

---

# 69. Ticket/Pass UI State

The frontend should display only backend-confirmed state.

Example:

```text
Payment checkout opened
```

does not mean:

```text
Ticket ACTIVE
```

Only:

```text
Backend verification = SUCCESS
```

allows:

```text
Ticket ACTIVE
```

---

# 70. Complete Ticket Lifecycle

```text
                  SELECT JOURNEY + TICKETABLE LEG
                        │
                        ▼
                 CREATE TICKET FOR LEG
                        │
                        ▼
                    PENDING
                        │
                        ▼
                 CREATE PAYMENT
                        │
                        ▼
                 RAZORPAY TEST
                        │
                 ┌──────┴──────┐
                 │             │
              SUCCESS        FAILED
                 │             │
                 ▼             ▼
               ACTIVE       INACTIVE/
                 │           FAILED
          ┌──────┴──────┐
          │             │
       VALIDATE       EXPIRE
          │
          ▼
        USED
```

Cancellation can occur from an appropriate business state.

---

# 71. Complete Pass Lifecycle

```text
SELECT PASS
     │
     ▼
CREATE PASS
     │
     ▼
PENDING
     │
     ▼
PAYMENT
     │
 ┌───┴────┐
 ▼        ▼
SUCCESS  FAILED
 │
 ▼
ACTIVE
 │
 ▼
EXPIRED
```

---

# 72. AI + Application Architecture

The complete relationship is:

```text
                     USER
                       │
                       ▼
                FRONTEND UI
                       │
             ┌─────────┴─────────┐
             │                   │
       Normal Planner        AI Assistant
             │                   │
             ▼                   ▼
          Flask ◄────────── Gemini
             │                 │
             │          Tool Requests
             │                 │
       ┌─────┼─────────────────┘
       │     │
       ▼     ▼
      OTP  PostgreSQL
       │     │
       └──┬──┘
          │
          ▼
 Intelligence Layer
          │
          ▼
    Journey Results
```

Ticket/payment path:

```text
Journey
   ↓
Ticket/Pass
   ↓
Flask
   ↓
Razorpay Test Mode
   ↓
Verification
   ↓
PostgreSQL
   ↓
Active Ticket/Pass
   ↓
QR
```

---

# 73. Implementation Modules

Recommended service modules:

```text
services/
├── ai_service.py
├── ticket_service.py
├── pass_service.py
├── payment_service.py
└── qr_service.py
```

Responsibilities:

### `ai_service.py`

```text
Gemini integration
tool definitions
tool execution coordination
AI response handling
```

### `ticket_service.py`

```text
ticket creation
ticket state transitions
ticket retrieval
ticket validity
```

### `pass_service.py`

```text
pass creation
pass pricing
pass validity
pass state
```

### `payment_service.py`

```text
Razorpay order creation
payment verification
payment state
reconciliation
```

### `qr_service.py`

```text
secure token generation
QR generation
```

---

# 74. AI Testing

Minimum AI tests:

```text
1. Normal transportation question
2. Journey planning question
3. Cheapest route request
4. Fastest route request
5. Follow-up question
6. User preference query
7. Journey history query
8. Active ticket query
9. Active pass query
10. Gemini unavailable
11. Tool unavailable
12. Ambiguous location
```

The expected behavior must be grounded in backend data.

---

# 75. Ticket Testing

Test:

```text
Create ticket for a journey leg
Payment pending
Payment success
Payment failure
Ticket activation
Ticket retrieval
QR generation
Valid QR
Invalid token
Expired ticket
Cancelled ticket
Eligible ticket cancellation/refund
Non-refundable post-validity cancellation
Repeated validation
```

---

# 76. Pass Testing

Test:

```text
Daily pass
Weekly pass
Monthly pass
Price retrieval
Payment success
Payment failure
Activation
Expiry
QR generation
```

---

# 77. Payment Testing

Test:

```text
Order creation
Correct amount
Correct payment type
Successful test payment
Failed test payment
Verification failure
Duplicate verification
Invalid signature
Unknown order
```

---

# 78. Final AI/Ticketing/Payment Rules

1. Gemini 2.5 Flash is an assistant, not the routing engine.
2. Gemini API access remains backend-only.
3. AI uses backend tools for factual transportation/user data.
4. AI must not invent transportation facts.
5. OTP remains authoritative for route calculation.
6. Backend remains authoritative for ticket/pass state.
7. Backend determines payment amounts.
8. Razorpay is used in Test Mode.
9. Payment must be verified server-side.
10. Successful payment activates the associated business item.
11. QR codes contain secure identifiers rather than unnecessary personal data.
12. QR validity is determined by the backend.
13. Ticket validation is recorded in PostgreSQL.
14. Payment credentials are never stored by IntelliTransit.
15. AI failure must not break normal journey planning.
16. Payment failure must not activate a ticket/pass.
17. Duplicate payment verification must be safe.
18. Historical ticket values must remain stable.
19. A journey can contain multiple independently ticketed legs.
20. One payment belongs to one ticket or one pass.
21. A user stopping at an intermediate point does not require a refund for a future leg that was never purchased.
22. Refunds, when supported, are evaluated at the individual ticket level.
23. IntelliTransit does not promise automatic refunds from external transportation operators.

---

# 79. Relationship to Next Document

The next document:

`08_SECURITY_TESTING_AND_ERROR_HANDLING.md`

will consolidate:

- authentication security;
- API security;
- database security;
- input validation;
- payment security;
- QR security;
- AI safety;
- external-service failure handling;
- testing strategy;
- integration tests;
- edge cases;
- performance testing;
- final quality checklist.

---

**END OF DOCUMENT**
