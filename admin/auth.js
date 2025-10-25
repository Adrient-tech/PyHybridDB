// Authentication Module for PyHybridDB Admin Panel

const AUTH_TOKEN_KEY = 'pyhybriddb_token';
const AUTH_USER_KEY = 'pyhybriddb_user';

// Authentication state
let currentToken = null;
let currentUser = null;

// Initialize authentication on page load
function initAuth() {
    // Check for existing token
    currentToken = localStorage.getItem(AUTH_TOKEN_KEY);
    currentUser = JSON.parse(localStorage.getItem(AUTH_USER_KEY) || 'null');
    
    if (currentToken && currentUser) {
        showMainApp();
    } else {
        showLoginForm();
    }
}

// Show login form
function showLoginForm() {
    document.getElementById('login-container').style.display = 'flex';
    document.getElementById('app-container').style.display = 'none';
}

// Show main app
function showMainApp() {
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('app-container').style.display = 'block';
    
    // Update user info in header
    if (currentUser) {
        document.getElementById('user-name').textContent = currentUser.username;
        document.getElementById('user-role').textContent = currentUser.role;
    }
}

// Login function
async function login() {
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    if (!username || !password) {
        errorDiv.textContent = 'Please enter username and password';
        errorDiv.style.display = 'block';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Store token and user info
            currentToken = data.access_token;
            currentUser = data.user;
            
            localStorage.setItem(AUTH_TOKEN_KEY, currentToken);
            localStorage.setItem(AUTH_USER_KEY, JSON.stringify(currentUser));
            
            // Clear form
            document.getElementById('login-username').value = '';
            document.getElementById('login-password').value = '';
            errorDiv.style.display = 'none';
            
            // Show main app
            showMainApp();
            loadDashboard();
            
        } else {
            const error = await response.json();
            errorDiv.textContent = error.detail || 'Login failed';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorDiv.textContent = 'Connection error. Please try again.';
        errorDiv.style.display = 'block';
    }
}

// Logout function
function logout() {
    if (confirm('Are you sure you want to logout?')) {
        currentToken = null;
        currentUser = null;
        
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(AUTH_USER_KEY);
        
        showLoginForm();
    }
}

// Get authorization headers
function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (currentToken) {
        headers['Authorization'] = `Bearer ${currentToken}`;
    }
    
    return headers;
}

// Authenticated fetch wrapper
async function authenticatedFetch(url, options = {}) {
    // Add authorization header
    if (!options.headers) {
        options.headers = {};
    }
    
    if (currentToken) {
        options.headers['Authorization'] = `Bearer ${currentToken}`;
    }
    
    if (!options.headers['Content-Type']) {
        options.headers['Content-Type'] = 'application/json';
    }
    
    try {
        const response = await fetch(url, options);
        
        // Check for authentication errors
        if (response.status === 401) {
            // Token expired or invalid
            showAlert('error', 'Session expired. Please login again.');
            logout();
            return null;
        }
        
        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Handle Enter key in login form
document.addEventListener('DOMContentLoaded', () => {
    const passwordInput = document.getElementById('login-password');
    if (passwordInput) {
        passwordInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                login();
            }
        });
    }
});
