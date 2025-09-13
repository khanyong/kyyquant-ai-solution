"""
NAS API 상세 테스트
"""

import requests
import json

def test_nas_api():
    """NAS API 상세 테스트"""

    nas_url = "http://192.168.50.150:8080"

    print("=" * 60)
    print("NAS API 상세 테스트")
    print("=" * 60)

    # 1. 헬스체크
    print("\n1. 서버 헬스체크...")
    try:
        response = requests.get(f"{nas_url}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   상태: {data.get('status')}")
            print(f"   버전: {data.get('version')}")
            print(f"   Supabase: {data.get('supabase')}")
    except Exception as e:
        print(f"   오류: {e}")

    # 2. 전체 종목 리스트 조회 (페이지별)
    print("\n2. 전체 종목 리스트 조회...")

    # 2-1. 전체 조회
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list")
        if response.status_code == 200:
            data = response.json()
            total_stocks = len(data.get('data', []))
            print(f"   전체 조회: {total_stocks}개 종목")

            # 시장별 집계
            stocks = data.get('data', [])
            kospi = len([s for s in stocks if s['market'] == 'KOSPI'])
            kosdaq = len([s for s in stocks if s['market'] == 'KOSDAQ'])
            konex = len([s for s in stocks if s['market'] == 'KONEX'])

            print(f"     - KOSPI: {kospi}개")
            print(f"     - KOSDAQ: {kosdaq}개")
            print(f"     - KONEX: {konex}개")
    except Exception as e:
        print(f"   오류: {e}")

    # 2-2. KOSPI만 조회
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list?market=KOSPI")
        if response.status_code == 200:
            data = response.json()
            print(f"\n   KOSPI만 조회: {len(data.get('data', []))}개")
    except Exception as e:
        print(f"   KOSPI 조회 오류: {e}")

    # 2-3. KOSDAQ만 조회
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list?market=KOSDAQ")
        if response.status_code == 200:
            data = response.json()
            print(f"   KOSDAQ만 조회: {len(data.get('data', []))}개")
    except Exception as e:
        print(f"   KOSDAQ 조회 오류: {e}")

    # 3. 전체 종목 수 확인 (별도 엔드포인트)
    print("\n3. 전체 종목 수 확인...")
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list-full")
        if response.status_code == 200:
            data = response.json()
            print(f"   데이터베이스 총 종목 수: {data.get('total_count', 0)}개")
    except Exception as e:
        print(f"   오류: {e}")

    # 4. OpenAPI 스키마 확인
    print("\n4. API 엔드포인트 목록...")
    try:
        response = requests.get(f"{nas_url}/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            if 'paths' in openapi:
                for path in openapi['paths']:
                    methods = list(openapi['paths'][path].keys())
                    print(f"   {path}: {methods}")
    except Exception as e:
        print(f"   오류: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_nas_api()