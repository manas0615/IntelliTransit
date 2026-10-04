/**
 * IntelliTransit Journey Planner Controller.
 * Handles location autocomplete, preference toggles, itinerary card rendering, and MapLibre sync.
 */
import ApiClient from "./api.js";
import MapManager from "./map.js";
import { formatCurrency, formatDuration, formatDistance, escapeHTML, showError, debounce } from "./utils.js";

// Pune Landmarks Cache for Local Autocomplete
const PUNE_PRESET_LANDMARKS = [
    { name: "Pune Railway Station", latitude: 18.5285, longitude: 73.8743 },
    { name: "Shivajinagar Bus Stand", latitude: 18.5314, longitude: 73.8446 },
    { name: "Swargate Bus Stand", latitude: 18.5018, longitude: 73.8586 },
    { name: "Civil Court Metro Interchange", latitude: 18.5236, longitude: 73.8500 },
    { name: "COEP Technological University", latitude: 18.5293, longitude: 73.8565 },
    { name: "Kothrud Stand", latitude: 18.5074, longitude: 73.8077 },
    { name: "Kothrud Depot", latitude: 18.5074, longitude: 73.8077 },
    { name: "Hinjewadi Phase 1", latitude: 18.5912, longitude: 73.7389 },
    { name: "Magarpatta City", latitude: 18.5146, longitude: 73.9298 },
    { name: "Viman Nagar", latitude: 18.5679, longitude: 73.9143 },
    { name: "Pune Airport", latitude: 18.5822, longitude: 73.9197 },
    { name: "Katraj Bus Depot", latitude: 18.4575, longitude: 73.8677 },
    { name: "Hadapsar Gadital", latitude: 18.5013, longitude: 73.9348 },
    { name: "Baner Phata", latitude: 18.5590, longitude: 73.7868 }
];

export class PlannerController {
    constructor() {
        this.mapManager = new MapManager("map");
        this.currentItineraries = [];
        this.selectedItineraryIndex = 0;
        this.currentJourneyId = null;

        this.initUI();
    }

    initUI() {
        this.setupAutocomplete("origin-input", "origin-lat", "origin-lng", "origin-suggestions");
        this.setupAutocomplete("dest-input", "dest-lat", "dest-lng", "dest-suggestions");

        const swapBtn = document.getElementById("swap-locations-btn");
        if (swapBtn) {
            swapBtn.addEventListener("click", () => this.swapLocations());
        }

        const form = document.getElementById("planner-form");
        if (form) {
            form.addEventListener("submit", (e) => this.handlePlanSubmit(e));
        }

        this.loadUserSavedPlaces();
    }

    async loadUserSavedPlaces() {
        if (!ApiClient.getToken()) return;
        try {
            const resp = await ApiClient.get("/users/locations", {}, { skipAuthRedirect: true });
            const locs = resp.data.locations || [];
            const quickContainer = document.getElementById("quick-locations");
            if (quickContainer && locs.length > 0) {
                quickContainer.innerHTML = `
                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 6px;">Saved Places:</div>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        ${locs.map(l => `
                            <button type="button" class="btn btn-outline btn-sm quick-loc-btn" 
                                data-name="${escapeHTML(l.location_name)}" 
                                data-lat="${l.latitude}" 
                                data-lng="${l.longitude}">
                                📍 ${escapeHTML(l.label)}
                            </button>
                        `).join("")}
                    </div>
                `;

                quickContainer.querySelectorAll(".quick-loc-btn").forEach(btn => {
                    btn.addEventListener("click", (e) => {
                        const target = e.currentTarget;
                        const destInput = document.getElementById("dest-input");
                        const destLat = document.getElementById("dest-lat");
                        const destLng = document.getElementById("dest-lng");
                        if (destInput && destLat && destLng) {
                            destInput.value = target.dataset.name;
                            destLat.value = target.dataset.lat;
                            destLng.value = target.dataset.lng;
                        }
                    });
                });
            }
        } catch {
            // Guest mode
        }
    }

    setupAutocomplete(inputId, latId, lngId, suggestionsId) {
        const input = document.getElementById(inputId);
        const latInput = document.getElementById(latId);
        const lngInput = document.getElementById(lngId);
        const list = document.getElementById(suggestionsId);
        if (!input || !list) return;

        const handleSearch = debounce((query) => {
            const q = query.toLowerCase().trim();
            if (!q) {
                list.style.display = "none";
                return;
            }

            const matches = PUNE_PRESET_LANDMARKS.filter(lm => lm.name.toLowerCase().includes(q));
            if (matches.length === 0) {
                list.style.display = "none";
                return;
            }

            list.innerHTML = matches.map(m => `
                <div class="suggestion-item" data-name="${escapeHTML(m.name)}" data-lat="${m.latitude}" data-lng="${m.longitude}"
                     style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid var(--border-color); font-size: 0.9rem;">
                    📍 <strong>${escapeHTML(m.name)}</strong>
                </div>
            `).join("");

            list.style.display = "block";

            list.querySelectorAll(".suggestion-item").forEach(item => {
                item.addEventListener("click", () => {
                    input.value = item.dataset.name;
                    latInput.value = item.dataset.lat;
                    lngInput.value = item.dataset.lng;
                    list.style.display = "none";
                });
            });
        }, 150);

        input.addEventListener("input", (e) => handleSearch(e.target.value));
        document.addEventListener("click", (e) => {
            if (!input.contains(e.target) && !list.contains(e.target)) {
                list.style.display = "none";
            }
        });
    }

    swapLocations() {
        const origInput = document.getElementById("origin-input");
        const origLat = document.getElementById("origin-lat");
        const origLng = document.getElementById("origin-lng");

        const destInput = document.getElementById("dest-input");
        const destLat = document.getElementById("dest-lat");
        const destLng = document.getElementById("dest-lng");

        const tempName = origInput.value;
        const tempLat = origLat.value;
        const tempLng = origLng.value;

        origInput.value = destInput.value;
        origLat.value = destLat.value;
        origLng.value = destLng.value;

        destInput.value = tempName;
        destLat.value = tempLat;
        destLng.value = tempLng;
    }

    async handlePlanSubmit(e) {
        e.preventDefault();
        const btn = document.getElementById("plan-submit-btn");
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span> Finding Routes...';

        const originName = document.getElementById("origin-input").value;
        let originLat = parseFloat(document.getElementById("origin-lat").value);
        let originLng = parseFloat(document.getElementById("origin-lng").value);

        const destName = document.getElementById("dest-input").value;
        let destLat = parseFloat(document.getElementById("dest-lat").value);
        let destLng = parseFloat(document.getElementById("dest-lng").value);

        // Fallback auto-resolve from Pune landmarks if typed directly
        if (isNaN(originLat) || isNaN(originLng)) {
            const oMatch = PUNE_PRESET_LANDMARKS.find(lm => 
                lm.name.toLowerCase().includes(originName.toLowerCase()) || 
                originName.toLowerCase().includes(lm.name.toLowerCase())
            );
            if (oMatch) {
                originLat = oMatch.latitude;
                originLng = oMatch.longitude;
                document.getElementById("origin-lat").value = oMatch.latitude;
                document.getElementById("origin-lng").value = oMatch.longitude;
            }
        }

        if (isNaN(destLat) || isNaN(destLng)) {
            const dMatch = PUNE_PRESET_LANDMARKS.find(lm => 
                lm.name.toLowerCase().includes(destName.toLowerCase()) || 
                destName.toLowerCase().includes(lm.name.toLowerCase())
            );
            if (dMatch) {
                destLat = dMatch.latitude;
                destLng = dMatch.longitude;
                document.getElementById("dest-lat").value = dMatch.latitude;
                document.getElementById("dest-lng").value = dMatch.longitude;
            }
        }

        if (isNaN(originLat) || isNaN(originLng) || isNaN(destLat) || isNaN(destLng)) {
            showError("Please select locations within Pune from the autocomplete suggestions.");
            btn.disabled = false;
            btn.innerHTML = '🔍 Find Routes';
            return;
        }

        const preference = document.getElementById("route-pref-select").value;
        const avoidTaxi = document.getElementById("avoid-taxi-toggle").checked;

        const payload = {
            origin: {
                name: originName,
                latitude: originLat,
                longitude: originLng
            },
            destination: {
                name: destName,
                latitude: destLat,
                longitude: destLng
            },
            preferences: {
                route_preference: preference,
                avoid_taxi: avoidTaxi
            }
        };

        try {
            const resp = await ApiClient.post("/journeys/plan", payload);
            const data = resp.data;
            this.currentItineraries = data.itineraries || [];
            this.currentJourneyId = data.journey_id;

            this.renderResults();
        } catch (err) {
            showError(err.message || "Failed to find routes.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = '🔍 Find Routes';
        }
    }

    renderResults() {
        const container = document.getElementById("results-container");
        if (!container) return;

        if (this.currentItineraries.length === 0) {
            container.innerHTML = `
                <div class="card" style="text-align:center; padding: 32px 16px;">
                    <h3>No Routes Found</h3>
                    <p>No feasible transit connections found for these points. Try loosening preference constraints.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <h3 style="margin-bottom: 12px;">Available Routes (${this.currentItineraries.length})</h3>
            <div id="itinerary-cards-list"></div>
            <div id="selected-itinerary-detail"></div>
        `;

        const cardsList = document.getElementById("itinerary-cards-list");

        cardsList.innerHTML = this.currentItineraries.map((it, idx) => `
            <div class="route-card ${idx === 0 ? 'selected' : ''}" data-index="${idx}">
                <div class="route-header">
                    <span class="route-badge">${escapeHTML(it.badge || `Option ${idx+1}`)}</span>
                    <span style="font-size: 1.15rem; font-weight: 800; color: var(--primary);">${formatCurrency(it.estimated_fare)}</span>
                </div>
                <div class="route-metrics">
                    <div class="metric-item">
                        <span class="metric-label">Duration</span>
                        <span class="metric-value">⏱️ ${formatDuration(it.total_duration_min)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Walking</span>
                        <span class="metric-value">🚶 ${formatDistance(it.walking_distance_m)}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Transfers</span>
                        <span class="metric-value">🔄 ${it.transfers_count}</span>
                    </div>
                </div>
                <div class="route-modes-chain">
                    ${(it.legs || []).map(leg => `
                        <span class="badge badge-${leg.mode.toLowerCase()}">${leg.mode}</span>
                    `).join(" → ")}
                </div>
            </div>
        `).join("");

        cardsList.querySelectorAll(".route-card").forEach(card => {
            card.addEventListener("click", (e) => {
                const idx = parseInt(e.currentTarget.dataset.index, 10);
                this.selectItinerary(idx);
            });
        });

        // Default select top ranked option
        this.selectItinerary(0);
    }

    selectItinerary(index) {
        this.selectedItineraryIndex = index;
        const itinerary = this.currentItineraries[index];
        if (!itinerary) return;

        // Highlight selected card
        document.querySelectorAll(".route-card").forEach((card, idx) => {
            if (idx === index) card.classList.add("selected");
            else card.classList.remove("selected");
        });

        // Render on MapLibre
        this.mapManager.renderRoute(itinerary);

        // Render detailed leg breakdown
        const detailContainer = document.getElementById("selected-itinerary-detail");
        if (detailContainer) {
            detailContainer.innerHTML = `
                <div class="card" style="margin-top: 16px; border-top: 3px solid var(--primary);">
                    <h4 style="margin-bottom: 8px;">Journey Leg Breakdown</h4>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px;">${escapeHTML(itinerary.recommendation_reason || "")}</p>
                    <div class="legs-list" style="display: flex; flex-direction: column; gap: 12px;">
                        ${(itinerary.legs || []).map((leg, lIdx) => `
                            <div style="border-left: 3px solid var(--mode-${leg.mode.toLowerCase()}); padding-left: 12px; position: relative;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <span class="badge badge-${leg.mode.toLowerCase()}">${leg.mode}</span>
                                        <strong style="font-size: 0.95rem; margin-left: 6px;">${escapeHTML(leg.from_name)} → ${escapeHTML(leg.to_name)}</strong>
                                    </div>
                                    <span style="font-weight: 700; font-size: 0.9rem;">${formatCurrency(leg.fare)}</span>
                                </div>
                                <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                    ${leg.route_name ? escapeHTML(leg.route_name) + " • " : ""}${formatDuration(leg.duration_min)} • ${formatDistance(leg.distance_meters)}
                                </div>
                                ${leg.is_ticketable ? `
                                    <button class="btn btn-primary btn-sm buy-leg-ticket-btn" 
                                        data-leg-id="${leg.leg_id || ''}" 
                                        data-journey-id="${leg.journey_id || this.currentJourneyId || ''}"
                                        data-fare="${leg.fare}"
                                        data-origin="${escapeHTML(leg.from_name)}"
                                        data-destination="${escapeHTML(leg.to_name)}"
                                        style="margin-top: 8px;">
                                        🎟️ Buy Ticket (${formatCurrency(leg.fare)})
                                    </button>
                                ` : ''}
                            </div>
                        `).join("")}
                    </div>
                </div>
            `;

            detailContainer.querySelectorAll(".buy-leg-ticket-btn").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    const target = e.currentTarget;
                    if (!ApiClient.getToken()) {
                        showError("Please sign in or register to purchase tickets.");
                        setTimeout(() => window.location.href = "/login.html", 1200);
                        return;
                    }
                    const legId = target.dataset.legId;
                    const journeyId = target.dataset.journeyId;
                    if (legId && journeyId) {
                        window.location.href = `/tickets.html?action=buy&journey_id=${journeyId}&leg_id=${legId}`;
                    } else {
                        showError("Saved journey reference required to buy ticket.");
                    }
                });
            });
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.plannerCtrl = new PlannerController();
});
