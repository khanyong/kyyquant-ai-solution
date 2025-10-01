"""
재설치 후 테스트 스크립트
"""
import requests
import json

BASE_URL = "http://192.168.50.150:8080"

print("="*50)
print("Auto Stock Backend Test Script")
print("="*50)

# 1. Health Check
print("\n1. Health Check...")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✓ Server is healthy")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 2. Root endpoint
print("\n2. Root Endpoint...")
try:
    r = requests.get(f"{BASE_URL}/", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Version: {data.get('version')}")
        print(f"   ✓ Status: {data.get('status')}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 3. Backtest Version
print("\n3. Backtest API Version...")
try:
    r = requests.get(f"{BASE_URL}/api/backtest/version", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"   ✓ Version: {data.get('version')}")
        print(f"   ✓ Features: {', '.join(data.get('features', []))}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 4. Strategy List
print("\n4. Strategy List...")
try:
    r = requests.get(f"{BASE_URL}/api/strategy/list", timeout=5)
    if r.status_code == 200:
        strategies = r.json()
        print(f"   ✓ Found {len(strategies)} strategies")
        for s in strategies[:3]:  # Show first 3
            print(f"     - {s.get('id')}: {s.get('name')}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# 5. Test Backtest Run
print("\n5. Test Backtest Run...")
test_data = {
    "strategy_id": "golden_cross",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "initial_capital": 10000000,
    "stock_codes": ["005930"]
}

try:
    r = requests.post(
        f"{BASE_URL}/api/backtest/run",
        json=test_data,
        timeout=30
    )
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        print(f"   ✓ Backtest completed")
        print(f"     - Initial: {result.get('initial_capital'):,}")
        print(f"     - Final: {result.get('final_capital'):,}")
        print(f"     - Return: {result.get('total_return_rate'):.2f}%")
    else:
        print(f"   ✗ Error: {r.text[:200]}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "="*50)
print("Test Complete!")
print("="*50)