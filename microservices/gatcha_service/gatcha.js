document.getElementById('drawGatcha').addEventListener('click', async function() {
    const response = await fetch('/gatcha/draw', { method: 'POST' });
    const result = await response.json();
    document.getElementById('gatchaResult').textContent = result.pokemon ? `You got: ${result.pokemon}` : 'Draw failed.';
});
