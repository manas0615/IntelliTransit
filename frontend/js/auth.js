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

        const path = window.location.pathname.toLowerCase();
        const isAuthPage = path.endsWith("/login.html") || 
                           path.endsWith("/register.html") || 
                           path.endsWith("/login") || 
                           path.endsWith("/register");

        const isPlanner = path.includes("planner");
        const isAi = path.includes("ai-assistant");
        const isTickets = path.includes("tickets");
        const isPasses = path.includes("passes");
        const isHistory = path.includes("history");
        const isProfile = path.includes("profile");
        const isAdminPage = path.includes("admin");
        const isValidator = path.includes("validator");
        const isLogin = path.includes("login");
        const isRegister = path.includes("register");

        let linksHtml = `
            <li><a href="/planner.html" class="nav-link ${isPlanner ? 'active' : ''}">Plan Journey</a></li>
            <li><a href="/ai-assistant.html" class="nav-link ${isAi ? 'active' : ''}">AI Assistant</a></li>
        `;

        if (isAuth && !isAuthPage) {
            if (isAdmin) {
                linksHtml += `
                    <li><a href="/admin.html" class="nav-link ${isAdminPage ? 'active' : ''}">Dashboard</a></li>
                    <li><a href="/validator.html" class="nav-link ${isValidator ? 'active' : ''}">Validator</a></li>
                `;
            } else {
                linksHtml += `
                    <li><a href="/tickets.html" class="nav-link ${isTickets ? 'active' : ''}">My Tickets</a></li>
                    <li><a href="/passes.html" class="nav-link ${isPasses ? 'active' : ''}">Passes</a></li>
                    <li><a href="/history.html" class="nav-link ${isHistory ? 'active' : ''}">History</a></li>
                `;
            }
            linksHtml += `
                <li><a href="/profile.html" class="nav-link ${isProfile ? 'active' : ''}">Profile</a></li>
                <li><button id="logout-btn" class="btn btn-outline btn-sm">Logout</button></li>
            `;
        } else {
            linksHtml += `
                <li><a href="/login.html" class="nav-link ${isLogin ? 'active' : ''}">Login</a></li>
                <li><a href="/register.html" class="btn btn-primary btn-sm ${isRegister ? 'active' : ''}">Sign Up</a></li>
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
