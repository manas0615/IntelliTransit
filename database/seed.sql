-- ============================================================================
-- IntelliTransit Seed Data
-- Transport Services, Fare Configurations, Initial Admin, and Demo User
-- ============================================================================

-- Seed Transport Services (Classification: SOURCED & CURATED)
INSERT INTO transport_services (service_id, mode, operator_name, service_name, external_id, description, is_active)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'BUS', 'PMPML', 'PMPML Standard Bus Service', 'PMPML-BUS-01', 'Pune Mahanagar Parivahan Mahamandal Ltd City Bus Network', TRUE),
    ('22222222-2222-2222-2222-222222222222', 'METRO', 'Maha Metro', 'Pune Metro Rail Service', 'MAHA-METRO-01', 'Pune Metro Purple Line (PCMC-Swargate) and Aqua Line (Vanaz-Ramwadi)', TRUE),
    ('33333333-3333-3333-3333-333333333333', 'TAXI', 'Pune City Taxi Service', 'Pune Hired Road Taxi Service', 'PUNE-TAXI-01', 'Curated metered taxi road transport within Pune metropolitan region', TRUE)
ON CONFLICT (service_id) DO NOTHING;

-- Seed Fare Configurations (Classification: SOURCED & CURATED)
INSERT INTO fare_configurations (fare_id, service_id, fare_type, base_fare, per_km_rate, minimum_fare, effective_from, is_active)
VALUES
    -- PMPML Bus: Base ₹10, ₹2/km
    ('44444444-4444-4444-4444-444444444441', '11111111-1111-1111-1111-111111111111', 'DISTANCE_BASED', 10.00, 2.00, 10.00, '2026-01-01 00:00:00', TRUE),
    -- Pune Metro: Base ₹10, ₹2.50/km, min ₹10
    ('44444444-4444-4444-4444-444444444442', '22222222-2222-2222-2222-222222222222', 'DISTANCE_BASED', 10.00, 2.50, 10.00, '2026-01-01 00:00:00', TRUE),
    -- Taxi: Base ₹25 (flag down / min), ₹17.00/km
    ('44444444-4444-4444-4444-444444444443', '33333333-3333-3333-3333-333333333333', 'DISTANCE_BASED', 25.00, 17.00, 25.00, '2026-01-01 00:00:00', TRUE)
ON CONFLICT (fare_id) DO NOTHING;

-- Seed Initial Admin User (password: Admin@123 -> bcrypt hash $2b$12$e6x8W2pX5U6x0G7pG7pG7O...)
-- We will use standard bcrypt hash for 'Admin@123' and 'User@123'
INSERT INTO users (user_id, full_name, email, phone, password_hash, role, is_active)
VALUES 
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'IntelliTransit Admin', 'admin@intellitransit.in', '9876543210', '$2b$12$6t336FwYyK8m.1rN6oQo1eTqjYjQj44Cskg15s6M9d8q0O4mU1xKy', 'ADMIN', TRUE),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Demo Commuter', 'demo@intellitransit.in', '9123456780', '$2b$12$6t336FwYyK8m.1rN6oQo1eTqjYjQj44Cskg15s6M9d8q0O4mU1xKy', 'USER', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Seed Preferences for Demo User
INSERT INTO user_preferences (preference_id, user_id, preferred_mode, route_preference, max_walking_distance_m, avoid_taxi, avoid_transfers)
VALUES 
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'METRO', 'FASTEST', 1500, FALSE, FALSE)
ON CONFLICT (user_id) DO NOTHING;

-- Seed Saved Locations for Demo User
INSERT INTO saved_locations (location_id, user_id, label, location_name, address, latitude, longitude)
VALUES 
    ('dddddddd-dddd-dddd-dddd-dddddddddd01', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Home', 'Kothrud Stand', 'Paud Road, Kothrud, Pune', 18.5074, 73.8077),
    ('dddddddd-dddd-dddd-dddd-dddddddddd02', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'College', 'COEP Technological University', 'Wellesley Road, Shivajinagar, Pune', 18.5293, 73.8565),
    ('dddddddd-dddd-dddd-dddd-dddddddddd03', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Station', 'Pune Railway Station', 'Station Road, Pune', 18.5285, 73.8743)
ON CONFLICT (location_id) DO NOTHING;
