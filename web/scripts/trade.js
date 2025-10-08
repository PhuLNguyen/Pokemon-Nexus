import { API } from './api.js';
import { renderTradeMenu, renderCreateTradeForm, renderFulfillTradeForm } from './renderer.js';

/**
 * Loads the main trade menu view.
 */
export async function loadTradeMenu() {
    window.actionContainer.innerHTML = '<h2>Loading Trade Data...</h2>';
    
    try {
        const data = await API.getTradeData();
        window.actionContainer.innerHTML = renderTradeMenu(
            data.inventory, 
            data.pending_trades, 
            data.current_player
        );
    } catch (error) {
        window.actionContainer.innerHTML = `<h2>Trade Server Error 🚨</h2><p>Could not load trade data.</p><p>Error: ${error.message}</p>`;
        console.error("Trade fetch error:", error);
    }
}

/**
 * Renders the form for creating a new trade offer.
 * @param {Array<Object>} inventory - The player's available Pokémon.
 */
export function renderCreateTradeForm(inventory) {
    window.actionContainer.innerHTML = renderCreateTradeForm(inventory);
}

/**
 * Renders the form for fulfilling an existing trade request.
 */
export async function renderFulfillTradeForm(tradeId, requestedCount, creator) {
    window.actionContainer.innerHTML = '<h2>Loading Inventory...</h2>';
    try {
        // We re-fetch inventory here to ensure we have the most up-to-date availability
        const inventory = await API.getInventory();
        window.actionContainer.innerHTML = renderFulfillTradeForm(tradeId, requestedCount, creator, inventory);
    } catch (error) {
        window.actionContainer.innerHTML = `<h2>Error loading inventory for trade fulfillment.</h2><p>${error.message}</p>`;
    }
}


// --- Action Handlers ---

/**
 * Handles the API call to create a new trade.
 */
export async function handleCreateTrade() {
    const checkboxes = document.querySelectorAll('.create-trade-checkbox:checked');
    const offeringIds = Array.from(checkboxes).map(cb => cb.value);
    const requestedCount = parseInt(document.getElementById('request-count').value);

    if (offeringIds.length < 1 || offeringIds.length > 5 || requestedCount < 1 || requestedCount > 5) {
        alert("Selection and request count must be between 1 and 5.");
        return;
    }

    window.actionContainer.innerHTML = `<h2>Sending Trade Request...</h2>`;

    try {
        const data = await API.createTrade(offeringIds, requestedCount);
        alert(data.message);
        loadTradeMenu(); // Reload the main trade menu
    } catch (error) {
        window.actionContainer.innerHTML = `<h2>Trade Creation Failed 😞</h2><p>Error: ${error.message}</p>`;
        console.error("Trade creation error:", error);
    }
}

/**
 * Handles the API call to fulfill an existing trade.
 */
export async function handleFulfillTrade(tradeId, requiredCount) {
    const checkboxes = document.querySelectorAll('.fulfill-trade-checkbox:checked');
    const fulfillingIds = Array.from(checkboxes).map(cb => cb.value);

    if (fulfillingIds.length !== requiredCount) {
        alert(`You must select exactly ${requiredCount} Pokémon.`);
        return;
    }

    window.actionContainer.innerHTML = `<h2>Fulfilling Trade...</h2>`;

    try {
        const data = await API.fulfillTrade(tradeId, fulfillingIds);
        alert(data.message);
        loadTradeMenu(); // Reload the main trade menu
    } catch (error) {
        window.actionContainer.innerHTML = `<h2>Trade Fulfillment Failed 😞</h2><p>Error: ${error.message}</p>`;
        console.error("Trade fulfillment error:", error);
    }
}

/**
 * Logic for selecting/unselecting Pokémon in the trade forms.
 */
export function toggleTradeSelection(element, type, max) {
    const checkbox = element.querySelector('.trade-checkbox');
    const overlay = element.querySelector('.selection-overlay');
    
    const selected = document.querySelectorAll(`.${type}-trade-checkbox:checked`);
    let isCurrentlySelected = checkbox.checked;
    
    if (!isCurrentlySelected && selected.length >= max) {
        alert(`You can only select up to ${max} Pokémon for this action.`);
        return; 
    }

    checkbox.checked = !isCurrentlySelected;
    overlay.style.display = checkbox.checked ? 'flex' : 'none';

    const finalSelected = document.querySelectorAll(`.${type}-trade-checkbox:checked`);
    
    const statusElement = document.getElementById('selection-status');
    if (statusElement) {
        statusElement.textContent = (type === 'create') 
            ? `Selected: ${finalSelected.length}` 
            : `Selected: ${finalSelected.length} / ${max}`;
    }
    
    if (type === 'fulfill') {
        const btn = document.getElementById('fulfill-confirm-btn');
        if (btn) btn.disabled = (finalSelected.length !== max);
    }
}