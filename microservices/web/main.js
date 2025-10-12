// The orchestrator script that ties together various modules for the game client

import { renderBattle, renderGatchaResult } from './renderer.js';
import { loadInventoryView, handleRelease } from './inventory.js';
import { loadTradeMenu, renderCreateTradeForm, renderFulfillTradeForm, handleCreateTrade, handleFulfillTrade, toggleTradeSelection } from './trade.js';
import { enterMatchmakingQueue, handleBattleEndConfirmation, setupSocketListeners } from './battle.js';
import { loadDashboard } from './user.js';
import { API } from './api.js'; // Ensure api.js is imported for generic calls

const actionContainer = document.getElementById('action-container');
window.actionContainer = actionContainer; // Make available globally for modules

// --- Global Functions (Attached to window for inline HTML/module calls) ---

// Expose these domain-specific functions globally for HTML onclick handlers
window.handleRelease = handleRelease;
window.loadTradeMenu = loadTradeMenu;
window.renderCreateTradeForm = renderCreateTradeForm;
window.renderFulfillTradeForm = renderFulfillTradeForm;
window.handleCreateTrade = handleCreateTrade;
window.handleFulfillTrade = handleFulfillTrade;
window.toggleTradeSelection = toggleTradeSelection;
window.loadDashboard = loadDashboard;
window.handleBattleEndConfirmation = handleBattleEndConfirmation;

// Global Socket.IO instance and state
window.socket = null; 
window.battleState = { inQueue: false };

// --- Main Content Loader ---

export async function loadContent(endpoint) {
    let content = '';
    window.actionContainer.innerHTML = '<h2>Loading...</h2>'; // Show loading screen

    try {
        // Direct API calls based on endpoint for non-realtime services
        if (endpoint === 'dashboard') {
            const data = await API.getDashboard();
            content = loadDashboard(data); // loadDashboard handles rendering
            return;
        } else if (endpoint === 'inventory') {
            // Inventory module handles its own fetching/rendering
            await loadInventoryView(); 
            return;
        } else if (endpoint === 'gatcha') {
            const data = await API.runGatcha();
            content = renderGatchaResult(data);
        } else if (endpoint === 'trade') {
            // Trade module handles its own fetching/rendering
            await loadTradeMenu(); 
            return;
        } else if (endpoint === 'battle') {
            // Battle requires pre-queue data, then queue entry
            const data = await API.getBattleData();
            content = renderBattle(data);
        } else {
             content = '<h2>Action Not Implemented</h2>';
        }

        actionContainer.innerHTML = content;
        
    } catch (error) {
        // Display user-friendly error messages
        const message = error.message || "Could not connect to the server or process the request.";
        actionContainer.innerHTML = `<h2>Server Error 🚨</h2><p>${message}</p>`;
        console.error("Fetch error:", error);
    }
}
window.loadContent = loadContent; // Make available globally

// --- Initialization ---
function init() {
    // Initialize Socket.IO connection
    // IMPORTANT: Socket.IO must connect to the Nginx proxy (localhost:5000), 
    // which will route the /socket.io path to the battle service.
    const socket = io('http://localhost:5000', {path: '/socket.io/'});

    window.socket = socket; 

    // Pass the socket instance to the battle module for event binding
    setupSocketListeners(window.socket);

    // Set up button listeners and load dashboard
    const dynamicButtons = document.querySelectorAll('.menu-container button');
    dynamicButtons.forEach(button => {
        button.addEventListener('click', () => {
            const endpoint = button.getAttribute('data-endpoint');
            window.loadContent(endpoint); 
        });
    });

    // Load the dashboard when the page first loads
    loadDashboard();
}

document.addEventListener('DOMContentLoaded', init);
