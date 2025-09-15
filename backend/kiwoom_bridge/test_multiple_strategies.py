"""
여러 전략 백테스트 실행 테스트
"""

import requests
import json

def test_strategy(strategy_id, name="Unknown"):
    """개별 전략 테스트"""

    url = "http://192.168.50.150:8080/api/backtest/run"

    data = {
        "strategy_id": strategy_id,
        "stock_codes": ["005930"],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 10000000
    }

    try:
        resp = requests.post(url, json=data, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            trades = result.get('summary', {}).get('total_trades', 0)

            # 개별 결과에서 더 자세한 정보 추출
            individual = result.get('individual_results', [])
            if individual and len(individual) > 0:
                stock_result = individual[0].get('result', {})
                buy_count = stock_result.get('buy_count', 0)
                sell_count = stock_result.get('sell_count', 0)

                print(f"[{name[:30]:30}] Trades: {trades:3} | Buy: {buy_count:3} | Sell: {sell_count:3}")

                # 거래가 0인 경우 상세 정보 출력
                if trades == 0:
                    print(f"  └─ ID: {strategy_id}")
            else:
                print(f"[{name[:30]:30}] Trades: {trades:3} | No individual results")

            return trades
        else:
            print(f"[{name[:30]:30}] ERROR: {resp.status_code}")
            return -1
    except Exception as e:
        print(f"[{name[:30]:30}] ERROR: {str(e)[:50]}")
        return -1

# 테스트할 전략 목록 (프론트엔드에서 확인한 ID들)
strategies = [
    ("88d01e47-c979-4e80-bef8-746a53f3bbca", "테스트 전략"),
    ("931f0e11-afb3-4620-acfe-a24efd325ba0", "스윙 트레이딩"),
    # 여기에 더 많은 전략 ID 추가
]

print("\n" + "="*80)
print("MULTIPLE STRATEGY TEST")
print("="*80)
print(f"Testing with 005930 (삼성전자), Period: 2024-01-01 ~ 2024-12-31")
print("-"*80)

success_count = 0
fail_count = 0
zero_count = 0

for strategy_id, name in strategies:
    trades = test_strategy(strategy_id, name)
    if trades > 0:
        success_count += 1
    elif trades == 0:
        zero_count += 1
    else:
        fail_count += 1

print("-"*80)
print(f"Results: Success: {success_count} | Zero trades: {zero_count} | Failed: {fail_count}")
print("="*80)