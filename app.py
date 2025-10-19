from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import pymysql # <-- CHANGE 1: New library import
from pymysql.constants import ER as errorcode # <-- For error codes

# Create an instance of the Flask class
app = Flask(__name__)
bcrypt = Bcrypt(app)

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mango@0606',
    'database': '23bai0063',
    'cursorclass': pymysql.cursors.DictCursor # To get results as dictionaries
}

# A function to get a new database connection
def get_db_connection():
    try:
        # CHANGE 2: Using pymysql.connect
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Test Route
@app.route('/')
def index():
    return '<h1>Stock Analysis API is running!</h1>'

# --- All your routes (register, login, analyze, watchlist) remain the same ---
# I am including them here for completeness.

@app.route('/register', methods=['POST'])
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
        return jsonify({"message": "User registered successfully"}), 21
    except pymysql.MySQLError as err:
        if err.args[0] == errorcode.ER_DUP_ENTRY:
            return jsonify({"error": "Username or email already exists"}), 409
        else:
            return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
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

@app.route('/analyze', methods=['GET'])
def analyze_stock():
    ticker = request.args.get('ticker')
    target_date_str = request.args.get('date')

    if not ticker or not target_date_str:
        return jsonify({"error": "Ticker and date query parameters are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            sql_historical = "SELECT close_price FROM historical_prices WHERE stock_id = %s AND price_date = %s"
            cursor.execute(sql_historical, (ticker, target_date_str))
            historical_record = cursor.fetchone()
            
            sql_recent = "SELECT close_price, price_date FROM historical_prices WHERE stock_id = %s ORDER BY price_date DESC LIMIT 1"
            cursor.execute(sql_recent, (ticker,))
            recent_record = cursor.fetchone()
    except pymysql.Error as err:
        return jsonify({"error": f"Database query failed: {err}"}), 500
    finally:
        if conn:
            conn.close()

    if not historical_record or not recent_record:
        return jsonify({"error": "Data not found for the given ticker or date. Ensure date is a valid trading day (Mon-Fri) and format is YYYY-MM-DD."}), 404

    historical_price = float(historical_record['close_price'])
    recent_price = float(recent_record['close_price'])
    recent_date = recent_record['price_date'].strftime('%Y-%m-%d')
    difference = recent_price - historical_price
    
    if historical_price == 0:
        percentage_change = float('inf')
    else:
        percentage_change = (difference / historical_price) * 100
    
    response = {
        "ticker": ticker,
        "historical_date": target_date_str,
        "historical_price": round(historical_price, 2),
        "recent_date": recent_date,
        "recent_price": round(recent_price, 2),
        "price_difference": round(difference, 2),
        "percentage_change": round(percentage_change, 2)
    }
    return jsonify(response), 200

@app.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    user_id = data.get('user_id')
    stock_id = data.get('stock_id')

    if not user_id or not stock_id:
        return jsonify({"error": "user_id and stock_id are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            sql_query = "INSERT INTO user_stocklist (user_id, stock_id) VALUES (%s, %s)"
            cursor.execute(sql_query, (user_id, stock_id))
        conn.commit()
        return jsonify({"message": "Stock added to watchlist successfully"}), 201
    except pymysql.MySQLError as err:
        if err.args[0] == errorcode.ER_DUP_ENTRY:
            return jsonify({"error": "This stock is already in the user's watchlist"}), 409
        elif err.args[0] == errorcode.ER_NO_REFERENCED_ROW_2:
            return jsonify({"error": "User ID or Stock ID not found"}), 404
        else:
            return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/watchlist/<int:user_id>', methods=['GET'])
def get_watchlist(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            sql_query = """
                SELECT s.stock_id, s.company_name, s.exchange
                FROM stock AS s
                JOIN user_stocklist AS usl ON s.stock_id = usl.stock_id
                WHERE usl.user_id = %s
            """
            cursor.execute(sql_query, (user_id,))
            watchlist_items = cursor.fetchall()
        return jsonify(watchlist_items), 200
    except pymysql.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/watchlist/remove', methods=['DELETE'])
def remove_from_watchlist():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    user_id = data.get('user_id')
    stock_id = data.get('stock_id')

    if not user_id or not stock_id:
        return jsonify({"error": "user_id and stock_id are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        with conn.cursor() as cursor:
            sql_query = "DELETE FROM user_stocklist WHERE user_id = %s AND stock_id = %s"
            cursor.execute(sql_query, (user_id, stock_id))
        conn.commit()
        
        if cursor.rowcount > 0:
            return jsonify({"message": "Stock successfully removed from watchlist"}), 200
        else:
            return jsonify({"error": "Item not found in this user's watchlist"}), 404
    except pymysql.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)