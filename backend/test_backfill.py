import requests
import asyncio
import json

# Test script for backfill endpoints
BASE_URL = "http://13.209.204.159:8001"

def test_backfill():
    print("=== Testing Sync History (Backfill) ===")
    
    # Test with a single stock (e.g., Samsung Electronics 005930)
    # Fetch last 5 days
    payload = {
        "stock_codes": ["005930"],
        "days": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/market/sync-history", json=payload, timeout=20)
        print(f"Status Code: {response.status_code}")
        
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except json.JSONDecodeError:
            print(f"Response (Raw Text): {response.text}")
        
        if response.status_code == 200:
            print("✅ Sync History Endpoint Works!")
        else:
            print("❌ Sync History Endpoint Failed!")
            
    except Exception as e:
        print(f"❌ Error Backfill: {e}")

def test_daily_close():
    print("\n=== Testing Daily Close (Batch) ===")
    print("Note: This scans all active strategies. Might take time.")
    
    try:
        # Trigger daily close batch
        response = requests.post(f"{BASE_URL}/api/market/daily-close", timeout=60)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Daily Close Endpoint Works!")
        else:
            print("❌ Daily Close Endpoint Failed!")
            
    except Exception as e:
        print(f"❌ Error Daily Close: {e}")

if __name__ == "__main__":
    test_backfill()
    # Uncomment to test full batch if safe
    # test_daily_close()
