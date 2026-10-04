# OpenTripPlanner 2 (OTP 2) Setup for IntelliTransit (Pune)

This directory hosts the OTP 2 routing engine configuration, Pune OSM road extract, and transit GTFS datasets.

## 1. Prerequisites
- **Java 17 or Java 21 JDK/JRE** installed and on the system `PATH`.
- Verified local Java version: `java -version`.

## 2. Directory Layout
```text
otp/
├── config/
│   ├── build-config.json     # Transit graph build rules
│   └── router-config.json    # Routing penalties & speeds
├── data/
│   ├── pune.osm.pbf          # OpenStreetMap street network for Pune
│   └── gtfs/                 # PMPML Bus & Pune Metro GTFS feeds
│       ├── pune_metro_gtfs.zip
│       └── pmpml_bus_gtfs.zip
├── otp-shaded.jar            # OTP 2 standalone executable JAR
├── start_otp.bat             # Windows execution script
└── README.md
```

## 3. Data Sources & Provenance
- **OpenStreetMap Pune Extract**: Sourced from Geofabrik / BBBike (`[18.35, 73.65, 18.70, 74.05]`).
- **Pune Metro GTFS**: Sourced & curated station locations and schedules for Line 1 (Purple Line) and Line 2 (Aqua Line).
- **PMPML Bus GTFS**: Public transit schedule dataset for major corridors in Pune.

## 4. Starting OTP 2
Run the batch script:
```cmd
cd otp
start_otp.bat
```
Or execute directly via Java:
```cmd
java -Xmx4G -jar otp-shaded.jar --build --serve data/
```
The router will be accessible at: `http://localhost:8080/otp/routers/default/plan`.
