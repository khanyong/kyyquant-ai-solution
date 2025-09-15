"""
특정 전략 테스트
"""

import requests
import json
import sys

def test_strategy(strategy_id, host="192.168.50.150", port="8080"):
    """특정 전략 테스트"""

    url = f"http://{host}:{port}/api/backtest/run"

    data = {
        "strategy_id": strategy_id,
        "stock_codes": ["005930"],
        "start_date": "2024-09-14",
        "end_date": "2025-09-12",
        "initial_capital": 10000000,
        "commission": 0.00015,
        "slippage": 0.001,
        "data_interval": "1d",
        "use_cached_data": True
    }

    print(f"\nTesting strategy: {strategy_id}")
    print(f"URL: {url}")
    print("-" * 60)

    try:
        resp = requests.post(url, json=data, timeout=30)

        if resp.status_code == 200:
            result = resp.json()
            trades = result.get('summary', {}).get('total_trades', 0)
            print(f"[OK] Status: {resp.status_code}")
            print(f"[Result] Total trades: {trades}")

            # 개별 종목 결과
            individual = result.get('individual_results', [])
            if individual:
                for stock_result in individual:
                    stock_code = stock_result.get('stock_code')
                    stock_trades = stock_result.get('result', {}).get('total_trades', 0)
                    print(f"  - {stock_code}: {stock_trades} trades")

            return trades
        else:
            print(f"[ERROR] Status: {resp.status_code}")
            print(f"Response: {resp.text[:200]}")
            return 0

    except Exception as e:
        print(f"[ERROR] {e}")
        return 0

if __name__ == "__main__":
    # 테스트할 전략들
    strategies = [
        ("931f0e11-afb3-4620-acfe-a24efd325ba0", "스윙 트레이딩"),
        ("88d01e47-c979-4e80-bef8-746a53f3bbca", "테스트 전략")
    ]

    print("\n" + "="*60)
    print("STRATEGY TEST")
    print("="*60)

    for strategy_id, name in strategies:
        print(f"\n[{name}]")
        trades = test_strategy(strategy_id)
        print()

    print("="*60)