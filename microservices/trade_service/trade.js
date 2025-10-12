document.getElementById('tradeForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const tradeWith = document.getElementById('tradeWith').value;
    const pokemonName = document.getElementById('pokemonName').value;
    const response = await fetch('/trade/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tradeWith, pokemonName })
    });
    const result = await response.json();
    const messageDiv = document.getElementById('tradeMessage');
    if (result.success) {
        messageDiv.textContent = 'Trade successful!';
    } else {
        messageDiv.textContent = 'Trade failed: ' + (result.message || 'Error');
    }
});
