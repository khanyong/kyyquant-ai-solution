"""
백테스트 API 최소 요청 테스트 - 필수 필드만 전송
"""
import requests
import json

# 필수 필드만 포함한 요청
url = "http://192.168.50.150:8080/api/backtest/run"

# 최소 필수 페이로드
payload = {
    "strategy_id": "fcfbcb90-d074-449e-a60f-a3c2a86fe74f",
    "stock_codes": ["005930"],
    "start_date": "2024-09-14",
    "end_date": "2025-09-12",
    "initial_capital": 10000000
}

# 브라우저와 동일한 헤더
headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:5173",
    "Referer": "http://localhost:5173/",
}

print("=" * 60)
print("백테스트 API 최소 요청 테스트")
print("=" * 60)
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
print("=" * 60)

try:
    # 요청 전송
    response = requests.post(url, json=payload, headers=headers)

    print(f"\n응답 상태 코드: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\nSuccess!")

        # 결과 요약
        print("\n===== 백테스트 결과 =====")
        if "total_return" in result:
            print(f"총 수익률: {result['total_return']:.2%}")
        if "sharpe_ratio" in result:
            print(f"샤프 비율: {result['sharpe_ratio']:.2f}")
        if "max_drawdown" in result:
            print(f"최대 낙폭: {result['max_drawdown']:.2%}")
        if "total_trades" in result:
            print(f"총 거래 횟수: {result['total_trades']}")
        if "data_source" in result:
            print(f"데이터 소스: {result['data_source']}")

        # 거래 내역 확인
        if "trades" in result and result["trades"]:
            print("\n===== 거래 내역 (처음 3개) =====")
            for i, trade in enumerate(result["trades"][:3], 1):
                print(f"\n거래 {i}:")
                print(f"  날짜: {trade.get('date', 'N/A')}")
                print(f"  유형: {trade.get('type', 'N/A')}")
                print(f"  가격: {trade.get('price', 'N/A')}")
                print(f"  수량: {trade.get('quantity', 'N/A')}")
                if "buy_reason" in trade:
                    print(f"  매수 이유: {trade['buy_reason']}")
                if "sell_reason" in trade:
                    print(f"  매도 이유: {trade['sell_reason']}")

    else:
        print(f"\nFailed!")
        print(f"Error response: {response.text[:500]}")
        if response.status_code == 422:
            try:
                error_detail = response.json()
                print(f"Validation error details: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
            except:
                pass

except Exception as e:
    print(f"\nException occurred: {e}")
    import traceback
    traceback.print_exc()