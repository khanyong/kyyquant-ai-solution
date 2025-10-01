import requests
import json

# NAS 서버 주소
NAS_URL = "http://192.168.50.150:8001"

# 1. Health Check
print("1. Health Check 테스트...")
try:
    response = requests.get(f"{NAS_URL}/health")
    print(f"   상태: {response.status_code}")
    print(f"   응답: {response.json()}")
except Exception as e:
    print(f"   오류: {e}")

print("\n2. 백테스트 API 테스트...")
# 백테스트 요청 데이터
backtest_data = {
    "symbol": "005930",  # 삼성전자
    "start_date": "2024-01-01",
    "end_date": "2024-03-01",
    "strategy_type": "golden_cross",
    "initial_capital": 10000000
}

try:
    response = requests.post(
        f"{NAS_URL}/api/v1/backtest/run",
        json=backtest_data
    )
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   총 수익률: {result.get('total_return', 0):.2f}%")
        print(f"   거래 횟수: {result.get('total_trades', 0)}")
    else:
        print(f"   오류 응답: {response.text}")
except Exception as e:
    print(f"   오류: {e}")

print("\n3. 전략 목록 조회...")
try:
    response = requests.get(f"{NAS_URL}/api/v1/strategies")
    print(f"   상태: {response.status_code}")
    if response.status_code == 200:
        strategies = response.json()
        print(f"   전략 개수: {len(strategies)}")
        for strategy in strategies[:3]:  # 처음 3개만 표시
            print(f"   - {strategy.get('name', 'Unknown')}")
except Exception as e:
    print(f"   오류: {e}")

print("\nTest Complete!")