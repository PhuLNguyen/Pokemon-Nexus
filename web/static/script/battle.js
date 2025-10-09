import { API } from './api.js';
import { renderBattleQueue, renderBattleResult } from './renderer.js';
import { loadDashboard } from './user.js'; // Import the dashboard loader

// Store battle state globally on the window object (initialized in main.js)

/**
 * Enters the player into the matchmaking queue.
 */
export async function enterMatchmakingQueue() {
    // Clear existing intervals before starting a new action
    if(window.battleState.queueInterval) {
        clearInterval(window.battleState.queueInterval);
        window.battleState.queueInterval = null;
    }
    
    window.actionContainer.innerHTML = renderBattleQueue('loading');
    
    try {
        const response = await API.enterQueue();

        if (response.status === 'queue') {
            window.battleState.inQueue = true;
            window.actionContainer.innerHTML = renderBattleQueue('queue', response.position);
            
            // Start polling for a match (check every 3 seconds)
            window.battleState.queueInterval = setInterval(checkMatchmakingStatus, 3000);
            
        } else if (response.status === 'matched') {
            // Match found immediately!
            window.battleState.battleId = response.battle_id;
            // No need to clear interval here since it wasn't set yet.
            await displayBattleResult(response.battle_id);
        } else {
             // Error (e.g., no available Pokemon)
             alert(response.message);
             loadDashboard();
        }

    } catch (error) {
        window.actionContainer.innerHTML = `<h2>Queue Error 🚨</h2><p>Could not enter queue: ${error.message}</p>`;
        console.error("Queue entry error:", error);
        loadDashboard();
    }
}

/**
 * Checks the queue status for a match.
 */
async function checkMatchmakingStatus() {
    
    // If a battle ID is set, check the result
    if (window.battleState.battleId) {
        clearInterval(window.battleState.queueInterval);
        return displayBattleResult(window.battleState.battleId);
    }
    
    // Call enterQueue again. The server handles returning the position or a match.
    try {
        const response = await API.enterQueue();
        
        if (response.status === 'matched') {
            window.battleState.battleId = response.battle_id;
            clearInterval(window.battleState.queueInterval);
            return displayBattleResult(response.battle_id);
            
        } else if (response.status === 'queue') {
            // Update position display
            window.actionContainer.innerHTML = renderBattleQueue('queue', response.position);
        }

    } catch (error) {
        // Stop polling on error
        clearInterval(window.battleState.queueInterval);
        alert("Queue polling failed. Returning to dashboard.");
        loadDashboard();
    }
}

/**
 * Retrieves and displays the final battle result.
 */
async function displayBattleResult(battleId) {
    window.actionContainer.innerHTML = '<h2>Retrieving Battle Results...</h2>';
    
    try {
        const result = await API.getBattleResult(battleId);
        
        // Reset battle state
        window.battleState.inQueue = false;
        window.battleState.battleId = null;

        if (result.status === 'complete') {
             window.actionContainer.innerHTML = renderBattleResult(result);
             // Re-load the dashboard info immediately after the battle result to show level/XP update
             loadDashboard();
        } else {
            throw new Error(result.message);
        }
        
    } catch (error) {
        window.actionContainer.innerHTML = `<h2>Result Error 🚨</h2><p>Failed to retrieve battle result: ${error.message}</p>`;
        console.error("Result retrieval error:", error);
        loadDashboard();
    }
}