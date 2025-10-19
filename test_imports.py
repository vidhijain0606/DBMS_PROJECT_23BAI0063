print("Starting import test...")

try:
    import time
    print("SUCCESS: Imported 'time'")

    import requests
    print("SUCCESS: Imported 'requests'")

    import mysql.connector
    print("SUCCESS: Imported 'mysql.connector'")

    print("\nAll libraries imported successfully!")

except Exception as e:
    print(f"\nERROR: An error occurred during import: {e}")