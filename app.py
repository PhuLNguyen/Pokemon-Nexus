from flask import Flask, request, render_template, redirect, url_for, flash

# Initialize the Flask application
app = Flask(__name__)
# A secret key is required for flashing messages (optional but recommended)
app.secret_key = 'your_secret_key_here' 

# --- Routes for the Login and Registration Forms ---

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Handles the main page, which displays the forms.
    GET: Just shows the index.html page.
    POST: This route is NOT used for submission; submissions go to /login or /register.
    """
    # Flask looks for templates in a folder named 'templates' by default.
    # Since the user requested index.html in the prompt, we'll assume it's there
    # or you can rename the file to 'index.html' and put it in a 'templates' folder.
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    """Handles the form submission from the Login form."""
    
    # Check if the request method is POST (which it should be from the form)
    if request.method == 'POST':
        # Get data from the form fields using their 'name' attributes
        email = request.form.get('email')
        password = request.form.get('password')

        # --- Basic Validation and Processing (Placeholder) ---
        
        if not email or not password:
            flash('Both email and password are required for login.', 'error')
            # In a real app, you would redirect to the form page and show the error
            return redirect(url_for('index'))

        # ⚠️ WARNING: In a real app, you would:
        # 1. Look up the user in a database using the email.
        # 2. **Securely** verify the password hash.
        
        # --- Placeholder for successful login ---
        print(f"LOGIN ATTEMPT: Email={email}, Password={password}")
        
        # Flash a message to show the user they logged in
        flash(f'Successfully logged in as {email}!', 'success')
        
        # Redirect to a protected page (e.g., a dashboard)
        return redirect(url_for('dashboard'))

    # If someone tries to access /login with GET, redirect them to the index
    return redirect(url_for('index'))


@app.route('/register', methods=['POST'])
def register():
    """Handles the form submission from the Registration form."""
    
    if request.method == 'POST':
        # Get data from the form fields using their 'name' attributes
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # --- Basic Validation and Processing (Placeholder) ---
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('index'))

        # ⚠️ WARNING: In a real app, you would:
        # 1. Check if the email already exists in the database.
        # 2. **Hash** the password before storing it.
        # 3. Save the new user's details (name, email, HASHED password) to the database.
        
        # --- Placeholder for successful registration ---
        print(f"REGISTRATION: Name={name}, Email={email}, Password={password}")
        
        # Flash a message to show the user they registered
        flash(f'Account created for {email}! Please log in.', 'success')
        
        # Redirect to the main page, where they can now log in
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))


# --- Dashboard Route (Example of a protected page) ---

@app.route('/dashboard')
def dashboard():
    """An example page a user sees after a successful login."""
    # In a real application, you would check if the user is authenticated here.
    return "<h1>Welcome to the Dashboard!</h1><p>You are successfully logged in.</p>"


# --- Run the application ---

if __name__ == '__main__':
    # Set debug=True for automatic reloads during development
    app.run(debug=True)