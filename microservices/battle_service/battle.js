document.getElementById('startBattle').addEventListener('click', async function() {
    const response = await fetch('/battle/start', { method: 'POST' });
    const result = await response.json();
    document.getElementById('battleResult').textContent = result.message || 'Battle started!';
});
