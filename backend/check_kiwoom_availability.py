import sys
import os
from api.kiwoom_client import get_kiwoom_client
from dotenv import load_dotenv

load_dotenv()

def check_availability():
    print("Checking Kiwoom API Availability...")
    client = get_kiwoom_client()
    
    # Try fetching current price for Samsung Electronics (005930)
    # This is a lightweight call.
    result = client.get_current_price("005930")
    
    if result:
        print("\n[SUCCESS] Kiwoom API is responding.")
        print(f"Data received: {result}")
        return True
    else:
        print("\n[FAILURE] Kiwoom API did not respond or returned error.")
        return False

if __name__ == "__main__":
    check_availability()
