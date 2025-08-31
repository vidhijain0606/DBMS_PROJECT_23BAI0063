import requests
import mysql.connector
import time

# ==============================================================================
# --- PLEASE EDIT THIS CONFIGURATION SECTION ---
# ==============================================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',     
    'password': 'Mango@0606', # The password you set for MySQL
    'database': '23bai0063'            # Your database name
}
# Paste the API key you received from Alpha Vantage
ALPHA_VANTAGE_API_KEY = 'YOUR_API_KEY_HERE'
# You can change or add to this list of stocks
STOCKS_TO_LOAD = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
# ==============================================================================
# --- END OF CONFIGURATION SECTION ---
# ==============================================================================


def populate_data():
    """Main function to connect to DB and populate stock data."""
    db_connection = None
    try:
        db_connection = mysql.connector.connect(**DB_CONFIG)
        cursor = db_connection.cursor()
        print("Successfully connected to the database.")
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return

    # The free Alpha Vantage API has a limit of 5 calls per minute.
    # We will process one stock every 15 seconds to be safe.
    call_interval_seconds = 15

    for ticker in STOCKS_TO_LOAD:
        print(f"\nProcessing {ticker}...")

        # 1. Get Company Info and INSERT into 'stock' table
        try:
            overview_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
            r = requests.get(overview_url)
            r.raise_for_status()  # This will raise an error for bad status codes
            overview_data = r.json()

            if 'Name' in overview_data and overview_data['Name'] is not None:
                stock_data = (
                    ticker,
                    overview_data.get('Name'),
                    overview_data.get('Industry'),
                    overview_data.get('Sector'),
                    overview_data.get('Exchange'),
                    overview_data.get('Currency')
                )
                sql_insert_stock = """
                    INSERT IGNORE INTO stock (stock_id, company_name, industry, sector, exchange, currency)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert_stock, stock_data)
                print(f"  > Inserted/updated info for {ticker} in 'stock' table.")
            else:
                print(f"  > Could not fetch company overview for {ticker}. API response might be empty or invalid. Skipping.")
                time.sleep(call_interval_seconds)
                continue

        except requests.exceptions.RequestException as e:
            print(f"  > HTTP Error fetching stock info for {ticker}: {e}")
            time.sleep(call_interval_seconds)
            continue
        except Exception as e:
            print(f"  > An unexpected error occurred during stock info processing for {ticker}: {e}")
            time.sleep(call_interval_seconds)
            continue
        
        # Wait before the next API call to respect the rate limit
        print(f"  > Waiting for {call_interval_seconds} seconds before next API call...")
        time.sleep(call_interval_seconds)

        # 2. Get Historical Data and INSERT into 'historical_prices'
        try:
            prices_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}'
            r = requests.get(prices_url)
            r.raise_for_status()
            price_data = r.json()
            
            time_series = price_data.get('Time Series (Daily)')

            if not time_series:
                print(f"  > Could not fetch historical prices for {ticker}. Skipping.")
                continue

            prices_to_insert = []
            for date_str, daily_data in time_series.items():
                price_tuple = (
                    ticker,
                    date_str,
                    daily_data.get('1. open'),
                    daily_data.get('2. high'),
                    daily_data.get('3. low'),
                    daily_data.get('4. close'),
                    daily_data.get('5. volume')
                )
                prices_to_insert.append(price_tuple)
            
            sql_insert_prices = """
                INSERT IGNORE INTO historical_prices (stock_id, price_date, open_price, high_price, low_price, close_price, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(sql_insert_prices, prices_to_insert)
            db_connection.commit()
            print(f"  > Inserted {cursor.rowcount} historical price records for {ticker}.")

        except requests.exceptions.RequestException as e:
            print(f"  > HTTP Error fetching historical prices for {ticker}: {e}")
        except Exception as e:
            print(f"  > An unexpected error occurred during historical price processing for {ticker}: {e}")
    
    # --- Clean up ---
    if db_connection and db_connection.is_connected():
        cursor.close()
        db_connection.close()
        print("\nData loading process finished and database connection closed.")

if __name__ == "__main__":
    populate_data()