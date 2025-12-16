
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Checking docker-compose.yml or .env for port. Usually 8000 or 8001. 
# v8-1 workflow uses http://host.docker.internal:8001, so I'll try localhost:8001
API_URL = "http://localhost:8001/api/indicators/calculate"

def test_calculation():
    payload = {
        "stock_code": "100250",  # Sample from verify_output.txt
        "indicators": [
            { "name": "ma", "params": { "period": 5 } },
            { "name": "ichimoku", "params": {} }
        ],
        "days": 100
    }
    
    print(f"Sending request to {API_URL}...")
    try:
        response = requests.post(API_URL, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_calculation()
