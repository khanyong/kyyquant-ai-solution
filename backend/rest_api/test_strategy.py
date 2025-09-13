"""
전략 엔진 테스트 스크립트
실제 전략 조건으로 백테스트가 작동하는지 확인
"""

import requests
import json
from datetime import datetime, timedelta

# 테스트용 전략 파라미터
test_strategy = {
    "strategy_id": "test-strategy-001",
    "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
    "end_date": datetime.now().strftime("%Y-%m-%d"),
    "initial_capital": 10000000,
    "commission": 0.00015,
    "slippage": 0.001,
    "stock_codes": ["005930", "000660", "035720"],  # 삼성전자, SK하이닉스, 카카오
    "parameters": {
        "indicators": [
            {"type": "RSI", "params": {"period": 14}},
            {"type": "SMA", "params": {"period": 20}},
            {"type": "SMA", "params": {"period": 50}}
        ],
        "buyConditions": [
            {
                "indicator": "RSI",
                "operator": "<",
                "value": 30,
                "combineWith": "AND"
            },
            {
                "indicator": "close",
                "operator": ">",
                "value": "sma_20",
                "combineWith": "AND"
            }
        ],
        "sellConditions": [
            {
                "indicator": "RSI",
                "operator": ">",
                "value": 70,
                "combineWith": "OR"
            },
            {
                "indicator": "close",
                "operator": "<",
                "value": "sma_20",
                "combineWith": "OR"
            }
        ]
    }
}

def test_backtest():
    """백테스트 테스트 실행"""

    # 백테스트 서버 URL
    url = "http://localhost:8000/api/backtest/run"

    print("="*60)
    print("전략 백테스트 테스트")
    print("="*60)
    print(f"시작일: {test_strategy['start_date']}")
    print(f"종료일: {test_strategy['end_date']}")
    print(f"종목: {', '.join(test_strategy['stock_codes'])}")
    print("\n매수 조건:")
    print("- RSI < 30")
    print("- 종가 > 20일 이동평균")
    print("\n매도 조건:")
    print("- RSI > 70 또는")
    print("- 종가 < 20일 이동평균")
    print("="*60)

    try:
        # 백테스트 실행
        print("\n백테스트 실행 중...")
        response = requests.post(url, json=test_strategy)

        if response.status_code == 200:
            result = response.json()

            print("\n✅ 백테스트 성공!")
            print("\n=== 결과 ===")

            # 결과 파싱
            if 'results' in result:
                metrics = result['results']
                print(f"총 수익률: {metrics.get('total_return', 0):.2f}%")
                print(f"승률: {metrics.get('win_rate', 0):.2f}%")
                print(f"최대 손실: {metrics.get('max_drawdown', 0):.2f}%")
                print(f"샤프 비율: {metrics.get('sharpe_ratio', 0):.2f}")
                print(f"총 거래 수: {metrics.get('total_trades', 0)}회")
                print(f"수익 거래: {metrics.get('winning_trades', 0)}회")
                print(f"손실 거래: {metrics.get('losing_trades', 0)}회")
                print(f"최종 자본: {metrics.get('final_capital', 0):,.0f}원")

                # 거래 내역 확인
                if 'trade_history' in metrics and metrics['trade_history']:
                    print(f"\n최근 거래 내역 ({len(metrics['trade_history'])}건):")
                    for i, trade in enumerate(metrics['trade_history'][:5], 1):
                        print(f"  {i}. {trade.get('date', 'N/A')} - {trade.get('type', 'N/A')} "
                              f"{trade.get('code', 'N/A')} @ {trade.get('price', 0):,.0f}원")
            else:
                print("결과 데이터가 없습니다.")
                print("응답:", json.dumps(result, indent=2, ensure_ascii=False))

        else:
            print(f"\n❌ 백테스트 실패: {response.status_code}")
            print(f"오류: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n❌ 백테스트 서버에 연결할 수 없습니다.")
        print("서버가 실행 중인지 확인하세요: python backend/rest_api/backtest_server.py")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")

if __name__ == "__main__":
    test_backtest()