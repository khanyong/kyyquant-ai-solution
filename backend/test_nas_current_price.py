"""
NAS 서버의 현재가 조회 API 테스트
"""

import requests
import json

def test_current_price():
    """NAS 서버에서 현재가 조회 테스트"""

    # NAS 서버 URL
    base_url = "http://192.168.50.150:8080"

    print("=" * 60)
    print("NAS 키움 REST API Bridge - 현재가 조회 테스트")
    print("=" * 60)

    # 테스트할 종목들
    stock_codes = ['005930', '000660', '035720']  # 삼성전자, SK하이닉스, 카카오

    for stock_code in stock_codes:
        print(f"\n종목코드: {stock_code}")

        # API 호출
        url = f"{base_url}/api/market/current-price"
        payload = {
            "stock_code": stock_code
        }

        try:
            response = requests.post(url, json=payload, timeout=10)

            print(f"상태 코드: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"응답 데이터:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

                # 데이터가 Mock인지 실제인지 확인
                if 'mock' in str(data).lower() or data.get('price', 0) == 50000:
                    print("⚠️ Mock 데이터로 보입니다")
                else:
                    print("✅ 실제 데이터로 보입니다")
            else:
                print(f"오류 응답: {response.text}")

        except Exception as e:
            print(f"❌ 오류: {e}")

    print("\n" + "=" * 60)
    print("다음 단계:")
    print("1. Mock 데이터가 나온다면 → data_downloader.py 실행 필요")
    print("2. 연결 오류가 나온다면 → 키움 API 키 설정 확인")
    print("3. 실제 데이터가 나온다면 → 성공!")
    print("=" * 60)

if __name__ == "__main__":
    test_current_price()