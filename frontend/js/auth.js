/**
 * IntelliTransit Authentication & Navigation State Manager.
 */
import ApiClient from "./api.js";
import { showSuccess, showError } from "./utils.js";

export class AuthManager {
    static getCurrentUser() {
        const userStr = localStorage.getItem("intellitransit_user");
        try {
            return userStr ? JSON.parse(userStr) : null;
        } catch {
            return null;
        }
    }

    static setCurrentUser(user) {
        if (user) {
            localStorage.setItem("intellitransit_user", JSON.stringify(user));
        } else {
            localStorage.removeItem("intellitransit_user");
        }
    }

    static isAuthenticated() {
        return !!ApiClient.getToken();
    }

    static async login(email, password) {
        try {
            const resp = await ApiClient.post("/auth/login", { email, password });
            const data = resp.data;
            ApiClient.setToken(data.token);
            AuthManager.setCurrentUser(data.user);
            showSuccess("Welcome back, " + data.user.full_name);
            return data;
        } catch (error) {
            showError(error.message || "Invalid credentials.");
            throw error;
        }
    }

    static async register(fullName, email, password, phone = null) {
        try {
            const resp = await ApiClient.post("/auth/register", {
                full_name: fullName,
                email,
                password,
                phone: phone || undefined
            });
            const data = resp.data;
            ApiClient.setToken(data.token);
            AuthManager.setCurrentUser(data.user);
            showSuccess("Account created successfully!");
            return data;
        } catch (error) {
            showError(error.message || "Registration failed.");
            throw error;
        }
    }

    static logout() {
        ApiClient.removeToken();
        AuthManager.setCurrentUser(null);
        showSuccess("Logged out successfully.");
        setTimeout(() => {
            window.location.href = "/index.html";
        }, 500);
    }

    static renderNavbar() {
        const navContainer = document.getElementById("navbar-links");
        if (!navContainer) return;

        const isAuth = AuthManager.isAuthenticated();
        const user = AuthManager.getCurrentUser();
        const isAdmin = user && user.role === "ADMIN";

        let linksHtml = `
            <li><a href="/planner.html" class="nav-link">Plan Journey</a></li>
            <li><a href="/ai-assistant.html" class="nav-link">AI Assistant</a></li>
        `;

        if (isAuth) {
            linksHtml += `
                <li><a href="/tickets.html" class="nav-link">My Tickets</a></li>
                <li><a href="/passes.html" class="nav-link">Passes</a></li>
                <li><a href="/history.html" class="nav-link">History</a></li>
                <li><a href="/profile.html" class="nav-link">Profile</a></li>
            `;
            if (isAdmin) {
                linksHtml += `
                    <li><a href="/admin.html" class="nav-link" style="color: var(--accent); font-weight: bold;">Admin</a></li>
                    <li><a href="/validator.html" class="nav-link" style="color: var(--secondary); font-weight: bold;">Validator</a></li>
                `;
            }
            linksHtml += `
                <li><button id="logout-btn" class="btn btn-outline btn-sm">Logout</button></li>
            `;
        } else {
            linksHtml += `
                <li><a href="/login.html" class="nav-link">Login</a></li>
                <li><a href="/register.html" class="btn btn-primary btn-sm">Sign Up</a></li>
            `;
        }

        navContainer.innerHTML = linksHtml;

        const logoutBtn = document.getElementById("logout-btn");
        if (logoutBtn) {
            logoutBtn.addEventListener("click", () => AuthManager.logout());
        }
    }

    static getUser() {
        return AuthManager.getCurrentUser();
    }

    static async initAuthNav() {
        AuthManager.renderNavbar();
    }
}

// Automatically render navigation bar when DOM loads
document.addEventListener("DOMContentLoaded", () => {
    AuthManager.renderNavbar();
});

export const auth = AuthManager;
export default AuthManager;
