import sqlite3
from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Function to initialize the SQLite3 database
def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL)''')
    conn.close()

# Initialize the database
with app.app_context():
    init_db()

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Connect to the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Fetch user from the database
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user'] = user[1]  # Store username in session
            return redirect(url_for('dashboard'))  # Redirect to dashboard
        else:
            return "Invalid username or password"  # Error handling
    return render_template('login.html')


# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        
        # Connect to the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            # Insert new user into the database
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                           (username, password, email))
            conn.commit()
            conn.close()

            return redirect(url_for('login'))  # Redirect to login after registration
        except sqlite3.IntegrityError:
            return "User already exists or there was an error."  # Error handling
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/cryptocurrency')
def cryptocurrency():
    return render_template('cryptocurrency.html')

@app.route('/academy')
def academy():
    return render_template('academy.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

if __name__ == '__main__':
    app.run(debug=True)
