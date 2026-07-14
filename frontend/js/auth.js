// frontend/js/auth.js
// This file handles login session management, JWT decoding with base64, and route guards.

/**
 * Decodes the payload portion of a JSON Web Token (JWT) in pure JavaScript.
 * A JWT is formatted as: Header.Payload.Signature
 * 
 * @param {string} token - The raw JWT string.
 * @returns {object|null} - The parsed JSON claims payload, or null if invalid.
 */
function parseJwt(token) {
    try {
        // Extract the payload (middle segment)
        const base64Url = token.split('.')[1];
        
        // Convert URL-safe base64 characters to standard base64 characters
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        
        // Calculate the required padding to make length a multiple of 4
        // Browser atob() throws an error if length is not a multiple of 4
        const padding = '='.repeat((4 - (base64.length % 4)) % 4);
        const base64WithPadding = base64 + padding;
        
        // Decode base64 to string
        const jsonPayload = decodeURIComponent(window.atob(base64WithPadding).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        
        // Return parsed JSON object
        return JSON.parse(jsonPayload);
    } catch (error) {
        console.error("Failed to parse JWT token:", error);
        return null;
    }
}

/**
 * Reads the active login session from localStorage and checks if it is expired.
 * 
 * @returns {object|null} - Decoded user details { id, name, role } or null.
 */
function getAuthUser() {
    const token = localStorage.getItem("access_token");
    if (!token) {
        return null;
    }
    
    const payload = parseJwt(token);
    if (!payload) {
        return null;
    }
    
    // Check expiration timestamp (payload.exp is in seconds since epoch)
    const currentUnixTime = Math.floor(Date.now() / 1000);
    if (payload.exp && payload.exp < currentUnixTime) {
        console.warn("User session has expired. Clearing token...");
        localStorage.removeItem("access_token");
        return null;
    }
    
    // Return structured user details
    return {
        id: parseInt(payload.sub),
        name: payload.name,
        role: payload.role
    };
}

/**
 * Standard logout function. Clears local storage and redirects to the login page.
 */
function logoutUser() {
    localStorage.removeItem("access_token");
    window.location.href = "login.html";
}

/**
 * Guard function for the dashboard page.
 * Forces the user to the login screen if they aren't authenticated.
 */
function requireAuth() {
    const user = getAuthUser();
    if (!user) {
        window.location.href = "login.html";
    }
    return user;
}

/**
 * Guard function for the login page.
 * Forces authenticated users directly to the dashboard to avoid re-logging in.
 */
function requireGuest() {
    const user = getAuthUser();
    if (user) {
        window.location.href = "dashboard.html";
    }
}
