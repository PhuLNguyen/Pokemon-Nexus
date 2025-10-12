document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    const result = await response.json();
    const messageDiv = document.getElementById('loginMessage');
    if (result.success) {
        messageDiv.textContent = 'Login successful!';
        // Redirect or update UI as needed
    } else {
        messageDiv.textContent = 'Login failed: ' + (result.message || 'Invalid credentials');
    }
});
