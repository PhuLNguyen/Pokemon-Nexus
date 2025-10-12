import { API } from './api.js';
import { renderBattle } from './renderer.js';

export async function enterMatchmakingQueue() {
    if (window.battleState.inQueue) return;
    
    try {
        window.battleState.inQueue = true;
        window.actionContainer.innerHTML = renderBattle(window.battleState);
        
        const response = await API.post('/battle/queue', {});
        const queueData = await response.json();
        
        window.battleState.queueInterval = setInterval(async () => {
            const statusResponse = await API.get('/battle/status');
            const status = await statusResponse.json();
            
            if (status.battleFound) {
                window.battleState.battleId = status.battleId;
                clearInterval(window.battleState.queueInterval);
                setupBattleUI(status);
            }
        }, 2000);
        
    } catch (error) {
        console.error('Error entering queue:', error);
        window.battleState.inQueue = false;
        window.actionContainer.innerHTML = '<p>Error joining battle queue</p>';
    }
}

export async function handleBattleEndConfirmation() {
    if (window.battleState.queueInterval) {
        clearInterval(window.battleState.queueInterval);
    }
    
    try {
        if (window.battleState.battleId) {
            await API.post('/battle/end', { battleId: window.battleState.battleId });
        }
        
        window.battleState.inQueue = false;
        window.battleState.battleId = null;
        window.actionContainer.innerHTML = renderBattle(window.battleState);
        
    } catch (error) {
        console.error('Error handling battle end:', error);
    }
}

export function setupSocketListeners() {
    if (!window.socket) return;
    
    window.socket.on('battle_update', (data) => {
        if (data.type === 'start') {
            setupBattleUI(data);
        } else if (data.type === 'move') {
            updateBattleUI(data);
        } else if (data.type === 'end') {
            handleBattleEnd(data);
        }
    });
}

function setupBattleUI(battleData) {
    // Implementation for battle UI setup
    window.actionContainer.innerHTML = `
        <div class="battle-interface">
            <h2>Battle Started!</h2>
            <div class="battle-field">
                <!-- Battle UI elements -->
            </div>
        </div>
    `;
}

function updateBattleUI(moveData) {
    // Implementation for updating battle UI after moves
}

function handleBattleEnd(endData) {
    // Implementation for battle end handling
}