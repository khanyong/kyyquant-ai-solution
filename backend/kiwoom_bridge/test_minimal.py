"""
최소 백테스트 테스트
"""

import requests
import json

# 최소 요청
url = "http://localhost:8080/api/backtest/run"  # NAS 컨테이너 포트
data = {
    "strategy_id": "88d01e47-c979-4e80-bef8-746a53f3bbca",
    "stock_codes": ["005930"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 10000000
}

print("Request:", json.dumps(data, indent=2))
print("\nSending to:", url)

try:
    response = requests.post(url, json=data, timeout=10)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Trades: {result.get('summary', {}).get('total_trades', 0)}")
    else:
        print(f"Error: {response.text[:200]}")
except requests.exceptions.Timeout:
    print("\nERROR: Request timeout!")
except Exception as e:
    print(f"\nERROR: {e}")