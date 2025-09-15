"""
컨테이너 테스트 스크립트 - 간단 버전
"""

import requests
import json
import sys
from datetime import datetime

def test_container(host="localhost", port="8080"):
    """컨테이너 테스트"""

    base_url = f"http://{host}:{port}"

    print("\n" + "="*60)
    print(f"🔍 CONTAINER TEST - {datetime.now()}")
    print(f"📍 URL: {base_url}")
    print("="*60 + "\n")

    # 1. 헬스체크
    print("1️⃣ 헬스체크...")
    try:
        resp = requests.get(f"{base_url}/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✅ 서버 실행 중")
            print(f"  - 앱 버전: {data.get('version')}")
            print(f"  - 백테스트 버전: {data.get('backtest_version')}")
            print(f"  - 백테스트 API: {data.get('backtest_api')}")
        else:
            print(f"  ❌ 오류: {resp.status_code}")
            return
    except Exception as e:
        print(f"  ❌ 연결 실패: {e}")
        return

    # 2. 버전 체크
    print("\n2️⃣ 버전 확인...")
    try:
        resp = requests.get(f"{base_url}/api/backtest/version", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✅ 코드 버전: {data.get('version')}")
            print(f"  - Core 모듈: {data.get('core_module')}")
            print(f"  - 작업 디렉토리: {data.get('working_dir')}")
        else:
            print(f"  ⚠️ 버전 엔드포인트 없음 (구버전)")
    except:
        print(f"  ⚠️ 버전 확인 실패")

    # 3. 백테스트 실행
    print("\n3️⃣ 백테스트 테스트...")
    try:
        data = {
            "strategy_id": "88d01e47-c979-4e80-bef8-746a53f3bbca",
            "stock_codes": ["005930"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 10000000
        }

        print(f"  - 전략 ID: {data['strategy_id']}")
        print(f"  - 종목: {data['stock_codes'][0]}")
        print(f"  - 기간: {data['start_date']} ~ {data['end_date']}")

        resp = requests.post(
            f"{base_url}/api/backtest/run",
            json=data,
            timeout=30
        )

        if resp.status_code == 200:
            result = resp.json()
            trades = result.get('summary', {}).get('total_trades', 0)
            print(f"\n  ✅ 백테스트 완료!")
            print(f"  📊 거래 횟수: {trades}회")

            if trades > 0:
                print(f"  ✅✅✅ 성공! 거래가 발생했습니다! ✅✅✅")
            else:
                print(f"  ⚠️⚠️⚠️ 거래가 0회입니다. 확인 필요! ⚠️⚠️⚠️")

        else:
            print(f"  ❌ 실행 실패: {resp.status_code}")
            print(f"  응답: {resp.text[:200]}")

    except Exception as e:
        print(f"  ❌ 테스트 실패: {e}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    # 인자: python test_container.py [host] [port]
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = sys.argv[2] if len(sys.argv) > 2 else "8080"

    test_container(host, port)