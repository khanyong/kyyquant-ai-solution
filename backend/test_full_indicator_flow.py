"""
전체 지표 계산 프로세스 검증
- 충분한 데이터가 있다고 가정
- 지표 계산 API 호출
- 결과 검증
"""
import requests
import json
from datetime import datetime

# Backend API URL
BASE_URL = "http://localhost:8000"

def test_indicator_calculation():
    """지표 계산 API 테스트"""

    print("=" * 60)
    print("지표 계산 API 전체 프로세스 검증")
    print("=" * 60)
    print()

    # 1. Health check
    print("1. API Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/indicators/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ API 정상: {response.json()}")
        else:
            print(f"   ❌ API 오류: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 연결 실패: {e}")
        print("   Backend 서버가 실행 중인지 확인하세요: python backend/main.py")
        return

    print()

    # 2. 지표 계산 요청
    print("2. 지표 계산 요청...")
    request_data = {
        "stock_code": "005930",
        "indicators": [
            {"name": "ma", "params": {"period": 20}},
            {"name": "ma", "params": {"period": 12}},
            {"name": "bollinger", "params": {"period": 20, "std_dev": 2}},
            {"name": "rsi", "params": {"period": 14}},
            {"name": "dmi", "params": {"period": 14}}
        ],
        "days": 60
    }

    print(f"   요청 데이터:")
    print(f"   - 종목: {request_data['stock_code']}")
    print(f"   - 지표: {len(request_data['indicators'])}개")
    print(f"   - 기간: {request_data['days']}일")
    print()

    try:
        response = requests.post(
            f"{BASE_URL}/api/indicators/calculate",
            json=request_data,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print("   ✅ 계산 성공!")
            print()
            print("3. 계산 결과:")
            print(f"   - 종목: {result['stock_code']}")
            print(f"   - 계산 시각: {result['calculated_at']}")
            print(f"   - 지표 개수: {len(result['indicators'])}개")
            print()
            print("   지표 값:")

            indicators = result['indicators']

            # 지표별로 출력
            if 'ma_20' in indicators:
                print(f"   • MA(20):  {indicators['ma_20']:,.0f}원")
            else:
                print(f"   • MA(20):  ❌ 계산 실패 (NaN)")

            if 'ma_12' in indicators:
                print(f"   • MA(12):  {indicators['ma_12']:,.0f}원")
            else:
                print(f"   • MA(12):  ❌ 계산 실패 (NaN)")

            if 'bollinger_upper' in indicators:
                print(f"   • Bollinger Upper: {indicators['bollinger_upper']:,.0f}원")
                print(f"   • Bollinger Middle: {indicators['bollinger_middle']:,.0f}원")
                print(f"   • Bollinger Lower: {indicators['bollinger_lower']:,.0f}원")
            else:
                print(f"   • Bollinger: ❌ 계산 실패 (NaN)")

            if 'rsi' in indicators:
                print(f"   • RSI(14): {indicators['rsi']:.2f}")
            else:
                print(f"   • RSI(14): ❌ 계산 실패 (NaN)")

            if 'dmi_plus' in indicators:
                print(f"   • DMI +DI: {indicators['dmi_plus']:.2f}")
                print(f"   • DMI -DI: {indicators['dmi_minus']:.2f}")
                print(f"   • DMI ADX: {indicators['adx']:.2f}")
            else:
                print(f"   • DMI: ❌ 계산 실패 (NaN)")

            if 'close' in indicators:
                print(f"   • 종가:    {indicators['close']:,.0f}원")

            print()

            # 4. 결과 검증
            print("4. 결과 검증:")

            # NaN이 아닌 지표 개수 확인
            valid_indicators = [k for k, v in indicators.items()
                               if v is not None and str(v) != 'nan']

            print(f"   - 유효한 지표: {len(valid_indicators)}/{len(indicators)}개")

            # 필수 지표 확인
            required_indicators = ['ma_20', 'ma_12', 'close']
            missing = [ind for ind in required_indicators if ind not in indicators]

            if missing:
                print(f"   ❌ 누락된 필수 지표: {', '.join(missing)}")
                print(f"   → 데이터가 부족합니다 (최소 20일 필요)")
            else:
                print(f"   ✅ 필수 지표 모두 계산됨")

            print()

            # 5. n8n 통합 검증
            print("5. n8n 통합 준비 상태:")
            if not missing:
                print("   ✅ Backend API 정상 작동")
                print("   ✅ 지표 계산 성공")
                print("   → n8n workflow v21에서 이 API를 호출하면 됩니다")
                print()
                print("   n8n HTTP Request 노드 설정:")
                print(f"   - Method: POST")
                print(f"   - URL: {BASE_URL}/api/indicators/calculate")
                print(f"   - Body: JSON")
                print(f"   - 예시: {json.dumps(request_data, indent=2, ensure_ascii=False)}")
            else:
                print("   ❌ 데이터 부족으로 지표 계산 실패")
                print("   → 월요일에 update_daily_prices.py 실행 필요")

        else:
            error_data = response.json()
            print(f"   ❌ 계산 실패: {response.status_code}")
            print(f"   에러: {error_data.get('detail', 'Unknown error')}")

    except Exception as e:
        print(f"   ❌ 요청 실패: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)


if __name__ == "__main__":
    test_indicator_calculation()
