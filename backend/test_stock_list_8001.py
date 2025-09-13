"""
종목 리스트 API 테스트 (포트 8001)
"""

import requests
import json

def test_stock_list_api():
    """종목 리스트 API 테스트"""

    # NAS 서버 URL - 포트 8001 시도
    nas_url = "http://192.168.50.150:8001"

    print("=" * 60)
    print("종목 리스트 API 테스트 (포트 8001)")
    print("=" * 60)

    # 1. 서버 상태 확인
    print("\n1. 서버 상태 확인")
    try:
        response = requests.get(f"{nas_url}/", timeout=5)
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            print(f"   서버 정보: {response.json()}")
    except Exception as e:
        print(f"   연결 실패: {e}")
        print("\n포트 8001로 연결할 수 없습니다.")
        print("8080 포트의 서버가 다른 버전일 수 있습니다.")
        return

    # 2. 전체 종목 리스트 조회
    print("\n2. 전체 종목 리스트 조회")
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list")
        print(f"   상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   성공: {data.get('count', 0)}개 종목")

            # 처음 5개 종목 출력
            if data.get('data'):
                print("\n   샘플 데이터 (처음 5개):")
                for stock in data['data'][:5]:
                    print(f"     - {stock['code']}: {stock['name']} ({stock['market']})")
        else:
            print(f"   실패: {response.text}")

    except Exception as e:
        print(f"   오류: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_stock_list_api()