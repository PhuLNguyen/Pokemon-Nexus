import { API } from './api.js';
import { renderBattle, renderGatchaResult } from './renderer.js';
import { loadInventoryView, handleRelease } from './inventory.js';
import { loadTradeMenu, renderCreateTradeForm, renderFulfillTradeForm, handleCreateTrade, handleFulfillTrade, toggleTradeSelection } from './trade.js';
import { enterMatchmakingQueue, handleBattleEndConfirmation, setupSocketListeners } from './battle.js';
import { loadDashboard } from './user.js';

const actionContainer = document.getElementById('action-container');
window.actionContainer = actionContainer;

// Expose functions globally
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
window.battleState = {
    inQueue: false,
    battleId: null,
    queueInterval: null,
    currentLevel: 1
};

window.loadContent = async function(endpoint) {
    actionContainer.innerHTML = '<h2>Loading...</h2>';
    
    try {
        if (window.battleState.queueInterval) {
            clearInterval(window.battleState.queueInterval);
            window.battleState.queueInterval = null;
        }

        switch (endpoint) {
            case 'gatcha':
                const gatchaResult = await API.post('/gatcha/roll', {});
                actionContainer.innerHTML = renderGatchaResult(gatchaResult);
                break;
                
            case 'inventory':
                await loadInventoryView();
                break;
                
            case 'battle':
                actionContainer.innerHTML = renderBattle(window.battleState);
                setupSocketListeners();
                break;
                
            case 'trade':
                await loadTradeMenu();
                break;
                
            default:
                actionContainer.innerHTML = '<h2>Invalid endpoint</h2>';
        }
    } catch (error) {
        console.error(`Error loading ${endpoint}:`, error);
        actionContainer.innerHTML = `<h2>Error loading ${endpoint}</h2>`;
    }
};

// Initialize socket connection when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.socket = io();
    setupSocketListeners();
});