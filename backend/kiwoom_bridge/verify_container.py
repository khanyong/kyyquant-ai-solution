"""
컨테이너 코드 버전 확인 스크립트
Synology NAS 컨테이너가 최신 코드를 사용하는지 확인
"""

import requests
import json
import sys
import hashlib
import os
from datetime import datetime

def check_version(url="http://localhost:8080"):
    """컨테이너 버전 확인"""

    print("\n" + "="*70)
    print("🔍 CONTAINER VERSION CHECK")
    print("="*70 + "\n")

    # 1. 기본 헬스체크
    try:
        print("1️⃣ 헬스체크 중...")
        response = requests.get(f"{url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 서버 상태: {data.get('status')}")
            print(f"  📌 앱 버전: {data.get('version')}")
            print(f"  📌 백테스트 버전: {data.get('backtest_version')}")
            print(f"  📌 빌드 시간: {data.get('build_time')}")
            print(f"  📌 백테스트 API: {data.get('backtest_api')}")
            print(f"  📌 작업 디렉토리: {data.get('working_dir')}")
        else:
            print(f"  ❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 연결 실패: {e}")
        print(f"  💡 컨테이너가 실행 중인지 확인하세요")
        return False

    # 2. 버전 상세 정보
    try:
        print("\n2️⃣ 버전 상세 정보 확인 중...")
        response = requests.get(f"{url}/api/backtest/version", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ 코드 버전: {data.get('version')}")
            print(f"  📌 빌드 시간: {data.get('build_time')}")
            print(f"  📌 Core 모듈: {data.get('core_module')}")
            print(f"  📌 Advanced Engine: {data.get('advanced_engine')}")
            print(f"  📌 Strategy Engine: {data.get('strategy_engine')}")

            # 파일 해시 확인
            print("\n  📁 파일 해시값:")
            file_hashes = data.get('file_hashes', {})
            for file_name, hash_val in file_hashes.items():
                status = "✅" if hash_val not in ["NOT_FOUND", "ERROR"] else "❌"
                print(f"    {status} {file_name}: {hash_val}")

            # 로컬 파일과 비교
            print("\n3️⃣ 로컬 파일과 비교 중...")
            local_hashes = calculate_local_hashes()

            all_match = True
            for file_name, remote_hash in file_hashes.items():
                local_hash = local_hashes.get(file_name, "NOT_FOUND")
                if remote_hash != local_hash:
                    all_match = False
                    print(f"  ⚠️ {file_name}: 불일치!")
                    print(f"     로컬: {local_hash}")
                    print(f"     컨테이너: {remote_hash}")
                else:
                    if remote_hash not in ["NOT_FOUND", "ERROR"]:
                        print(f"  ✅ {file_name}: 일치")

            if all_match:
                print("\n✅ 모든 파일이 최신 버전입니다!")
            else:
                print("\n⚠️ 일부 파일이 다릅니다. 재빌드가 필요할 수 있습니다.")

        else:
            print(f"  ❌ 버전 엔드포인트 없음 (구버전 코드 사용 중)")
            print(f"  💡 컨테이너를 재빌드하세요")
            return False

    except Exception as e:
        print(f"  ❌ 버전 확인 실패: {e}")
        return False

    # 3. 간단한 백테스트 실행
    print("\n4️⃣ 백테스트 API 테스트 중...")
    try:
        test_data = {
            "strategy_id": "88d01e47-c979-4e80-bef8-746a53f3bbca",
            "stock_codes": ["005930"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 10000000
        }

        response = requests.post(
            f"{url}/api/backtest/run",
            json=test_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            trades = result.get('summary', {}).get('total_trades', 0)
            print(f"  ✅ 백테스트 실행 성공")
            print(f"  📊 거래 횟수: {trades}회")

            if trades == 0:
                print(f"  ⚠️ 거래가 발생하지 않음 - 전략 또는 데이터 확인 필요")
            else:
                print(f"  ✅ 정상적으로 거래가 발생함!")

        else:
            print(f"  ❌ 백테스트 실행 실패: {response.status_code}")
            print(f"  응답: {response.text[:200]}")

    except Exception as e:
        print(f"  ❌ 백테스트 테스트 실패: {e}")

    print("\n" + "="*70 + "\n")
    return True

def calculate_local_hashes():
    """로컬 파일 해시 계산"""
    hashes = {}
    base_dir = os.path.dirname(__file__)

    files_to_check = [
        'backtest_api.py',
        'backtest_engine_advanced.py',
        'core/indicators.py',
        'core/conditions.py',
        'core/naming.py'
    ]

    for file_name in files_to_check:
        try:
            file_path = os.path.join(base_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                    hashes[file_name] = hashlib.md5(content).hexdigest()[:8]
            else:
                hashes[file_name] = "NOT_FOUND"
        except Exception as e:
            hashes[file_name] = f"ERROR"

    return hashes

def suggest_fix():
    """문제 해결 방법 제안"""
    print("\n💡 문제 해결 방법:")
    print("\n1. 컨테이너 재빌드 (Synology Container Manager):")
    print("   - 프로젝트 선택 → 액션 → 빌드")
    print("   - 또는: 프로젝트 삭제 → 새로 생성")
    print("\n2. 캐시 없이 재빌드:")
    print("   - SSH 접속 후: docker-compose build --no-cache")
    print("\n3. 볼륨 마운트 확인 (docker-compose.yml):")
    print("   - volumes 섹션에 ./:/app 있는지 확인")
    print("\n4. 파일 동기화 확인:")
    print("   - NAS에 파일이 제대로 업로드되었는지 확인")
    print("   - File Station에서 파일 수정 시간 확인")

if __name__ == "__main__":
    # 명령줄 인자로 URL 받기
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"

    print(f"🔗 대상 서버: {url}")

    if not check_version(url):
        suggest_fix()