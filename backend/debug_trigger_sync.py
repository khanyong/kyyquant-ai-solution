
import requests
import json

# Try localhost ports
ports = [8000, 8001, 8080]

def trigger_sync():
    # Use the test user ID
    payload = {"user_id": "f912da32-897f-4dbb-9242-3a438e9733a8"}
    
    for port in ports:
        url = f"http://localhost:{port}/api/sync/account"
        print(f"Trying {url}...")
        try:
            res = requests.post(url, json=payload, timeout=30)
            if res.status_code == 200:
                print(f"Success! {res.json()}")
                return
            else:
                print(f"Failed with {res.status_code}: {res.text}")
        except Exception as e:
            print(f"Connection failed: {e}")

if __name__ == "__main__":
    trigger_sync()
