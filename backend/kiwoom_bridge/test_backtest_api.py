"""
백테스트 API 직접 테스트
"""

import requests
import json
from datetime import datetime, timedelta

def test_backtest_api():
    """백테스트 API 직접 호출"""

    # API 엔드포인트
    url = "http://localhost:8001/api/backtest/run"

    # 간단한 종목 1개로만 테스트
    payload = {
        "strategy_id": "88d01e47-c979-4e80-bef8-746a53f3bbca",
        "start_date": "2024-09-14",
        "end_date": "2025-09-12",
        "initial_capital": 10000000,
        "commission": 0.00015,
        "slippage": 0.001,
        "data_interval": "1d",
        "filtering_mode": "pre-filter",
        "use_cached_data": True,
        "stock_codes": ["005930"]  # 삼성전자만 테스트
    }

    print("="*60)
    print("백테스트 API 테스트")
    print("="*60)
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        # API 호출
        response = requests.post(url, json=payload)

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            # 결과 분석
            if 'data' in result:
                data = result['data']
                summary = data.get('summary', {})

                print("\n[Summary]")
                print(f"Total Return: {summary.get('total_return', 0):.2f}%")
                print(f"Total Trades: {summary.get('total_trades', 0)}")
                print(f"Win Rate: {summary.get('win_rate', 0):.2f}%")

                # 개별 종목 결과
                individual = data.get('individual_results', [])
                if individual:
                    stock_result = individual[0]
                    print(f"\n[Stock: {stock_result.get('stock_code')}]")
                    print(f"Trades: {stock_result.get('total_trades', 0)}")
                    print(f"Return: {stock_result.get('total_return', 0):.2f}%")

                    # 거래 내역
                    trades = stock_result.get('trades', [])
                    if trades:
                        print(f"\n[First Trade]")
                        print(json.dumps(trades[0], indent=2))
                    else:
                        print("\n[No Trades Generated]")

                        # 디버그 정보 확인
                        debug_info = stock_result.get('debug_info', {})
                        if debug_info:
                            print("\n[Debug Info]")
                            print(f"Data rows: {debug_info.get('data_rows', 0)}")
                            print(f"Buy signals: {debug_info.get('buy_signals', 0)}")
                            print(f"Sell signals: {debug_info.get('sell_signals', 0)}")

                            # 지표 확인
                            indicators = debug_info.get('indicators', [])
                            if indicators:
                                print(f"Calculated indicators: {indicators}")

            else:
                print("\n[ERROR] No data in response")
                print(json.dumps(result, indent=2))

        else:
            print(f"\n[ERROR] {response.text}")

    except Exception as e:
        print(f"\n[EXCEPTION] {e}")

if __name__ == "__main__":
    test_backtest_api()