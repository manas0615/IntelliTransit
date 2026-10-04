/**
 * IntelliTransit Central API Client.
 * Automatically manages Authorization headers and 401 redirect handling.
 */
import { showError } from "./utils.js";

const API_BASE = "/api";

export class ApiClient {
    static getToken() {
        return localStorage.getItem("intellitransit_token");
    }

    static setToken(token) {
        if (token) {
            localStorage.setItem("intellitransit_token", token);
        } else {
            localStorage.removeItem("intellitransit_token");
        }
    }

    static removeToken() {
        localStorage.removeItem("intellitransit_token");
    }

    static async request(endpoint, options = {}) {
        const cleanEndpoint = endpoint.startsWith('/api') ? endpoint.slice(4) : endpoint;
        const url = `${API_BASE}${cleanEndpoint.startsWith('/') ? cleanEndpoint : '/' + cleanEndpoint}`;
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        const token = ApiClient.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json().catch(() => null);

            if (response.status === 401) {
                // Token expired or invalid
                ApiClient.removeToken();
                const path = window.location.pathname;
                const isAuthPage = path.endsWith("login.html") || path.endsWith("register.html");
                const isPublicPage = path.endsWith("index.html") || path.endsWith("planner.html") || path === "/" || path === "";

                if (!options.skipAuthRedirect && !isAuthPage && !isPublicPage) {
                    showError("Session expired. Please log in again.");
                    setTimeout(() => {
                        window.location.href = "/login.html";
                    }, 1000);
                }
                throw new Error(data?.error?.message || "Authentication required");
            }

            if (!response.ok) {
                const errorMsg = data?.error?.message || `Request failed with status ${response.status}`;
                const err = new Error(errorMsg);
                err.status = response.status;
                err.code = data?.error?.code;
                err.details = data?.error?.details;
                throw err;
            }

            return data;
        } catch (error) {
            console.error("API Client Error:", error);
            throw error;
        }
    }

    static get(endpoint, params = {}, options = {}) {
        const url = new URL(endpoint, window.location.origin);
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });
        const cleanPath = url.pathname.replace(/^\/api/, "") + url.search;
        return ApiClient.request(cleanPath, { method: "GET", ...options });
    }

    static post(endpoint, body = {}, options = {}) {
        return ApiClient.request(endpoint, {
            method: "POST",
            body: JSON.stringify(body),
            ...options
        });
    }

    static put(endpoint, body = {}, options = {}) {
        return ApiClient.request(endpoint, {
            method: "PUT",
            body: JSON.stringify(body),
            ...options
        });
    }

    static delete(endpoint, options = {}) {
        return ApiClient.request(endpoint, { method: "DELETE", ...options });
    }
}

export const api = ApiClient;
export default ApiClient;
