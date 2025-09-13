"""
시놀로지 NAS에서 키움 REST API 연결 테스트
Linux 환경에서 실행 가능
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_kiwoom_rest_api():
    """NAS에서 키움 REST API 테스트"""

    print("=" * 60)
    print("시놀로지 NAS - 키움 REST API 연결 테스트")
    print("=" * 60)

    # 환경변수에서 API 키 로드
    app_key = os.getenv('KIWOOM_APP_KEY')
    app_secret = os.getenv('KIWOOM_APP_SECRET')

    print(f"\n1. API 키 확인:")
    print(f"   APP_KEY: {app_key[:10]}..." if app_key else "   APP_KEY: 없음")
    print(f"   APP_SECRET: {app_secret[:10]}..." if app_secret else "   APP_SECRET: 없음")

    # 키움 REST API URL들
    urls = [
        {
            "name": "키움 REST API (기본)",
            "url": "https://openapi.kiwoom.com:9443/oauth2/token",
            "method": "form"
        },
        {
            "name": "키움 REST API (대체 포트 8443)",
            "url": "https://openapi.kiwoom.com:8443/oauth2/token",
            "method": "form"
        },
        {
            "name": "키움 REST API (HTTP)",
            "url": "http://openapi.kiwoom.com:8080/oauth2/token",
            "method": "form"
        }
    ]

    print(f"\n2. 연결 테스트:")

    for api in urls:
        print(f"\n   테스트: {api['name']}")
        print(f"   URL: {api['url']}")

        try:
            if api['method'] == 'form':
                # Form data 방식
                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                data = {
                    "grant_type": "client_credentials",
                    "appkey": app_key,
                    "appsecret": app_secret
                }
                response = requests.post(
                    api['url'],
                    data=data,
                    headers=headers,
                    timeout=10,
                    verify=False  # SSL 검증 임시 비활성화
                )
            else:
                # JSON 방식
                headers = {"Content-Type": "application/json"}
                data = {
                    "grant_type": "client_credentials",
                    "appkey": app_key,
                    "appsecret": app_secret
                }
                response = requests.post(
                    api['url'],
                    json=data,
                    headers=headers,
                    timeout=10,
                    verify=False
                )

            print(f"   상태 코드: {response.status_code}")

            if response.status_code == 200:
                print(f"   ✅ 성공! 토큰 발급 완료")
                token_data = response.json()
                print(f"   토큰: {token_data.get('access_token', '')[:50]}...")
                return api['url'], token_data
            else:
                print(f"   ❌ 실패: {response.text[:100]}")

        except requests.exceptions.ConnectTimeout:
            print(f"   ❌ 연결 시간 초과")
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ 연결 오류: {str(e)[:100]}")
        except Exception as e:
            print(f"   ❌ 기타 오류: {str(e)[:100]}")

    print("\n" + "=" * 60)
    print("해결 방안:")
    print("=" * 60)
    print("""
    1. NAS 방화벽 설정 확인
       - DSM > 제어판 > 보안 > 방화벽
       - 9443 포트 허용 규칙 추가

    2. Docker 네트워크 설정
       - bridge 네트워크 사용
       - 포트 매핑 확인

    3. 키움증권 API 서비스 확인
       - API 서비스 활성화 여부
       - IP 화이트리스트 설정

    4. NAS에서 직접 실행
       ssh admin@nas_ip
       cd /volume1/docker/auto_stock
       python test_nas_connection.py
    """)

if __name__ == "__main__":
    test_kiwoom_rest_api()