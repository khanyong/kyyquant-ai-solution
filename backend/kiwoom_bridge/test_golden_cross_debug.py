"""
골든크로스 전략 디버깅 - 실제 백테스트 API 테스트
"""
import requests
import json
from datetime import datetime, timedelta

# 백테스트 요청
request_data = {
    'strategy_id': 'golden-cross',
    'stock_codes': ['005930'],  # 삼성전자
    'start_date': '2024-09-14',
    'end_date': '2025-09-12',
    'initial_capital': 10000000,
    'commission': 0.00015,
    'slippage': 0.001,
    'data_interval': '1d'
}

print("=== 백테스트 요청 ===")
print(json.dumps(request_data, indent=2))

try:
    # 로컬 서버로 요청
    response = requests.post('http://localhost:8001/api/backtest/run', json=request_data)

    print(f"\n=== 응답 상태: {response.status_code} ===")

    if response.status_code == 200:
        result = response.json()

        print(f"\n=== 백테스트 결과 ===")
        print(f"총 수익률: {result.get('total_return', 0):.2f}%")
        print(f"승률: {result.get('win_rate', 0):.2f}%")
        print(f"총 거래: {result.get('total_trades', 0)}회")
        print(f"매수: {result.get('buy_count', 0)}회")
        print(f"매도: {result.get('sell_count', 0)}회")

        trades = result.get('trades', [])

        if trades:
            print(f"\n=== 거래 내역 ({len(trades)}건) ===")
            for i, trade in enumerate(trades[:5]):  # 처음 5개만 출력
                print(f"\n거래 {i+1}:")
                print(f"  날짜: {trade.get('date', 'N/A')}")
                print(f"  유형: {trade.get('type', trade.get('action', 'N/A'))}")
                print(f"  가격: {trade.get('price', 0):,.0f}")

                # 신호 이유 확인
                signal_reason = trade.get('signal_reason', '')
                if signal_reason:
                    print(f"  신호 이유: {signal_reason}")
                else:
                    print(f"  신호 이유: [없음]")

                # 신호 상세 확인
                signal_details = trade.get('signal_details', {})
                if signal_details:
                    print(f"  신호 상세: {json.dumps(signal_details, ensure_ascii=False)}")

                # 수익 정보 (매도인 경우)
                if 'profit' in trade:
                    print(f"  수익: {trade.get('profit', 0):,.0f}")
                    print(f"  수익률: {trade.get('profit_pct', 0):.2f}%")
        else:
            print("\n거래 내역이 없습니다.")
    else:
        print(f"에러: {response.text}")

except Exception as e:
    print(f"요청 실패: {e}")