// --- API Configuration ---
// All requests are proxied through the Nginx layer on port 5000 (default)
// Nginx will route the path (e.g., /api/auth/) to the correct internal service.
const API_BASE = 'http://localhost:5000/api'; 
const API_AUTH = '/auth'; 
const API_INVENTORY = '/inventory';
const API_GATCHA = '/gatcha';
const API_TRADE = '/trade';
const API_BATTLE = '/battle'; 

async function request(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
        // IMPORTANT: Credentials must be included for session management
        credentials: 'include' 
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        
        // Handle no content response (e.g., successful logout)
        if (response.status === 204) {
             return { message: 'Action successful' };
        }
        
        // Try to parse JSON response
        const jsonResponse = await response.json().catch(() => ({ message: 'No JSON response received' }));
        
        if (!response.ok) {
            // Throw error for status codes like 400, 401, 404, etc.
            throw new Error(jsonResponse.message || `API Error: ${response.status}`);
        }
        return jsonResponse;
    } catch (error) {
        console.error("API Request Failed:", url, error);
        throw error;
    }
}

export const API = {
    // --- Auth Service (Auth Service uses path /api/auth/...) ---
    login: (email, password) => request(`${API_BASE}${API_AUTH}/login`, 'POST', { email, password }),
    register: (email, password) => request(`${API_BASE}${API_AUTH}/register`, 'POST', { email, password }),
    logout: () => request(`${API_BASE}${API_AUTH}/logout`),
    getDashboard: () => request(`${API_BASE}${API_AUTH}/dashboard`),

    // --- Inventory Service (Inventory Service uses path /api/inventory/...) ---
    getInventory: () => request(`${API_BASE}${API_INVENTORY}`),
    releaseMonster: (monster_id) => request(`${API_BASE}${API_INVENTORY}/release`, 'POST', { monster_id }),

    // --- Gatcha Service (Gatcha Service uses path /api/gatcha/...) ---
    runGatcha: () => request(`${API_BASE}${API_GATCHA}`),

    // --- Trade Service (Trade Service uses path /api/trade/...) ---
    getTrades: () => request(`${API_BASE}${API_TRADE}`),
    createTrade: (monster_id, desired_species) => request(`${API_BASE}${API_TRADE}`, 'POST', { monster_id, desired_species }),
    fulfillTrade: (trade_id, accepting_monster_id) => request(`${API_BASE}${API_TRADE}/${trade_id}`, 'POST', { accepting_monster_id }),

    // --- Battle Service (Battle Service uses path /api/battle/...) ---
    getBattleData: () => request(`${API_BASE}${API_BATTLE}/data`),
};
