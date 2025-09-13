"""
NAS 서버의 API 라우트 확인
"""

import requests

def test_api_routes():
    """NAS 서버의 사용 가능한 엔드포인트 확인"""

    nas_url = "http://192.168.50.150:8080"

    print("=" * 60)
    print("NAS 서버 API 엔드포인트 테스트")
    print("=" * 60)

    # 테스트할 엔드포인트들
    endpoints = [
        {"method": "GET", "path": "/", "desc": "루트 경로"},
        {"method": "POST", "path": "/api/test", "desc": "테스트 엔드포인트"},
        {"method": "POST", "path": "/api/market/current-price", "desc": "현재가 조회", "data": {"stock_code": "005930"}},
        {"method": "GET", "path": "/api/market/stock-list", "desc": "종목 리스트 (새로 추가)"},
        {"method": "POST", "path": "/api/backtest/run", "desc": "백테스트"},
    ]

    for ep in endpoints:
        print(f"\n[{ep['method']}] {ep['path']}")
        print(f"   설명: {ep['desc']}")

        try:
            if ep['method'] == "GET":
                response = requests.get(f"{nas_url}{ep['path']}", timeout=5)
            else:
                data = ep.get('data', {})
                response = requests.post(f"{nas_url}{ep['path']}", json=data, timeout=5)

            print(f"   상태: {response.status_code}")

            if response.status_code == 200:
                print(f"   OK 성공")
                # 응답 내용 일부 출력
                result = response.json()
                if 'success' in result:
                    print(f"   응답: success={result['success']}")
                if 'count' in result:
                    print(f"   데이터 수: {result['count']}")
            elif response.status_code == 404:
                print(f"   X 엔드포인트 없음 (404)")
            else:
                print(f"   ! 오류: {response.status_code}")

        except Exception as e:
            print(f"   X 연결 실패: {e}")

    print("\n" + "=" * 60)
    print("결과 요약:")
    print("- 404 에러가 나는 엔드포인트는 서버에 구현되지 않음")
    print("- /api/market/stock-list가 404라면 main.py 업데이트 필요")
    print("=" * 60)

if __name__ == "__main__":
    test_api_routes()