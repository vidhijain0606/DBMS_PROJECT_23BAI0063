from flask import Blueprint, request, jsonify
from pymysql.constants import ER as errorcode

# We need to import the bcrypt object and the database connection function
# that we defined in our main __init__.py file.
from project import bcrypt, get_db_connection

# Create a Blueprint. The first argument is the blueprint's name, 
# and the second is the import name, which is always __name__.
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    firstname = data.get('firstname')
    lastname = data.get('lastname')

    if not all([username, email, password]):
        return jsonify({"error": "Username, email, and password are required"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            sql_query = """
                INSERT INTO users (username, email, PasswordHash, firstname, lastname)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql_query, (username, email, pw_hash, firstname, lastname))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except Exception as err:
        # We check the specific error code for duplicate entry
        if hasattr(err, 'args') and err.args[0] == errorcode.ER_DUP_ENTRY:
            return jsonify({"error": "Username or email already exists"}), 409
        else:
            return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if conn:
            conn.close()


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            sql_query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql_query, (username,))
            user = cursor.fetchone()
    finally:
        if conn:
            conn.close()

    if user and bcrypt.check_password_hash(user['PasswordHash'], password):
        return jsonify({
            "message": "Login successful",
            "user_id": user['user_id'],
            "username": user['username']
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401