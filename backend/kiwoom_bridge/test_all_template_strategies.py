"""
모든 템플릿 전략 테스트
"""

import requests
import json
import time

def test_strategy(strategy_id, name):
    """전략 테스트"""
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
    except Exception as e:
        print(f"    Error: {str(e)[:50]}")
        return -1

# 템플릿 전략 목록 (일반적인 템플릿 이름들)
template_names = [
    "골든크로스",
    "데드크로스",
    "볼린저 밴드",
    "RSI 과매수/과매도",
    "RSI 반전",
    "MACD 시그널",
    "스윙 트레이딩",
    "단기 모멘텀",
    "변동성 돌파"
]

print("\n" + "="*80)
print("TEMPLATE STRATEGY TEST")
print("="*80)
print("Testing common template strategies...")
print("-"*80)

# 먼저 전략 목록 가져오기
strategies_url = "http://192.168.50.150:8080/api/backtest/strategies"
try:
    resp = requests.get(strategies_url, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        if data.get('success'):
            strategies = data.get('strategies', [])

            print(f"Found {len(strategies)} total strategies\n")

            # 템플릿 전략 찾기
            template_strategies = []
            for s in strategies:
                name = s.get('name', '')
                # 템플릿 이름과 매칭
                for template in template_names:
                    if template in name or name.startswith('[템플릿]'):
                        template_strategies.append((s['id'], name))
                        break

            print(f"Found {len(template_strategies)} template strategies to test\n")

            # 각 템플릿 전략 테스트
            working = []
            not_working = []

            for sid, name in template_strategies:
                print(f"Testing: {name[:40]:40} ", end='')
                trades = test_strategy(sid, name)

                if trades > 0:
                    print(f"[OK] {trades:3} trades")
                    working.append((name, trades))
                elif trades == 0:
                    print(f"[X]    0 trades")
                    not_working.append(name)
                else:
                    print(f"[!]  Error")

                time.sleep(0.5)  # 서버 부하 방지

            # 결과 요약
            print("\n" + "="*80)
            print("SUMMARY")
            print("-"*80)

            print(f"\n[WORKING] ({len(working)} strategies):")
            for name, trades in working:
                print(f"  - {name}: {trades} trades")

            print(f"\n[NOT WORKING] ({len(not_working)} strategies):")
            for name in not_working:
                print(f"  - {name}")

            # 패턴 분석
            if working and not_working:
                print("\n" + "-"*80)
                print("PATTERN ANALYSIS:")
                print("""
                Working strategies typically have:
                - Simple operators (>, <, >=, <=)
                - Direct numeric comparisons
                - Standard indicator formats

                Not working strategies might have:
                - Complex operators (cross_above, cross_below)
                - Stage-based conditions
                - Incorrect indicator parameter formats
                """)

except Exception as e:
    print(f"Error getting strategies: {e}")

print("="*80)