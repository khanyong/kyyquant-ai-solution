"""
키움증권 REST API 연결 테스트
직접 API 호출하여 문제 파악
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_kiwoom_api():
    """키움 API 직접 테스트"""

    # API 정보
    app_key = os.getenv('KIWOOM_APP_KEY')
    app_secret = os.getenv('KIWOOM_APP_SECRET')

    print("=" * 60)
    print("키움증권 REST API 테스트")
    print("=" * 60)

    # 가능한 URL들 테스트
    urls = [
        "https://openapi.kiwoom.com:9443",
        "https://openapivts.kiwoom.com:29443",
        "https://openapi.koreainvestment.com:9443",
        "https://openapivts.koreainvestment.com:29443"
    ]

    for base_url in urls:
        print(f"\n테스트 URL: {base_url}")

        # 1. Health Check
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            print(f"  Health Check: {response.status_code}")
        except Exception as e:
            print(f"  Health Check 실패: {e}")

        # 2. Token 발급 테스트 - form-data
        try:
            token_url = f"{base_url}/oauth2/token"
            data = {
                "grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret
            }

            # form-data로 시도
            response = requests.post(token_url, data=data, timeout=5)
            print(f"  Token (form-data): {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 성공! 이 URL과 form-data 방식 사용")
                print(f"  응답: {response.json()}")
                return base_url, "form-data"

        except Exception as e:
            print(f"  Token (form-data) 실패: {e}")

        # 3. Token 발급 테스트 - JSON
        try:
            headers = {"content-type": "application/json"}
            response = requests.post(token_url, json=data, headers=headers, timeout=5)
            print(f"  Token (JSON): {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ 성공! 이 URL과 JSON 방식 사용")
                print(f"  응답: {response.json()}")
                return base_url, "json"

        except Exception as e:
            print(f"  Token (JSON) 실패: {e}")

    print("\n" + "=" * 60)
    print("❌ 모든 URL 테스트 실패")
    print("=" * 60)

    print("""
가능한 원인:
1. API 키가 잘못됨
2. 네트워크 차단 (방화벽)
3. API 서버 점검 중
4. 키움증권 OpenAPI+는 실제로 COM 기반이며, REST API는 Bridge 서버 필요

해결 방법:
1. 키움증권 OpenAPI+ 홈페이지에서 API 키 재확인
2. Windows에서 키움 OpenAPI+ 설치 후 Bridge 서버 실행
3. Mock 데이터로 백테스트 진행
    """)

    return None, None

if __name__ == "__main__":
    result = test_kiwoom_api()

    if result[0]:
        print(f"\n✅ 사용할 설정:")
        print(f"  URL: {result[0]}")
        print(f"  방식: {result[1]}")