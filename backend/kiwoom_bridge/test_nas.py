"""
NAS 컨테이너 테스트 - IP 지정 가능
"""

import requests
import json
import sys

def test_nas(host="192.168.50.150", port="8080"):
    """NAS 테스트"""

    url = f"http://{host}:{port}"

    print("\n" + "="*60)
    print(f"NAS Container Test")
    print(f"URL: {url}")
    print("="*60 + "\n")

    # 1. 헬스체크
    print("1. Health Check...")
    try:
        resp = requests.get(f"{url}/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  OK - Server running")
            print(f"  - App version: {data.get('version')}")
            print(f"  - Backtest version: {data.get('backtest_version')}")
            print(f"  - Backtest API: {data.get('backtest_api')}")
        else:
            print(f"  Error: {resp.status_code}")
            return
    except Exception as e:
        print(f"  Connection failed: {e}")
        print("\n  [Tips]")
        print("  - Check if container is running in Container Manager")
        print("  - Check firewall settings for port 8080")
        return

    # 2. 버전 체크
    print("\n2. Version Check...")
    try:
        resp = requests.get(f"{url}/api/backtest/version", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  Code version: {data.get('version')}")
            print(f"  Build time: {data.get('build_time')}")
            print(f"  Core module: {data.get('core_module')}")
        else:
            print(f"  No version endpoint (old code)")
    except:
        print(f"  Version check failed")

    # 3. 백테스트
    print("\n3. Backtest Test...")
    try:
        data = {
            "strategy_id": "88d01e47-c979-4e80-bef8-746a53f3bbca",
            "stock_codes": ["005930"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 10000000
        }

        resp = requests.post(
            f"{url}/api/backtest/run",
            json=data,
            timeout=30
        )

        if resp.status_code == 200:
            result = resp.json()
            trades = result.get('summary', {}).get('total_trades', 0)
            print(f"  Backtest complete!")
            print(f"  Total trades: {trades}")

            if trades > 0:
                print(f"\n  SUCCESS! Trades generated: {trades}")
            else:
                print(f"\n  WARNING: 0 trades - check strategy/data")

        else:
            print(f"  Failed: {resp.status_code}")
            print(f"  Response: {resp.text[:200]}")

    except Exception as e:
        print(f"  Test failed: {e}")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    # Usage: python test_nas.py [host] [port]
    # Default: 192.168.50.150:8080
    host = sys.argv[1] if len(sys.argv) > 1 else "192.168.50.150"
    port = sys.argv[2] if len(sys.argv) > 2 else "8080"

    test_nas(host, port)