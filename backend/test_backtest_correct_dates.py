"""
백테스트 테스트 - 올바른 날짜 범위
2024-09-14 ~ 2025-09-12 (약 1년)
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://192.168.50.150:8080"

print("="*60)
print("백테스트 테스트 - 1년 데이터")
print("기간: 2024-09-14 ~ 2025-09-12")
print("="*60)

# 백테스트 실행
test_data = {
    "strategy_id": "golden_cross",
    "start_date": "2024-09-14",  # 시작일
    "end_date": "2025-09-12",    # 종료일 (약 1년)
    "initial_capital": 10000000,  # 1천만원
    "stock_codes": ["005930"],    # 삼성전자
    "commission": 0.00015,        # 수수료 0.015%
    "slippage": 0.001            # 슬리피지 0.1%
}

print("\n📊 백테스트 파라미터:")
print(f"  - 전략: {test_data['strategy_id']}")
print(f"  - 종목: {test_data['stock_codes']}")
print(f"  - 기간: {test_data['start_date']} ~ {test_data['end_date']}")
print(f"  - 초기자본: {test_data['initial_capital']:,}원")

print("\n⏳ 백테스트 실행 중...")

try:
    response = requests.post(
        f"{BASE_URL}/api/backtest/run",
        json=test_data,
        timeout=60  # 60초 타임아웃
    )

    if response.status_code == 200:
        result = response.json()

        print("\n✅ 백테스트 성공!")
        print("\n📈 결과 요약:")
        print(f"  - 초기 자본: {result.get('initial_capital', 0):,.0f}원")
        print(f"  - 최종 자본: {result.get('final_capital', 0):,.0f}원")
        print(f"  - 총 수익: {result.get('total_return', 0):,.0f}원")
        print(f"  - 수익률: {result.get('total_return_rate', 0):.2f}%")
        print(f"  - 승률: {result.get('win_rate', 0):.2f}%")
        print(f"  - 총 거래: {result.get('total_trades', 0)}건")
        print(f"  - 승리: {result.get('winning_trades', 0)}건")
        print(f"  - 패배: {result.get('losing_trades', 0)}건")
        print(f"  - 최대 손실: {result.get('max_drawdown', 0):.2f}%")

        # 거래 내역 표시
        trades = result.get('trades', [])
        if trades:
            print(f"\n📝 최근 거래 5건:")
            for trade in trades[-5:]:
                trade_type = "매수" if trade.get('type') == 'buy' else "매도"
                date = trade.get('date', 'N/A')[:10] if trade.get('date') else 'N/A'
                print(f"  - {date}: {trade_type} {trade.get('quantity', 0)}주 @ {trade.get('price', 0):,.0f}원")
                if trade.get('type') == 'sell' and 'profit_rate' in trade:
                    print(f"    수익률: {trade.get('profit_rate', 0):.2f}%")

    elif response.status_code == 500:
        error_detail = response.json().get('detail', 'Unknown error')
        print(f"\n❌ 서버 오류: {error_detail}")
        print("\n디버깅 정보:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")

    else:
        print(f"\n❌ 오류 발생:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")

except requests.exceptions.Timeout:
    print("\n⏱️ 타임아웃: 백테스트가 60초 이상 소요됩니다.")
    print("더 짧은 기간으로 다시 시도해보세요.")

except requests.exceptions.ConnectionError:
    print("\n🔌 연결 오류: 서버에 연결할 수 없습니다.")
    print(f"서버 주소를 확인하세요: {BASE_URL}")

except Exception as e:
    print(f"\n❌ 예상치 못한 오류: {e}")

print("\n" + "="*60)