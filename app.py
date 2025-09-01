from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector
from mysql.connector import errorcode

# Create an instance of the Flask class
app = Flask(__name__)
bcrypt = Bcrypt(app)

# --- Database Configuration ---
# (This should be the same as your load_data.py script)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',     # E.g., 'root'
    'password': 'Mango@0606', # The password you set for MySQL
    'database': '23bai0063'            # Your database name
}

# A function to get a new database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Test Route to make sure the server is running
@app.route('/')
def index():
    return '<h1>Stock Analysis API is running!</h1>'


# --- We will add the /register endpoint here in the next step ---

@app.route('/register', methods=['POST'])
def register():
    # 1. Get data from the incoming request's JSON body
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    firstname = data.get('firstname')
    lastname = data.get('lastname')

    # 2. Basic validation to ensure required fields are present
    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400

    # 3. Securely hash the password
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # 4. Insert the new user into the database
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    
    sql_query = """
        INSERT INTO users (username, email, PasswordHash, firstname, lastname)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(sql_query, (username, email, pw_hash, firstname, lastname))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except mysql.connector.Error as err:
        # Check for duplicate entry error (error code 1062)
        if err.errno == errorcode.ER_DUP_ENTRY:
            return jsonify({"error": "Username or email already exists"}), 409 # 409 Conflict
        else:
            return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()

# Run the app
if __name__ == '__main__':
    app.run(debug=True)