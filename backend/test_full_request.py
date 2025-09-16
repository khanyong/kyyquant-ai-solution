"""
백테스트 API 전체 요청 테스트 - 브라우저와 동일한 조건
"""
import requests
import json

# 브라우저와 동일한 요청 생성
url = "http://192.168.50.150:8080/api/backtest/run"

# 실제 브라우저가 보내는 요청과 동일한 페이로드
payload = {
    "strategy_id": "fcfbcb90-d074-449e-a60f-a3c2a86fe74f",
    "stock_codes": ["005930"],
    "start_date": "2024-09-14",
    "end_date": "2025-09-12",
    "initial_capital": 10000000,
    "commission": 0.00015,
    "slippage": 0.001,
    "parameters": {},
    # 추가 필드들 (브라우저가 보낼 수 있는 것들)
    "data_interval": "1d",
    "filtering_mode": "pre-filter",
    "use_cached_data": True,
    "filter_id": None
}

# 브라우저와 동일한 헤더
headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:5173",
    "Referer": "http://localhost:5173/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

print("=" * 60)
print("백테스트 API 전체 테스트")
print("=" * 60)
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("=" * 60)

try:
    # 요청 전송
    response = requests.post(url, json=payload, headers=headers)

    print(f"\n응답 상태 코드: {response.status_code}")
    print(f"응답 헤더: {dict(response.headers)}")

    if response.status_code == 200:
        result = response.json()
        print("\nSuccess!")
        print(f"Result: {json.dumps(result, indent=2)[:500]}...")
    else:
        print(f"\nFailed!")
        print(f"Error response: {response.text}")
        if response.status_code == 422:
            try:
                error_detail = response.json()
                print(f"Validation error details: {json.dumps(error_detail, indent=2)}")
            except:
                pass

except Exception as e:
    print(f"\nException occurred: {e}")
    import traceback
    traceback.print_exc()