-- ============================================================================
-- IntelliTransit: Authoritative PostgreSQL Database Schema
-- Baseline: 11 Tables, Exact Constraints, Indexes, and Relational Integrity
-- ============================================================================

-- Enable pgcrypto for UUID generation if not already available
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Drop existing tables in reverse dependency order
DROP TABLE IF EXISTS ticket_validations CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS passes CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS fare_configurations CASCADE;
DROP TABLE IF EXISTS transport_services CASCADE;
DROP TABLE IF EXISTS journey_legs CASCADE;
DROP TABLE IF EXISTS journeys CASCADE;
DROP TABLE IF EXISTS saved_locations CASCADE;
DROP TABLE IF EXISTS user_preferences CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ----------------------------------------------------------------------------
-- 1. USERS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(100) NOT NULL CHECK (length(trim(full_name)) > 0),
    email VARCHAR(255) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    phone VARCHAR(15) UNIQUE CHECK (phone IS NULL OR phone ~* '^[6-9][0-9]{9}$'),
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN')),
    account_type VARCHAR(30) NOT NULL DEFAULT 'COMMUTER' CHECK (account_type IN ('COMMUTER', 'ADMINISTRATOR', 'CONDUCTOR')),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);

-- ----------------------------------------------------------------------------
-- 2. USER_PREFERENCES TABLE (1:1 with users)
-- ----------------------------------------------------------------------------
CREATE TABLE user_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(user_id) ON DELETE CASCADE,
    preferred_mode VARCHAR(20) CHECK (preferred_mode IS NULL OR preferred_mode IN ('BUS', 'METRO', 'TAXI')),
    route_preference VARCHAR(30) CHECK (route_preference IS NULL OR route_preference IN ('FASTEST', 'CHEAPEST', 'LEAST_WALKING', 'FEWEST_TRANSFERS', 'BALANCED')),
    max_walking_distance_m INTEGER CHECK (max_walking_distance_m IS NULL OR max_walking_distance_m >= 0),
    avoid_taxi BOOLEAN NOT NULL DEFAULT FALSE,
    avoid_transfers BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- ----------------------------------------------------------------------------
-- 3. SAVED_LOCATIONS TABLE (1:N with users)
-- ----------------------------------------------------------------------------
CREATE TABLE saved_locations (
    location_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    label VARCHAR(50) NOT NULL CHECK (length(trim(label)) > 0),
    location_name VARCHAR(150) NOT NULL CHECK (length(trim(location_name)) > 0),
    address TEXT,
    latitude DECIMAL(9,6) NOT NULL CHECK (latitude BETWEEN -90.000000 AND 90.000000),
    longitude DECIMAL(9,6) NOT NULL CHECK (longitude BETWEEN -180.000000 AND 180.000000),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_saved_locations_user_id ON saved_locations(user_id);

-- ----------------------------------------------------------------------------
-- 4. JOURNEYS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE journeys (
    journey_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    origin_name VARCHAR(150) NOT NULL CHECK (length(trim(origin_name)) > 0),
    origin_latitude DECIMAL(9,6) NOT NULL CHECK (origin_latitude BETWEEN -90.000000 AND 90.000000),
    origin_longitude DECIMAL(9,6) NOT NULL CHECK (origin_longitude BETWEEN -180.000000 AND 180.000000),
    destination_name VARCHAR(150) NOT NULL CHECK (length(trim(destination_name)) > 0),
    destination_latitude DECIMAL(9,6) NOT NULL CHECK (destination_latitude BETWEEN -90.000000 AND 90.000000),
    destination_longitude DECIMAL(9,6) NOT NULL CHECK (destination_longitude BETWEEN -180.000000 AND 180.000000),
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP CHECK (arrival_time IS NULL OR departure_time IS NULL OR arrival_time >= departure_time),
    total_duration_min INTEGER CHECK (total_duration_min IS NULL OR total_duration_min >= 0),
    walking_distance_m INTEGER CHECK (walking_distance_m IS NULL OR walking_distance_m >= 0),
    estimated_fare DECIMAL(10,2) CHECK (estimated_fare IS NULL OR estimated_fare >= 0.00),
    route_type VARCHAR(30),
    otp_itinerary_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_journeys_user_id ON journeys(user_id);
CREATE INDEX idx_journeys_created_at ON journeys(created_at DESC);

-- ----------------------------------------------------------------------------
-- 5. TRANSPORT_SERVICES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE transport_services (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('BUS', 'METRO', 'TAXI')),
    operator_name VARCHAR(100) NOT NULL CHECK (length(trim(operator_name)) > 0),
    service_name VARCHAR(150) NOT NULL CHECK (length(trim(service_name)) > 0),
    external_id VARCHAR(100),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transport_services_mode ON transport_services(mode);
CREATE INDEX idx_transport_services_is_active ON transport_services(is_active);

-- ----------------------------------------------------------------------------
-- 6. FARE_CONFIGURATIONS TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE fare_configurations (
    fare_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_id UUID NOT NULL REFERENCES transport_services(service_id) ON DELETE CASCADE,
    fare_type VARCHAR(30) NOT NULL CHECK (fare_type IN ('FLAT', 'DISTANCE_BASED', 'ZONE_BASED')),
    base_fare DECIMAL(10,2) NOT NULL CHECK (base_fare >= 0.00),
    per_km_rate DECIMAL(10,2) CHECK (per_km_rate IS NULL OR per_km_rate >= 0.00),
    minimum_fare DECIMAL(10,2) CHECK (minimum_fare IS NULL OR minimum_fare >= 0.00),
    effective_from TIMESTAMP NOT NULL,
    effective_until TIMESTAMP CHECK (effective_until IS NULL OR effective_until > effective_from),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_fare_configurations_service_id ON fare_configurations(service_id);
CREATE INDEX idx_fare_configurations_is_active ON fare_configurations(is_active);

-- ----------------------------------------------------------------------------
-- 7. JOURNEY_LEGS TABLE (Leg-based representation)
-- ----------------------------------------------------------------------------
CREATE TABLE journey_legs (
    leg_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    journey_id UUID NOT NULL REFERENCES journeys(journey_id) ON DELETE CASCADE,
    sequence_number INTEGER NOT NULL CHECK (sequence_number >= 1),
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('BUS', 'METRO', 'TAXI', 'WALK')),
    service_id UUID REFERENCES transport_services(service_id) ON DELETE SET NULL,
    from_name VARCHAR(150) NOT NULL CHECK (length(trim(from_name)) > 0),
    from_latitude DECIMAL(9,6) NOT NULL CHECK (from_latitude BETWEEN -90.000000 AND 90.000000),
    from_longitude DECIMAL(9,6) NOT NULL CHECK (from_longitude BETWEEN -180.000000 AND 180.000000),
    to_name VARCHAR(150) NOT NULL CHECK (length(trim(to_name)) > 0),
    to_latitude DECIMAL(9,6) NOT NULL CHECK (to_latitude BETWEEN -90.000000 AND 90.000000),
    to_longitude DECIMAL(9,6) NOT NULL CHECK (to_longitude BETWEEN -180.000000 AND 180.000000),
    departure_time TIMESTAMP,
    arrival_time TIMESTAMP CHECK (arrival_time IS NULL OR departure_time IS NULL OR arrival_time >= departure_time),
    duration_min INTEGER CHECK (duration_min IS NULL OR duration_min >= 0),
    walking_distance_m INTEGER CHECK (walking_distance_m IS NULL OR walking_distance_m >= 0),
    estimated_fare DECIMAL(10,2) CHECK (estimated_fare IS NULL OR estimated_fare >= 0.00),
    is_ticketable BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_journey_legs_journey_seq UNIQUE (journey_id, sequence_number)
);

CREATE INDEX idx_journey_legs_journey_id ON journey_legs(journey_id);
CREATE INDEX idx_journey_legs_service_id ON journey_legs(service_id);

-- ----------------------------------------------------------------------------
-- 8. PAYMENTS TABLE (Simulated Demo Payments)
-- ----------------------------------------------------------------------------
CREATE TABLE payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0.00),
    currency CHAR(3) NOT NULL DEFAULT 'INR' CHECK (length(currency) = 3),
    payment_type VARCHAR(20) NOT NULL CHECK (payment_type IN ('TICKET', 'PASS')),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED', 'REFUNDED')),
    payment_method VARCHAR(50) NOT NULL DEFAULT 'SIMULATED',
    transaction_reference VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_tx_ref ON payments(transaction_reference);

-- ----------------------------------------------------------------------------
-- 9. TICKETS TABLE (Leg-based ticketing snapshot)
-- ----------------------------------------------------------------------------
CREATE TABLE tickets (
    ticket_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    journey_id UUID NOT NULL REFERENCES journeys(journey_id) ON DELETE RESTRICT,
    journey_leg_id UUID NOT NULL REFERENCES journey_legs(leg_id) ON DELETE RESTRICT,
    payment_id UUID NOT NULL UNIQUE REFERENCES payments(payment_id) ON DELETE RESTRICT,
    ticket_token VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACTIVE', 'USED', 'EXPIRED', 'CANCELLED')),
    origin VARCHAR(150) NOT NULL CHECK (length(trim(origin)) > 0),
    destination VARCHAR(150) NOT NULL CHECK (length(trim(destination)) > 0),
    fare DECIMAL(10,2) NOT NULL CHECK (fare >= 0.00),
    valid_from TIMESTAMP,
    valid_until TIMESTAMP CHECK (valid_until IS NULL OR valid_from IS NULL OR valid_until >= valid_from),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_token ON tickets(ticket_token);
CREATE INDEX idx_tickets_journey_id ON tickets(journey_id);
CREATE INDEX idx_tickets_journey_leg_id ON tickets(journey_leg_id);

-- ----------------------------------------------------------------------------
-- 10. PASSES TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE passes (
    pass_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    payment_id UUID NOT NULL UNIQUE REFERENCES payments(payment_id) ON DELETE RESTRICT,
    pass_type VARCHAR(20) NOT NULL CHECK (pass_type IN ('DAILY', 'WEEKLY', 'MONTHLY')),
    pass_token VARCHAR(255) UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACTIVE', 'EXPIRED', 'CANCELLED')),
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0.00),
    valid_from TIMESTAMP,
    valid_until TIMESTAMP CHECK (valid_until IS NULL OR valid_from IS NULL OR valid_until >= valid_from),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_passes_user_id ON passes(user_id);
CREATE INDEX idx_passes_status ON passes(status);
CREATE INDEX idx_passes_token ON passes(pass_token);

-- ----------------------------------------------------------------------------
-- 11. TICKET_VALIDATIONS TABLE (Audit inspection history)
-- ----------------------------------------------------------------------------
CREATE TABLE ticket_validations (
    validation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID NOT NULL REFERENCES tickets(ticket_id) ON DELETE RESTRICT,
    validator_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    validation_status VARCHAR(20) NOT NULL CHECK (validation_status IN ('VALID', 'INVALID', 'EXPIRED', 'CANCELLED')),
    validation_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ticket_validations_ticket_id ON ticket_validations(ticket_id);
CREATE INDEX idx_ticket_validations_validator_id ON ticket_validations(validator_user_id);
CREATE INDEX idx_ticket_validations_time ON ticket_validations(validation_time);
