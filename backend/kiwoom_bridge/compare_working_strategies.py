"""
작동하는 전략과 안 하는 전략 비교
"""

import requests
import json

def test_and_get_info(strategy_id, name):
    """전략 테스트 및 정보 조회"""

    # 1. 백테스트 실행
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
            return trades
        return -1
    except:
        return -1

# 테스트할 전략들
print("\n" + "="*80)
print("STRATEGY COMPARISON")
print("="*80)

# 작동하는 전략과 안 하는 전략 목록 (프론트엔드에서 확인 필요)
working_strategies = [
    # 여기에 볼린저 밴드와 RSI 반전 전략 ID 추가
]

not_working_strategies = [
    ("931f0e11-afb3-4620-acfe-a24efd325ba0", "스윙 트레이딩")
]

# 알려진 작동 전략
known_working = [
    ("88d01e47-c979-4e80-bef8-746a53f3bbca", "테스트 전략")
]

print("\n[KNOWN WORKING STRATEGIES]")
for sid, name in known_working:
    trades = test_and_get_info(sid, name)
    print(f"  {name:30} : {trades:3} trades")

print("\n[NOT WORKING STRATEGIES]")
for sid, name in not_working_strategies:
    trades = test_and_get_info(sid, name)
    print(f"  {name:30} : {trades:3} trades")

print("\n" + "="*80)

# 차이점 분석
print("\n[POSSIBLE DIFFERENCES]")
print("""
1. Indicator Format:
   - Working: indicators have 'params' object with 'period' inside
   - Not Working: indicators might have 'period' directly without 'params'

2. Operator Types:
   - Working: Simple operators (>, <, >=, <=)
   - Not Working: Complex operators (cross_above, cross_below)

3. Condition Structure:
   - Working: Simple numeric comparisons
   - Not Working: Complex stage-based strategies

4. Value Types:
   - Working: Numeric values or indicator references
   - Not Working: String values that need parsing
""")

print("="*80)