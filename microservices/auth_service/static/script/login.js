function showRegister() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'block';
}

function showLogin() {
    document.getElementById('register-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
}

document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            // Successful login (200)
            window.location.href = '/home';
            return;
        }

        // Non-2xx: try to parse and show message
        let result = {};
        try { result = await response.json(); } catch (e) { /* ignore */ }
        alert('Login failed: ' + (result.message || 'Invalid credentials'));
    } catch (error) {
        alert('Error during login: ' + error.message);
    }
});

document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;

    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.status === 201 || response.ok) {
            alert('Registration successful! Please login.');
            showLogin();
            return;
        }

        let result = {};
        try { result = await response.json(); } catch (e) { /* ignore */ }
        alert('Registration failed: ' + (result.message || 'Unknown error'));
    } catch (error) {
        alert('Error during registration: ' + error.message);
    }
});
