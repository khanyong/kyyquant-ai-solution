"""
백테스트 API 테스트 - 상세 로깅
"""

import requests
import json
import time
from datetime import datetime

def test_backtest_with_logging():
    """백테스트 API 호출 후 로그 확인"""

    url = "http://localhost:8001/api/backtest/run"

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
        "stock_codes": ["005930"]
    }

    print("="*60)
    print(f"백테스트 실행 시간: {datetime.now()}")
    print("="*60)
    print("API 호출 중...")

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"응답 코드: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            # 요약 정보
            if 'summary' in result:
                summary = result['summary']
                print(f"\n[요약]")
                print(f"총 거래: {summary.get('total_trades', 0)}회")
                print(f"매수: {summary.get('buy_count', 0)}회")
                print(f"매도: {summary.get('sell_count', 0)}회")

            # 개별 결과
            if 'individual_results' in result:
                for stock in result['individual_results']:
                    stock_result = stock.get('result', {})
                    print(f"\n[{stock['stock_code']}]")
                    print(f"거래: {stock_result.get('total_trades', 0)}회")
                    print(f"수익률: {stock_result.get('total_return', 0):.2f}%")

            # 전체 응답 저장
            with open('backtest_response.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n전체 응답이 backtest_response.json에 저장됨")

        else:
            print(f"오류: {response.text}")

    except Exception as e:
        print(f"예외 발생: {e}")

    print("\n*** Docker 로그를 확인하세요 ***")
    print("Docker Desktop → kiwoom-bridge → Logs")
    print("특히 다음 내용을 찾아보세요:")
    print("- [DEBUG] AdvancedBacktestEngine.run")
    print("- [Core] 신호: 매수 X, 매도 X")
    print("- ERROR 또는 Exception")

if __name__ == "__main__":
    test_backtest_with_logging()