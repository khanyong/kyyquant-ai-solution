"""NAS 서버 백테스트 API 테스트"""
import requests
import json

# API 엔드포인트 URL
url = "https://api.bll-pro.com/api/backtest-run"

# 테스트 요청 데이터
request_data = {
    "strategy_id": "fcfbcb90-d074-449e-a60f-a3c2a86fe74f",  # Golden Cross 전략
    "stock_codes": ["005930"],  # 삼성전자
    "start_date": "2024-09-14",
    "end_date": "2025-09-12",
    "initial_capital": 10000000,
    "commission": 0.00015,
    "slippage": 0.001,
    "parameters": {}
}

print("=" * 60)
print("NAS 서버 백테스트 API 테스트")
print("=" * 60)
print(f"URL: {url}")
print(f"전략 ID: {request_data['strategy_id']}")
print(f"종목 코드: {request_data['stock_codes']}")
print(f"기간: {request_data['start_date']} ~ {request_data['end_date']}")
print("=" * 60)

try:
    # API 호출
    print("\n백테스트 요청 전송 중...")
    response = requests.post(url, json=request_data, timeout=60)

    print(f"응답 상태 코드: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n[SUCCESS] 백테스트 성공!")
        print("-" * 60)

        # 요약 정보 출력
        if 'summary' in result:
            summary = result['summary']
            print("[SUMMARY] 요약 정보:")
            print(f"  - 총 수익률: {summary.get('total_return', 0):.2f}%")
            print(f"  - 승률: {summary.get('average_win_rate', 0):.2f}%")
            print(f"  - 샤프 비율: {summary.get('average_sharpe_ratio', 0):.2f}")
            print(f"  - 최대 낙폭: {summary.get('max_drawdown', 0):.2f}%")
            print(f"  - 총 거래 횟수: {summary.get('total_trades', 0)}")
            print(f"  - 매수 횟수: {summary.get('buy_count', 0)}")
            print(f"  - 매도 횟수: {summary.get('sell_count', 0)}")
            print(f"  - 데이터 소스: {summary.get('data_source', 'unknown')}")

            # 데이터 소스 상세
            if 'data_source_detail' in summary:
                detail = summary['data_source_detail']
                print(f"  - 데이터 소스 상세:")
                print(f"    - Supabase: {detail.get('supabase', 0)}")
                print(f"    - Mock: {detail.get('mock', 0)}")

        # 개별 거래 내역 확인
        if 'individual_results' in result and len(result['individual_results']) > 0:
            ind_result = result['individual_results'][0]
            if 'result' in ind_result and 'trades' in ind_result['result']:
                trades = ind_result['result']['trades']
                print(f"\n[TRADES] 거래 내역 ({len(trades)}건):")

                for i, trade in enumerate(trades[:5], 1):  # 처음 5개만 표시
                    print(f"\n  거래 #{i}:")
                    print(f"    날짜: {trade.get('date', 'N/A')}")
                    print(f"    유형: {trade.get('type', 'N/A')}")
                    print(f"    가격: {trade.get('price', 0):,.0f}")

                    # 매수/매도 이유 확인
                    if 'buy_reason' in trade:
                        print(f"    [REASON] 매수 이유: {trade['buy_reason']}")
                    elif 'sell_reason' in trade:
                        print(f"    [REASON] 매도 이유: {trade['sell_reason']}")
                    elif 'reason' in trade:
                        print(f"    [REASON] 이유: {trade['reason']}")

                if len(trades) > 5:
                    print(f"\n  ... 외 {len(trades)-5}개 거래")

        print("\n" + "=" * 60)
        print("테스트 완료!")

    else:
        print(f"\n[ERROR] 백테스트 실패!")
        print(f"응답 내용: {response.text}")

except requests.exceptions.Timeout:
    print("\n[TIMEOUT] 요청 시간 초과 (60초)")

except requests.exceptions.ConnectionError as e:
    print(f"\n[CONNECTION ERROR] 연결 오류: {e}")

except Exception as e:
    print(f"\n[ERROR] 예상치 못한 오류: {e}")
    import traceback
    traceback.print_exc()