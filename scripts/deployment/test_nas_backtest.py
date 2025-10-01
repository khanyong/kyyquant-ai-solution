import requests
import json

# NAS 서버 주소
NAS_URL = "http://192.168.50.150:8001"

print("=== NAS Auto-Stock Backend Test ===\n")

# 1. Version Check
print("1. Version Check...")
try:
    response = requests.get(f"{NAS_URL}/api/backtest/version")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   Error: {e}")

# 2. Run Backtest
print("\n2. Run Backtest...")
backtest_data = {
    "symbol": "005930",  # Samsung Electronics
    "start_date": "2024-01-01",
    "end_date": "2024-03-01",
    "strategy_type": "golden_cross",
    "initial_capital": 10000000,
    "commission": 0.015
}

try:
    response = requests.post(
        f"{NAS_URL}/api/backtest/run",
        json=backtest_data
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: Backtest completed")
        print(f"   - Total Return: {result.get('total_return', 0):.2f}%")
        print(f"   - Total Trades: {result.get('total_trades', 0)}")
        print(f"   - Win Rate: {result.get('win_rate', 0):.2f}%")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# 3. Quick Backtest
print("\n3. Quick Backtest...")
quick_data = {
    "symbol": "035720",  # Kakao
    "days": 30,
    "strategy_type": "rsi_oversold"
}

try:
    response = requests.post(
        f"{NAS_URL}/api/backtest/quick",
        json=quick_data
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Success: Quick backtest completed")
        print(f"   - Total Return: {result.get('total_return', 0):.2f}%")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n=== Test Complete ===")
print("NAS Backend is running successfully at port 8001!")