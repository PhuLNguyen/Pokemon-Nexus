import { API } from './api.js';

export async function loadTradeMenu() {
    try {
        const response = await API.get('/trade/list');
        const trades = await response.json();
        
        let content = `
            <div class="trade-view">
                <h2>Trading Center</h2>
                <button onclick="renderCreateTradeForm()">Create New Trade</button>
                <div class="active-trades">
                    <h3>Active Trades</h3>
        `;
        
        trades.forEach(trade => {
            content += `
                <div class="trade-card">
                    <h4>Trade #${trade.id}</h4>
                    <p>Offering: ${trade.offeringPokemon.name} (Level ${trade.offeringPokemon.level})</p>
                    <p>Requesting: ${trade.requestingPokemon.name} (Level ${trade.requestingPokemon.level})</p>
                    <button onclick="renderFulfillTradeForm(${trade.id})">Fulfill Trade</button>
                </div>
            `;
        });
        
        content += `
                </div>
            </div>
        `;
        
        window.actionContainer.innerHTML = content;
    } catch (error) {
        console.error('Error loading trades:', error);
        window.actionContainer.innerHTML = '<p>Error loading trades</p>';
    }
}

export function renderCreateTradeForm() {
    window.actionContainer.innerHTML = `
        <div class="trade-form">
            <h2>Create New Trade</h2>
            <form onsubmit="handleCreateTrade(event)">
                <div class="form-group">
                    <label>Offering Pokemon:</label>
                    <select name="offeringPokemonId" required>
                        <!-- Populated dynamically -->
                    </select>
                </div>
                <div class="form-group">
                    <label>Requesting Pokemon:</label>
                    <select name="requestingPokemonType" required>
                        <!-- Populated dynamically -->
                    </select>
                    <input type="number" name="requestingPokemonLevel" min="1" max="100" required>
                </div>
                <button type="submit">Create Trade</button>
            </form>
        </div>
    `;
}

export function renderFulfillTradeForm(tradeId) {
    window.actionContainer.innerHTML = `
        <div class="trade-form">
            <h2>Fulfill Trade #${tradeId}</h2>
            <form onsubmit="handleFulfillTrade(event, ${tradeId})">
                <div class="form-group">
                    <label>Select Pokemon to Trade:</label>
                    <select name="fulfillingPokemonId" required>
                        <!-- Populated dynamically -->
                    </select>
                </div>
                <button type="submit">Complete Trade</button>
            </form>
        </div>
    `;
}

export async function handleCreateTrade(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const tradeData = {
        offeringPokemonId: formData.get('offeringPokemonId'),
        requestingPokemonType: formData.get('requestingPokemonType'),
        requestingPokemonLevel: formData.get('requestingPokemonLevel')
    };
    
    try {
        await API.post('/trade/create', tradeData);
        loadTradeMenu();
    } catch (error) {
        console.error('Error creating trade:', error);
    }
}

export async function handleFulfillTrade(event, tradeId) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const fulfillData = {
        tradeId: tradeId,
        fulfillingPokemonId: formData.get('fulfillingPokemonId')
    };
    
    try {
        await API.post('/trade/fulfill', fulfillData);
        loadTradeMenu();
    } catch (error) {
        console.error('Error fulfilling trade:', error);
    }
}

export function toggleTradeSelection(pokemonId) {
    // Implementation for trade pokemon selection
}