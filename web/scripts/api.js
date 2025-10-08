const BASE_URL = 'http://localhost:5000/api/';

/**
 * Handles all generic GET/POST API calls.
 * @param {string} endpoint - The API endpoint (e.g., 'inventory', 'gatcha').
 * @param {string} method - The HTTP method ('GET' or 'POST').
 * @param {Object} bodyData - Data to send with a POST request.
 * @returns {Promise<Object>} - The JSON response data.
 */
async function callApi(endpoint, method = 'GET', bodyData = null) {
    const url = BASE_URL + endpoint;
    const fetchOptions = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (bodyData && method === 'POST') {
        fetchOptions.body = JSON.stringify(bodyData);
    }

    const response = await fetch(url, fetchOptions);
    
    if (!response.ok) {
        // Fetch the error message from the server if available
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
}

// Specific API functions
export const API = {
    getInventory: () => callApi('inventory'),
    runGatcha: () => callApi('gatcha', 'POST'),
    getTradeData: () => callApi('trade'),
    getBattleData: () => callApi('battle'),
    
    releasePokemon: (ids) => callApi('release', 'POST', { ids }),
    
    createTrade: (offering_ids, looking_for_count) => 
        callApi('trade/create', 'POST', { offering_ids, looking_for_count }),
        
    fulfillTrade: (trade_id, fulfilling_ids) => 
        callApi('trade/fulfill', 'POST', { trade_id, fulfilling_ids })
};