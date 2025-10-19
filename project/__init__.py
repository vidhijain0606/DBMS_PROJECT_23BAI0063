from flask import Flask
from flask_bcrypt import Bcrypt
import pymysql

# Initialize the extension
bcrypt = Bcrypt()
# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mango@0606',
    'database': '23bai0063',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    """A helper function to connect to the database."""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except pymysql.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def create_app():
    """The application factory function."""
    app = Flask(__name__)

    app.secret_key = 'a_super_secret_key_change_later'

    bcrypt.init_app(app)

    # --- Import and Register Blueprints ---
    from .auth.routes import auth_bp  # Import the blueprint
    app.register_blueprint(auth_bp)  # Register it with the app

    print("Flask App Created and Auth Blueprint Registered!") # New confirmation message
    return app