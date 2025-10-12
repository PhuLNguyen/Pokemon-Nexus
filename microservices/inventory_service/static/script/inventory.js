import { API } from './api.js';

let selectedPokemon = [];

export async function loadInventoryView() {
    try {
        const response = await API.get('/inventory');
        const inventory = await response.json();
        
        let content = `
            <div class="inventory-view">
                <h2>Your Pokemon</h2>
                <div class="pokemon-grid">
        `;
        
        inventory.forEach(pokemon => {
            content += `
                <div class="pokemon-card ${selectedPokemon.includes(pokemon.id) ? 'selected' : ''}" 
                     onclick="togglePokemonSelection(${pokemon.id})">
                    <h3>${pokemon.name}</h3>
                    <p>Level: ${pokemon.level}</p>
                    <p>Type: ${pokemon.type}</p>
                    <button onclick="handleRelease(${pokemon.id})">Release</button>
                </div>
            `;
        });
        
        content += `
                </div>
            </div>
        `;
        
        window.actionContainer.innerHTML = content;
    } catch (error) {
        console.error('Error loading inventory:', error);
        window.actionContainer.innerHTML = '<p>Error loading inventory</p>';
    }
}

export async function handleRelease(pokemonId) {
    try {
        await API.post('/inventory/release', { pokemonId });
        loadInventoryView(); // Refresh the view
    } catch (error) {
        console.error('Error releasing pokemon:', error);
    }
}

export function togglePokemonSelection(pokemonId) {
    const index = selectedPokemon.indexOf(pokemonId);
    if (index === -1) {
        selectedPokemon.push(pokemonId);
    } else {
        selectedPokemon.splice(index, 1);
    }
    loadInventoryView(); // Refresh view to show selection
}