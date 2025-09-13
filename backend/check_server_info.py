"""
NAS 서버 정보 상세 확인
"""

import requests
import json

def check_server():
    """서버 상세 정보 확인"""

    nas_url = "http://192.168.50.150:8080"

    print("=" * 60)
    print("NAS 서버 상세 정보")
    print("=" * 60)

    # 1. 루트 경로 확인
    print("\n1. 서버 기본 정보 (/):")
    try:
        response = requests.get(f"{nas_url}/")
        if response.status_code == 200:
            info = response.json()
            print(json.dumps(info, indent=2, ensure_ascii=False))

            # 버전 확인
            if 'version' in info:
                print(f"\n   서버 버전: {info['version']}")
    except Exception as e:
        print(f"   오류: {e}")

    # 2. docs 경로 시도 (FastAPI는 자동으로 /docs 제공)
    print("\n2. API 문서 확인 (/docs):")
    try:
        response = requests.get(f"{nas_url}/docs")
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            print("   FastAPI 문서 페이지 존재")
    except Exception as e:
        print(f"   오류: {e}")

    # 3. openapi.json 확인 (모든 엔드포인트 목록)
    print("\n3. OpenAPI 스키마 (/openapi.json):")
    try:
        response = requests.get(f"{nas_url}/openapi.json")
        if response.status_code == 200:
            openapi = response.json()

            # 경로 목록 출력
            if 'paths' in openapi:
                print("   사용 가능한 엔드포인트:")
                for path in openapi['paths']:
                    methods = list(openapi['paths'][path].keys())
                    print(f"     {path}: {methods}")
        else:
            print(f"   상태 코드: {response.status_code}")
    except Exception as e:
        print(f"   오류: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_server()