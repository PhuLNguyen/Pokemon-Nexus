import { API } from './api.js';

export async function loadDashboard() {
    try {
        const response = await API.get('/user/dashboard');
        const dashboardData = await response.json();
        
        window.actionContainer.innerHTML = `
            <div class="dashboard">
                <h2>Trainer Dashboard</h2>
                <div class="stats-container">
                    <div class="stat-card">
                        <h3>Pokemon Owned</h3>
                        <p>${dashboardData.pokemonCount}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Battle Record</h3>
                        <p>Wins: ${dashboardData.wins}</p>
                        <p>Losses: ${dashboardData.losses}</p>
                    </div>
                    <div class="stat-card">
                        <h3>Trades Completed</h3>
                        <p>${dashboardData.tradesCompleted}</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading dashboard:', error);
        window.actionContainer.innerHTML = '<p>Error loading dashboard</p>';
    }
}