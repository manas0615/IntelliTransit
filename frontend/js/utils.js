/**
 * IntelliTransit Shared Frontend Utilities.
 */

// DOM escaping to prevent XSS
export function escapeHTML(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Currency formatter for INR
export function formatCurrency(amount) {
    const val = parseFloat(amount) || 0.0;
    return `₹${val.toFixed(2)}`;
}

// Duration formatter
export function formatDuration(minutes) {
    const mins = parseInt(minutes, 10) || 0;
    if (mins < 60) {
        return `${mins} min`;
    }
    const hrs = Math.floor(mins / 60);
    const rem = mins % 60;
    return rem > 0 ? `${hrs}h ${rem}m` : `${hrs}h`;
}

// Distance formatter
export function formatDistance(meters) {
    const m = parseFloat(meters) || 0.0;
    if (m < 1000) {
        return `${Math.round(m)}m`;
    }
    return `${(m / 1000).toFixed(1)} km`;
}

// Toast notification helper
export function showToast(message, type = "info", duration = 4000) {
    let container = document.getElementById("toast-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-container";
        document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100%)";
        setTimeout(() => toast.remove(), 200);
    }, duration);
}

export function showError(message) {
    showToast(message, "error");
}

export function showSuccess(message) {
    showToast(message, "success");
}

// Debounce helper for autocomplete
export function debounce(func, wait = 250) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Date/Time formatter
export function formatDateTime(dateStr) {
    if (!dateStr) return "N/A";
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return String(dateStr);
    return d.toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });
}
