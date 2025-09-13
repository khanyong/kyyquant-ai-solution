"""
키움 API 서버 직접 연결 테스트
네트워크 연결 문제 확인
"""

import socket
import ssl
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """연결 테스트"""

    print("=" * 60)
    print("키움 API 서버 연결 테스트")
    print("=" * 60)

    # 1. DNS 확인
    print("\n1. DNS 확인:")
    try:
        ip = socket.gethostbyname('openapi.kiwoom.com')
        print(f"   ✅ openapi.kiwoom.com -> {ip}")
    except Exception as e:
        print(f"   ❌ DNS 확인 실패: {e}")

    # 2. 포트 연결 테스트
    print("\n2. 포트 9443 연결 테스트:")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('openapi.kiwoom.com', 9443))
        if result == 0:
            print(f"   ✅ 포트 9443 연결 가능")
        else:
            print(f"   ❌ 포트 9443 연결 실패 (에러 코드: {result})")
        sock.close()
    except Exception as e:
        print(f"   ❌ 소켓 연결 실패: {e}")

    # 3. HTTPS 연결 테스트
    print("\n3. HTTPS 연결 테스트:")
    try:
        response = requests.get('https://openapi.kiwoom.com:9443/',
                              timeout=5,
                              verify=False)  # SSL 검증 임시 비활성화
        print(f"   ✅ HTTPS 연결 성공 (상태 코드: {response.status_code})")
    except requests.exceptions.SSLError as e:
        print(f"   ⚠️ SSL 오류: {e}")
    except requests.exceptions.ConnectTimeout:
        print(f"   ❌ 연결 시간 초과 (5초)")
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ 연결 오류: {e}")
    except Exception as e:
        print(f"   ❌ 기타 오류: {e}")

    # 4. 대체 URL 테스트
    print("\n4. 대체 URL 테스트:")

    # 한국투자증권 API (혹시 이것일 수도)
    alt_urls = [
        'https://openapi.koreainvestment.com:9443',
        'https://openapivts.koreainvestment.com:29443',
    ]

    for url in alt_urls:
        try:
            response = requests.get(url, timeout=3, verify=False)
            print(f"   ✅ {url} - 연결 성공")
        except:
            print(f"   ❌ {url} - 연결 실패")

    print("\n" + "=" * 60)
    print("가능한 원인:")
    print("=" * 60)
    print("""
1. 방화벽이 9443 포트를 차단
2. 키움 API 서버가 현재 점검 중
3. VPN이나 프록시 사용 중
4. 회사/기관 네트워크에서 차단
5. API URL이 변경됨

해결 방법:
1. Windows 방화벽에서 9443 포트 허용
2. 다른 네트워크(모바일 핫스팟 등)로 테스트
3. VPN 끄고 시도
4. 키움증권 고객센터 문의 (1544-9000)

대안:
- Mock 데이터로 백테스트 진행
- 이미 수집된 과거 데이터 사용
    """)

if __name__ == "__main__":
    test_connection()