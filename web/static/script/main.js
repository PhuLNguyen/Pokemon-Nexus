// The orchestrator script that ties together various modules for the game client

import { renderBattle, renderGatchaResult } from './renderer.js';
import { loadInventoryView, handleRelease } from './inventory.js';
import { loadTradeMenu, renderCreateTradeForm, renderFulfillTradeForm, handleCreateTrade, handleFulfillTrade, toggleTradeSelection } from './trade.js';
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


/**
 * Main function to load content based on the button clicked.
 * It now delegates domain logic to the respective module files.
 * @param {string} endpoint - The data-endpoint attribute from the button.
 */
window.loadContent = async function(endpoint) {
    actionContainer.innerHTML = '<h2>Loading...</h2>';
    
    try {
        let content = '';

        if (endpoint === 'inventory' || endpoint === 'release') {
            // Inventory logic is handled by inventory.js
            return loadInventoryView();
        }
        
        if (endpoint === 'trade') {
            // Trade logic is handled by trade.js
            return loadTradeMenu();
        }

        if (endpoint === 'gatcha') {
            // Gatcha is a simple API call and render, kept here for flow
            const data = await API.runGatcha();
            content = renderGatchaResult(data);
        } else if (endpoint === 'battle') {
            const data = await API.getBattleData();
            content = renderBattle(data);
        } else {
             content = '<h2>Action Not Implemented</h2>';
        }

        actionContainer.innerHTML = content;

    } catch (error) {
        actionContainer.innerHTML = `<h2>Server Error 🚨</h2><p>Could not connect to the server or process the request.</p><p>Error: ${error.message}</p>`;
        console.error("Fetch error:", error);
    }
}

// --- Initialization ---

function init() {
    const dynamicButtons = document.querySelectorAll('.menu-container button');
    dynamicButtons.forEach(button => {
        button.addEventListener('click', () => {
            const endpoint = button.getAttribute('data-endpoint');
            window.loadContent(endpoint); 
        });
    });
}

document.addEventListener('DOMContentLoaded', init);