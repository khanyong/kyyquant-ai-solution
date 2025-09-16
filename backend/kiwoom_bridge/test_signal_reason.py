"""
신호 이유 디버깅 - API 응답 확인
"""
import requests
import json

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
    response = requests.post('http://localhost:8001/api/backtest/run', json=request_data)

    if response.status_code == 200:
        result = response.json()

        print(f"\n=== 백테스트 결과 ===")
        print(f"총 수익률: {result.get('total_return', 0):.2f}%")
        print(f"총 거래: {result.get('total_trades', 0)}회")

        trades = result.get('trades', [])

        print(f"\n=== 거래 내역 상세 ({len(trades)}건) ===")
        for i, trade in enumerate(trades):
            print(f"\n거래 {i+1}:")
            print(f"  날짜: {trade.get('date')}")
            print(f"  유형: {trade.get('type', trade.get('action'))}")
            print(f"  가격: {trade.get('price'):,.0f}")

            # 신호 이유 확인 - 모든 가능한 필드 체크
            reason_fields = ['signal_reason', 'reason', 'buy_reason', 'sell_reason', 'signal']
            for field in reason_fields:
                if field in trade:
                    print(f"  {field}: {trade[field]}")

            # signal_details 확인
            if 'signal_details' in trade:
                print(f"  signal_details: {json.dumps(trade['signal_details'], ensure_ascii=False, indent=4)}")

            # 모든 필드 출력 (디버깅용)
            print(f"  전체 필드: {list(trade.keys())}")

        # 전체 응답 구조 확인
        print("\n=== 전체 응답 키 ===")
        print(list(result.keys()))

        # trades 배열의 첫 번째 항목 전체 출력
        if trades:
            print("\n=== 첫 번째 거래 전체 데이터 ===")
            print(json.dumps(trades[0], ensure_ascii=False, indent=2))

        # individual_results 확인
        individual_results = result.get('individual_results', [])
        if individual_results and len(individual_results) > 0:
            print("\n=== Individual Results ===")
            first_result = individual_results[0]
            print(f"종목: {first_result.get('stock_code')}")
            print(f"수익률: {first_result.get('total_return', 0):.2f}%")

            ind_trades = first_result.get('trades', [])
            print(f"거래 수: {len(ind_trades)}개")

            if ind_trades:
                print("\n=== Individual 거래 내역 ===")
                for i, trade in enumerate(ind_trades[:5]):  # 처음 5개만
                    print(f"\n거래 {i+1}:")
                    print(f"  날짜: {trade.get('date')}")
                    print(f"  유형: {trade.get('type', trade.get('action'))}")
                    print(f"  가격: {trade.get('price', 0):,.0f}")

                    # 모든 가능한 이유 필드 확인
                    for field in ['signal_reason', 'reason', 'buy_reason', 'sell_reason']:
                        if field in trade:
                            print(f"  {field}: {trade[field]}")

                    if 'signal_details' in trade:
                        print(f"  signal_details: {json.dumps(trade['signal_details'], ensure_ascii=False)}")

                    print(f"  전체 키: {list(trade.keys())}")
    else:
        print(f"에러: {response.text}")

except Exception as e:
    print(f"요청 실패: {e}")