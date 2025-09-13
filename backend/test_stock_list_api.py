"""
종목 리스트 API 테스트
"""

import requests
import json

def test_stock_list_api():
    """종목 리스트 API 테스트"""

    # NAS 서버 URL
    nas_url = "http://192.168.50.150:8080"

    print("=" * 60)
    print("종목 리스트 API 테스트")
    print("=" * 60)

    # 1. 전체 종목 리스트 조회
    print("\n1. 전체 종목 리스트 조회")
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

    # 2. KOSPI 종목만 조회
    print("\n2. KOSPI 종목만 조회")
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list?market=KOSPI")
        print(f"   상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   KOSPI 종목 수: {data.get('count', 0)}개")

    except Exception as e:
        print(f"   오류: {e}")

    # 3. KOSDAQ 종목만 조회
    print("\n3. KOSDAQ 종목만 조회")
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list?market=KOSDAQ")
        print(f"   상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   KOSDAQ 종목 수: {data.get('count', 0)}개")

    except Exception as e:
        print(f"   오류: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_stock_list_api()