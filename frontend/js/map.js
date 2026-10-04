/**
 * MapLibre GL JS Wrapper for IntelliTransit.
 * Renders interactive Pune map, markers, and mode-specific polyline geometries.
 */

export class MapManager {
    constructor(containerId = "map") {
        this.containerId = containerId;
        this.map = null;
        this.markers = [];
        this.routeLayerIds = [];
        this.puneCenter = [73.8567, 18.5204]; // [lng, lat] for Pune
        this.init();
    }

    init() {
        const container = document.getElementById(this.containerId);
        if (!container) return;

        // MapLibre GL JS initialization with OpenStreetMap raster tiles
        this.map = new maplibregl.Map({
            container: this.containerId,
            style: {
                version: 8,
                sources: {
                    "osm-tiles": {
                        type: "raster",
                        tiles: [
                            "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                        ],
                        tileSize: 256,
                        attribution: "&copy; OpenStreetMap Contributors"
                    }
                },
                layers: [
                    {
                        id: "osm-layer",
                        type: "raster",
                        source: "osm-tiles",
                        minzoom: 0,
                        maxzoom: 19
                    }
                ]
            },
            center: this.puneCenter,
            zoom: 12
        });

        // Add standard navigation controls (zoom, compass)
        this.map.addControl(new maplibregl.NavigationControl(), "top-right");

        this.map.on("load", () => {
            this.map.resize();
        });

        this.map.on("error", (e) => {
            console.warn("MapLibre map error:", e);
        });
    }

    clearMap() {
        // Remove markers
        this.markers.forEach(m => m.remove());
        this.markers = [];

        // Remove route layers and sources
        if (this.map && this.map.isStyleLoaded()) {
            this.routeLayerIds.forEach(id => {
                if (this.map.getLayer(id)) this.map.removeLayer(id);
                if (this.map.getSource(id)) this.map.removeSource(id);
            });
            this.routeLayerIds = [];
        }
    }

    renderRoute(itinerary) {
        if (!this.map) return;
        if (!this.map.isStyleLoaded()) {
            this.map.once("load", () => this.renderRoute(itinerary));
            return;
        }

        this.clearMap();

        const legs = itinerary.legs || [];
        if (legs.length === 0) return;

        const bounds = new maplibregl.LngLatBounds();
        const modeColors = {
            "WALK": "#6b7280",
            "BUS": "#16a34a",
            "METRO": "#2563eb",
            "TAXI": "#f59e0b"
        };

        legs.forEach((leg, index) => {
            const rawPoints = (leg.points && leg.points.length > 0) ? leg.points : [
                [leg.from_latitude, leg.from_longitude],
                [leg.to_latitude, leg.to_longitude]
            ];

            // Convert [lat, lng] -> [lng, lat] for MapLibre GeoJSON
            const coordinates = rawPoints.map(p => [p[1], p[0]]);
            coordinates.forEach(c => bounds.extend(c));

            const sourceId = `route-segment-${index}`;
            const color = modeColors[leg.mode] || "#3b82f6";
            const isDash = leg.mode === "WALK";

            if (this.map.getSource(sourceId)) {
                this.map.getSource(sourceId).setData({
                    type: "Feature",
                    properties: { mode: leg.mode },
                    geometry: { type: "LineString", coordinates }
                });
            } else {
                this.map.addSource(sourceId, {
                    type: "geojson",
                    data: {
                        type: "Feature",
                        properties: { mode: leg.mode },
                        geometry: { type: "LineString", coordinates }
                    }
                });

                this.map.addLayer({
                    id: sourceId,
                    type: "line",
                    source: sourceId,
                    layout: {
                        "line-join": "round",
                        "line-cap": "round"
                    },
                    paint: {
                        "line-color": color,
                        "line-width": isDash ? 4 : 6,
                        ...(isDash ? { "line-dasharray": [2, 2] } : {})
                    }
                });
            }

            this.routeLayerIds.push(sourceId);
        });

        // Add Origin Marker (Green)
        const firstLeg = legs[0];
        const elOrigin = document.createElement("div");
        elOrigin.className = "marker-origin";
        const originMarker = new maplibregl.Marker({ element: elOrigin })
            .setLngLat([firstLeg.from_longitude, firstLeg.from_latitude])
            .setPopup(new maplibregl.Popup().setText(`Start: ${firstLeg.from_name}`))
            .addTo(this.map);
        this.markers.push(originMarker);

        // Add Destination Marker (Red)
        const lastLeg = legs[legs.length - 1];
        const elDest = document.createElement("div");
        elDest.className = "marker-dest";
        const destMarker = new maplibregl.Marker({ element: elDest })
            .setLngLat([lastLeg.to_longitude, lastLeg.to_latitude])
            .setPopup(new maplibregl.Popup().setText(`Destination: ${lastLeg.to_name}`))
            .addTo(this.map);
        this.markers.push(destMarker);

        // Fit map bounds to show complete journey with padding
        if (!bounds.isEmpty()) {
            this.map.fitBounds(bounds, { padding: 40, maxZoom: 15 });
        }
    }
}

export default MapManager;
