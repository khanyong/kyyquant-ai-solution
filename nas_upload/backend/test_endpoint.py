"""
Test script to verify backtest endpoint
"""

import requests
import json

# Test the root endpoint
print("Testing root endpoint...")
response = requests.get("http://192.168.50.150:8080/")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test the backtest version endpoint
print("\nTesting backtest version endpoint...")
response = requests.get("http://192.168.50.150:8080/api/backtest/version")
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test the backtest run endpoint with minimal data
print("\nTesting backtest run endpoint...")
test_data = {
    "strategy_id": "golden_cross",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "initial_capital": 10000000,
    "stock_codes": ["005930"]  # Samsung Electronics
}

response = requests.post(
    "http://192.168.50.150:8080/api/backtest/run",
    json=test_data
)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500] if response.text else 'No response'}")