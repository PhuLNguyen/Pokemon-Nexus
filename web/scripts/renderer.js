// Function to generate common Pokémon card HTML
function generatePokemonCardHtml(p, type) {
    // Escape single quotes for use in onclick handler parameter string
    const inventoryString = JSON.stringify(p).replace(/"/g, '&quot;');
    
    let selectionElement = '';
    let lockStatus = p.locked ? ' (LOCKED)' : '';

    if (type === 'inventory') {
        selectionElement = `<input type="checkbox" name="pokemon_id" value="${p.id}" class="release-checkbox" style="position: absolute; top: 10px; left: 10px; width: 20px; height: 20px;" ${p.locked ? 'disabled' : ''}>`;
    } else if (type === 'trade-create' || type === 'trade-fulfill') {
        // ToggleTradeSelection is a global function defined in main.js/window object
        const max = type === 'trade-create' ? 5 : p.requiredCount; 
        const className = type === 'trade-create' ? 'create-trade-checkbox' : 'fulfill-trade-checkbox';

        selectionElement = `
            <div class="pokemon-card" style="display:inline-block; margin: 5px; position: relative; cursor: pointer;" data-id="${p.id}" onclick="window.toggleTradeSelection(this, '${type === 'trade-create' ? 'create' : 'fulfill'}', ${max})">
                <input type="checkbox" class="trade-checkbox ${className}" value="${p.id}" style="display: none;">
                <div class="selection-overlay">SELECTED</div>
                <h3>${p.name}</h3>
                <img src="${p.image}" alt="${p.name}">
            </div>
        `;
    }
    
    // Base card structure
    const cardContent = `
        <h3>${p.name}${lockStatus}</h3>
        <img src="${p.image}" alt="${p.name}">
        <ul class="stat-list">
            <li>HP: ${p.hp}</li>
            <li>ATK: ${p.atk}</li>
            <li>DEF: ${p.def}</li>
        </ul>
    `;
    
    // Return different structure based on context
    if (type === 'trade-create' || type === 'trade-fulfill') {
        return selectionElement; // For trade, the selectionElement is the whole card wrapper
    } else {
        return `<div class="pokemon-card" style="display:inline-block; margin: 10px; position: relative;">${selectionElement}${cardContent}</div>`;
    }
}


export function renderGatchaResult(data) {
    const p = data.new_pokemon;
    return `
        <div class="pokemon-card">
            <h2>🎉 Gatcha Pull! You Got: ${p.name}! 🎉</h2>
            <img src="${p.image}" alt="${p.name}">
            <ul class="stat-list">
                <li><strong>HP:</strong> ${p.hp}</li>
                <li><strong>ATK:</strong> ${p.atk}</li>
                <li><strong>DEF:</strong> ${p.def}</li>
            </ul>
            <p style="margin-top: 15px;">**This Pokémon has been added to your Inventory!**</p>
        </div>
    `;
}

export function renderInventory(pokemonList, handleRelease) {
    if (pokemonList.length === 0) {
        return `<h2>Inventory Empty</h2><p>You haven't caught any Pokemon yet! Go use the Gatcha!</p>`;
    }

    const inventoryHtml = pokemonList.map(p => generatePokemonCardHtml(p, 'inventory')).join('');

    return `
        <h2>Your Pokemon Inventory (${pokemonList.length} Caught)</h2>
        <form id="release-form" onsubmit="return false;"> 
            <p>Locked Pokémon (in trade) cannot be released.</p>
            <div style="display:flex; flex-wrap:wrap; justify-content:center;">${inventoryHtml}</div>
            <button type="button" onclick="window.handleRelease()" style="margin-top: 20px; padding: 10px 30px; background-color: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer;">
                Confirm Release Selected
            </button>
        </form>
    `;
}


export function renderBattle(data) {
    return `
        <h2>Battle Queue Status</h2>
        <p>Status: <strong>${data.status}</strong></p>
        <p>${data.message}</p>
        <p>Current Queue Position: <strong>#${data.position}</strong></p>
    `;
}

// --- TRADE RENDERERS ---

export function renderTradeMenu(inventory, pendingTrades, currentPlayer, renderCreateTradeForm, renderFulfillTradeForm) {
    const inventoryString = JSON.stringify(inventory).replace(/"/g, '&quot;');
    
    const tradeListHtml = pendingTrades.map(trade => {
        const offeredNames = trade.offered_details.map(p => p.name).join(', ');
        return `
            <li class="trade-request-item" style="border: 1px solid #5bc0de; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                <p><strong>Offer ID:</strong> ${trade.id} | From: ${trade.creator}</p>
                <p><strong>Offering:</strong> ${offeredNames} (${trade.offered_details.length} Total)</p>
                <p><strong>Requesting:</strong> ${trade.looking_for_count} of YOUR Pokémon</p>
                <button class="menu-button" style="background-color: #28a745; margin-top: 10px;" onclick="window.renderFulfillTradeForm('${trade.id}', ${trade.looking_for_count}, '${trade.creator}')">Fulfill This Trade</button>
            </li>
        `;
    }).join('');

    return `
        <div style="width: 100%;">
            <h1>Pokémon Trade Center</h1>
            
            <div style="display: flex; justify-content: space-around; margin-bottom: 30px;">
                <button class="menu-button" style="background-color: #28a745;" onclick="window.renderCreateTradeForm(${inventoryString})">
                    + Create New Trade
                </button>
            </div>
            
            <h2>Pending Trade Requests (${pendingTrades.length})</h2>
            <ul style="list-style: none; padding: 0; max-width: 600px; margin: 0 auto; text-align: left;">
                ${tradeListHtml || '<p>No pending trade requests at the moment.</p>'}
            </ul>
        </div>
    `;
}

export function renderCreateTradeForm(inventory, handleCreateTrade, loadTradeMenu) {
    const maxSelection = 5;
    const inventoryHtml = inventory.map(p => generatePokemonCardHtml(p, 'trade-create')).join('');

    return `
        <h1>Create New Trade (Select 1-${maxSelection} to Offer)</h1>
        <div id="selection-status">Selected: 0</div>
        
        <div style="margin: 20px 0;">
            <label for="request-count" style="font-weight: bold;">Number of Pokémon you want in return:</label>
            <input type="number" id="request-count" value="1" min="1" max="${maxSelection}" style="width: 50px; padding: 5px; margin-left: 10px; color: #333;">
        </div>
        
        <div style="display:flex; flex-wrap:wrap; justify-content:center;">${inventoryHtml}</div>
        
        <div style="margin-top: 20px;">
            <button onclick="window.handleCreateTrade()" class="menu-button" style="background-color: #28a745;">Confirm Trade Offer</button>
            <button onclick="window.loadContent('trade')" class="menu-button" style="background-color: #6c757d;">Cancel</button>
        </div>
    `;
}

export function renderFulfillTradeForm(tradeId, requestedCount, creator, inventory, handleFulfillTrade, loadTradeMenu) {
    const availableInventory = inventory.filter(p => !p.locked);
    
    // Attach requestedCount to the Pokemon object for use in generatePokemonCardHtml
    const inventoryWithCount = availableInventory.map(p => ({...p, requiredCount: requestedCount}));

    const inventoryHtml = inventoryWithCount.map(p => generatePokemonCardHtml(p, 'trade-fulfill')).join('');

    return `
        <h1>Fulfill Trade Request from ${creator}</h1>
        <h2>You must select exactly ${requestedCount} Pokémon to complete this trade.</h2>
        <div id="selection-status">Selected: 0 / ${requestedCount}</div>

        <p>Select your ${requestedCount} Pokémon to send:</p>
        <div style="display:flex; flex-wrap:wrap; justify-content:center;">${inventoryHtml || '<p>Your available inventory is empty!</p>'}</div>
        
        <div style="margin-top: 20px;">
            <button onclick="window.handleFulfillTrade('${tradeId}', ${requestedCount})" class="menu-button" style="background-color: #28a745;" id="fulfill-confirm-btn" disabled>Confirm Fulfillment</button>
            <button onclick="window.loadContent('trade')" class="menu-button" style="background-color: #6c757d;">Cancel</button>
        </div>
    `;
}