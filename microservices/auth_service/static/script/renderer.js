export function renderBattle(battleState) {
    return `
        <div class="battle-view">
            <h2>Battle Interface</h2>
            <div class="battle-status">
                <p>Current Level: ${battleState.currentLevel}</p>
                ${battleState.inQueue ? 
                    `<p>Looking for opponent...</p>
                     <button onclick="handleBattleEndConfirmation()">Cancel</button>` 
                    : 
                    `<button onclick="enterMatchmakingQueue()">Find Opponent</button>`}
            </div>
        </div>
    `;
}

export function renderGatchaResult(pokemon) {
    return `
        <div class="gatcha-result">
            <h3>You got a new Pokemon!</h3>
            <div class="pokemon-card">
                <h4>${pokemon.name}</h4>
                <p>Level: ${pokemon.level}</p>
                <p>Type: ${pokemon.type}</p>
                <button onclick="loadInventoryView()">View Inventory</button>
            </div>
        </div>
    `;
}