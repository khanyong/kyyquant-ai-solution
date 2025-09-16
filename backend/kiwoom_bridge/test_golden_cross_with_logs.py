"""
골든크로스 전략 디버깅 - 서버 로그 확인용
"""
import requests
import json
from datetime import datetime, timedelta
import time

# 백테스트 요청
request_data = {
    'strategy_id': 'golden-cross',
    'stock_codes': ['005930'],  # 삼성전자
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'initial_capital': 10000000,
    'commission': 0.00015,
    'slippage': 0.001,
    'data_interval': '1d'
}

print("=== 백테스트 요청 ===")
print(json.dumps(request_data, indent=2))
print("\n서버 로그를 확인하세요...")
print("=" * 50)

try:
    # 로컬 서버로 요청
    print("\n[요청 전송 중...]")
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
            for i, trade in enumerate(trades[:10]):  # 처음 10개만 출력
                print(f"\n거래 {i+1}:")
                print(f"  날짜: {trade.get('date', 'N/A')}")
                print(f"  유형: {trade.get('type', 'N/A')}")
                print(f"  가격: {trade.get('price', 0):,.0f}")

                # 신호 이유 확인
                signal_reason = trade.get('signal_reason', '')
                if signal_reason:
                    print(f"  신호 이유: {signal_reason}")

                # 신호 상세 확인
                signal_details = trade.get('signal_details', {})
                if signal_details:
                    print(f"  신호 상세: {json.dumps(signal_details, ensure_ascii=False)}")
        else:
            print("\n거래 내역이 없습니다.")
            print("\n[디버깅 힌트]")
            print("1. Core 모듈이 로드되었는지 확인")
            print("2. 지표명이 소문자인지 확인 (ma_20, ma_60)")
            print("3. Supabase에서 데이터가 로드되었는지 확인")
            print("4. cross_above 연산자가 제대로 작동하는지 확인")
    else:
        print(f"에러: {response.text}")

except Exception as e:
    print(f"요청 실패: {e}")

print("\n서버 로그를 확인하여 다음을 체크하세요:")
print("- [Core] 신호: 매수 X, 매도 X")
print("- [Core] 매수 신호 날짜")
print("- Supabase에서 데이터 로드 여부")