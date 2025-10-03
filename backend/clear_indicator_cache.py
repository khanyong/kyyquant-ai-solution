"""
백테스트 API 서버 캐시 클리어 요청
"""
import requests

# NAS 서버 주소
NAS_URL = "http://192.168.0.100:8000"  # 실제 NAS 주소로 변경 필요

def clear_cache():
    """캐시 클리어 API 호출"""
    try:
        # 만약 캐시 클리어 엔드포인트가 있다면
        response = requests.post(f"{NAS_URL}/api/backtest/clear-cache")
        print(f"Cache clear response: {response.status_code}")
        print(response.json())
    except Exception as e:
        print(f"Failed to clear cache: {e}")
        print("\n대안: NAS 서버에서 백테스트 API 재시작이 필요합니다.")
        print("SSH로 접속하여 다음 명령 실행:")
        print("  docker restart auto_stock_backend")
        print("  또는")
        print("  docker-compose restart backend")

if __name__ == '__main__':
    print("=" * 60)
    print("Indicator Cache Clear")
    print("=" * 60)
    clear_cache()
