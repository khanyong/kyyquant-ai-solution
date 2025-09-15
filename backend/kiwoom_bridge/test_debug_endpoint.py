"""
전략 디버그 엔드포인트 테스트
"""

import requests
import json

def debug_strategy(strategy_id, name=""):
    """전략 디버그"""

    url = "http://192.168.50.150:8080/api/backtest/debug/strategy"

    data = {
        "strategy_id": strategy_id
    }

    try:
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            result = resp.json()

            print(f"\n[{name}]")
            print(f"ID: {strategy_id}")
            print("-"*60)

            if result.get('success'):
                print(f"Strategy Name: {result.get('strategy_name')}")
                print(f"Indicators: {result.get('indicators_count')}")
                print(f"Buy Conditions: {result.get('buy_conditions_count')}")
                print(f"Sell Conditions: {result.get('sell_conditions_count')}")

                issues = result.get('issues', [])
                if issues:
                    print(f"\n⚠️ Issues Found ({len(issues)}):")
                    for issue in issues:
                        print(f"  - {issue}")
                else:
                    print("\n✅ No issues found")

                print(f"\nTest Result: {result.get('test_result')}")

                # Config 일부 출력
                config = result.get('config', {})
                if config:
                    print("\nSample Config:")

                    # 첫 번째 지표
                    indicators = config.get('indicators', [])
                    if indicators:
                        print(f"  First Indicator: {json.dumps(indicators[0], ensure_ascii=False)}")

                    # 첫 번째 매수 조건
                    buy_conditions = config.get('buyConditions', [])
                    if buy_conditions:
                        print(f"  First Buy Condition: {json.dumps(buy_conditions[0], ensure_ascii=False)}")

            else:
                print(f"ERROR: {result.get('message', 'Unknown error')}")

        else:
            print(f"HTTP Error: {resp.status_code}")

    except Exception as e:
        print(f"Request Error: {e}")

# 테스트
strategies = [
    ("88d01e47-c979-4e80-bef8-746a53f3bbca", "테스트 전략 (작동함)"),
    ("931f0e11-afb3-4620-acfe-a24efd325ba0", "스윙 트레이딩 (0 거래)")
]

print("\n" + "="*80)
print("STRATEGY DEBUG")
print("="*80)

for strategy_id, name in strategies:
    debug_strategy(strategy_id, name)

print("\n" + "="*80)