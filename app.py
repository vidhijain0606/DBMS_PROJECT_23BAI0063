from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector
from mysql.connector import errorcode

# Create an instance of the Flask class
app = Flask(__name__)
bcrypt = Bcrypt(app)

# --- Database Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',     
    'password': 'Mango@0606', 
    'database': '23bai0063'            
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
@app.route('/login', methods=['POST'])
def login():
    # 1. Get data from the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # 2. Find the user in the database
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True) 

    sql_query = "SELECT * FROM users WHERE username = %s"

    cursor.execute(sql_query, (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # 3. Check if user exists and if the password is correct
    if user and bcrypt.check_password_hash(user['PasswordHash'], password):
        # Login successful
        return jsonify({
            "message": "Login successful",
            "user_id": user['user_id'],
            "username": user['username']
        }), 200
    else:
        # Invalid credentials
        return jsonify({"error": "Invalid username or password"}), 401 # 401 Unauthorized
#stock_details !
@app.route('/analyze', methods=['GET'])
def analyze_stock():
    # 1. Get the ticker and date from the URL query parameters
    ticker = request.args.get('ticker')
    target_date_str = request.args.get('date')

    # 2. Validate that we received the required inputs
    if not ticker or not target_date_str:
        return jsonify({"error": "Ticker and date query parameters are required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        # 3. Query for the historical price on the specific date
        sql_historical = "SELECT close_price FROM historical_prices WHERE stock_id = %s AND price_date = %s"
        cursor.execute(sql_historical, (ticker, target_date_str))
        historical_record = cursor.fetchone()

        # 4. Query for the most recent price
        sql_recent = "SELECT close_price, price_date FROM historical_prices WHERE stock_id = %s ORDER BY price_date DESC LIMIT 1"
        cursor.execute(sql_recent, (ticker,))
        recent_record = cursor.fetchone()

        # 5. Check if we found the data
        if not historical_record or not recent_record:
            return jsonify({"error": "Data not found for the given ticker or date. Ensure date is a valid trading day (Mon-Fri) and format is YYYY-MM-DD."}), 404

        # 6. Perform the calculations
        historical_price = float(historical_record['close_price'])
        recent_price = float(recent_record['close_price'])
        recent_date = recent_record['price_date'].strftime('%Y-%m-%d')

        difference = recent_price - historical_price

        # Avoid division by zero if historical price was 0
        if historical_price == 0:
            percentage_change = float('inf') # Represent infinite change
        else:
            percentage_change = (difference / historical_price) * 100

        # 7. Prepare the successful JSON response
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

    except Exception as e:
        return jsonify({"error": f"An error occurred: {e}"}), 500
    finally:
        cursor.close()
        conn.close()
@app.route('/watchlist/add', methods=['POST'])
def add_to_watchlist():
    # 1. Get data from the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user_id = data.get('user_id')
    stock_id = data.get('stock_id') # This is the ticker symbol

    # 2. Validate input
    if not user_id or not stock_id:
        return jsonify({"error": "user_id and stock_id are required"}), 400

    # 3. Insert into the database
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()

    sql_query = "INSERT INTO user_stocklist (user_id, stock_id) VALUES (%s, %s)"

    try:
        cursor.execute(sql_query, (user_id, stock_id))
        conn.commit()
        return jsonify({"message": "Stock added to watchlist successfully"}), 201

    except mysql.connector.Error as err:
        # Handle specific errors
        if err.errno == errorcode.ER_DUP_ENTRY:
            return jsonify({"error": "This stock is already in the user's watchlist"}), 409 # Conflict
        elif err.errno == errorcode.ER_NO_REFERENCED_ROW_2:
            return jsonify({"error": "User ID or Stock ID not found"}), 404 # Not Found
        else:
            # Handle other potential database errors
            return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()
@app.route('/watchlist/<int:user_id>', methods=['GET'])
def get_watchlist(user_id):
    # The <int:user_id> in the URL tells Flask to pass the number
    # from the URL as an argument to our function.

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)

    try:
        # We use a JOIN to get stock details from the 'stock' table
        # based on the IDs stored in the 'user_stocklist' table.
        sql_query = """
            SELECT s.stock_id, s.company_name, s.exchange
            FROM stock AS s
            JOIN user_stocklist AS usl ON s.stock_id = usl.stock_id
            WHERE usl.user_id = %s
        """
        cursor.execute(sql_query, (user_id,))
        watchlist_items = cursor.fetchall() # Use fetchall() to get all rows

        return jsonify(watchlist_items), 200

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()
@app.route('/watchlist/remove', methods=['DELETE'])
def remove_from_watchlist():
    # 1. Get data from the request
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user_id = data.get('user_id')
    stock_id = data.get('stock_id')

    # 2. Validate input
    if not user_id or not stock_id:
        return jsonify({"error": "user_id and stock_id are required"}), 400

    # 3. Delete from the database
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()

    sql_query = "DELETE FROM user_stocklist WHERE user_id = %s AND stock_id = %s"

    try:
        cursor.execute(sql_query, (user_id, stock_id))
        conn.commit()

        # cursor.rowcount tells us how many rows were deleted.
        # If 0, it means the item wasn't on the list to begin with.
        if cursor.rowcount > 0:
            return jsonify({"message": "Stock successfully removed from watchlist"}), 200
        else:
            return jsonify({"error": "Item not found in this user's watchlist"}), 404

    except mysql.connector.Error as err:
        return jsonify({"error": f"Database error: {err}"}), 500
    finally:
        cursor.close()
        conn.close()
if __name__ == '__main__':
    app.run(debug=True)