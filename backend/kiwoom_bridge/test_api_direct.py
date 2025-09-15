"""
백테스트 API 직접 호출 테스트
"""

import requests
import json
from datetime import datetime, timedelta

# API 엔드포인트 - NAS IP 주소로 변경하세요
# 예: "http://192.168.1.100:8001/api/backtest/run"
API_URL = "http://[NAS_IP]:8001/api/backtest/run"  # NAS IP로 변경 필요!

# 요청 데이터
request_data = {
    "strategy_id": "test_strategy",
    "stock_codes": ["005930"],  # 삼성전자
    "start_date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
    "end_date": datetime.now().strftime("%Y-%m-%d"),
    "initial_capital": 10000000,
    "commission": 0.00015,
    "slippage": 0.001,
    "data_interval": "1d",
    "filtering_mode": "pre-filter",
    "use_cached_data": False,
    "parameters": {
        "strategy_config": {
            "templateId": "golden-cross",
            "indicators": [
                {"type": "ma", "params": {"period": 20}},
                {"type": "ma", "params": {"period": 60}}
            ],
            "buyConditions": [
                {"indicator": "ma_20", "operator": "cross_above", "value": "ma_60"}
            ],
            "sellConditions": [
                {"indicator": "ma_20", "operator": "cross_below", "value": "ma_60"}
            ],
            "stopLoss": 5,
            "takeProfit": 10
        }
    }
}

print("="*60)
print("백테스트 API 직접 호출")
print("="*60)

print(f"\nAPI URL: {API_URL}")
print(f"\n요청 데이터:")
print(json.dumps(request_data, indent=2, ensure_ascii=False))

try:
    print("\n📡 API 호출 중...")
    response = requests.post(API_URL, json=request_data, timeout=30)

    print(f"\n응답 상태: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\n✅ 백테스트 성공!")
        print(f"  총 거래: {result.get('total_trades', 0)}")
        print(f"  매수: {result.get('buy_count', 0)}")
        print(f"  매도: {result.get('sell_count', 0)}")
        print(f"  수익률: {result.get('total_return', 0):.2f}%")

        if result.get('trades'):
            print(f"\n거래 내역 (처음 3개):")
            for trade in result.get('trades', [])[:3]:
                print(f"  {trade}")
    else:
        print(f"\n❌ API 오류:")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ Docker 컨테이너에 연결할 수 없습니다.")
    print("   docker ps로 컨테이너 실행 상태를 확인하세요.")

except requests.exceptions.Timeout:
    print("\n⏱️ 요청 시간 초과")

except Exception as e:
    print(f"\n❌ 오류: {e}")

print("\n" + "="*60)
print("Docker 로그 확인:")
print("docker logs kiwoom-bridge --tail 50")
print("="*60)