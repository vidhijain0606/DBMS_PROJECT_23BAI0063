import requests
import pymysql # <-- CHANGE 1: New library import
import time

# ==============================================================================
# --- CONFIGURATION SECTION ---
# ==============================================================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mango@0606',
    'database': '23bai0063'
}
ALPHA_VANTAGE_API_KEY = 'TZIGQLR608KRFG4M'
STOCKS_TO_LOAD = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
# ==============================================================================
# --- END OF CONFIGURATION SECTION ---
# ==============================================================================

def populate_data():
    """Main function to connect to DB and populate stock data."""
    db_connection = None
    try:
        # CHANGE 2: Using pymysql.connect instead of mysql.connector.connect
        db_connection = pymysql.connect(**DB_CONFIG) 
        cursor = db_connection.cursor()
        print("Successfully connected to the database.")
    except pymysql.Error as err:
        print(f"Error connecting to database: {err}")
        return

    call_interval_seconds = 15

    for ticker in STOCKS_TO_LOAD:
        print(f"\nProcessing {ticker}...")
        try:
            overview_url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}'
            r = requests.get(overview_url)
            r.raise_for_status()
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
                db_connection.commit()
                print(f"  > Inserted/updated info for {ticker} in 'stock' table.")
            else:
                print(f"  > Could not fetch company overview for {ticker}. API response might be empty. Skipping.")
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
        
        print(f"  > Waiting for {call_interval_seconds} seconds before next API call...")
        time.sleep(call_interval_seconds)

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
    
    if db_connection and db_connection.open:
        cursor.close()
        db_connection.close()
        print("\nData loading process finished and database connection closed.")

if __name__ == "__main__":
    populate_data()