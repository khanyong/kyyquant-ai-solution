"""
NAS 백테스트 시스템 테스트
strategy_engine 통합 후 작동 확인
"""

import requests
import json
from datetime import datetime, timedelta

# NAS 서버 설정
NAS_URL = "http://192.168.50.150:8080"  # NAS 백테스트 서버

def test_health_check():
    """서버 상태 확인"""
    print("="*60)
    print("1. 서버 상태 확인")
    print("="*60)

    try:
        response = requests.get(f"{NAS_URL}/")
        if response.status_code == 200:
            print("✅ 서버가 정상 작동 중입니다.")
            print(f"응답: {response.json()}")
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

    return True

def test_backtest_with_strategy():
    """전략 백테스트 실행"""
    print("\n" + "="*60)
    print("2. 전략 백테스트 테스트")
    print("="*60)

    # 테스트용 전략 설정
    test_request = {
        "strategy_id": "test-strategy-001",
        "stock_codes": ["005930", "000660"],  # 삼성전자, SK하이닉스
        "start_date": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
        "end_date": datetime.now().strftime("%Y-%m-%d"),
        "initial_capital": 10000000,
        "commission": 0.00015,
        "slippage": 0.001,
        "parameters": {
            "indicators": [
                {"type": "RSI", "params": {"period": 14}},
                {"type": "SMA", "params": {"period": 20}},
                {"type": "SMA", "params": {"period": 50}}
            ],
            "buyConditions": [
                {
                    "indicator": "rsi",
                    "operator": "<",
                    "value": 30,
                    "combineWith": "AND"
                }
            ],
            "sellConditions": [
                {
                    "indicator": "rsi",
                    "operator": ">",
                    "value": 70,
                    "combineWith": "OR"
                },
                {
                    "indicator": "close",
                    "operator": "<",
                    "value": "sma_20",
                    "combineWith": "OR"
                }
            ]
        }
    }

    print("전략 설정:")
    print(f"- 종목: {', '.join(test_request['stock_codes'])}")
    print(f"- 기간: {test_request['start_date']} ~ {test_request['end_date']}")
    print("- 매수 조건: RSI < 30")
    print("- 매도 조건: RSI > 70 또는 종가 < 20일 이동평균")
    print("\n백테스트 실행 중...")

    try:
        response = requests.post(
            f"{NAS_URL}/api/backtest/run",
            json=test_request,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            if 'results' in result:
                metrics = result['results']
                print("\n✅ 백테스트 성공!")
                print("\n=== 백테스트 결과 ===")
                print(f"총 수익률: {metrics.get('total_return', 0):.2f}%")
                print(f"승률: {metrics.get('win_rate', 0):.2f}%")
                print(f"최대 손실: {metrics.get('max_drawdown', 0):.2f}%")
                print(f"샤프 비율: {metrics.get('sharpe_ratio', 0):.2f}")
                print(f"총 거래 수: {metrics.get('total_trades', 0)}회")
                print(f"매수 횟수: {metrics.get('buy_count', 0)}회")
                print(f"매도 횟수: {metrics.get('sell_count', 0)}회")
                print(f"수익 거래: {metrics.get('winning_trades', 0)}회")
                print(f"손실 거래: {metrics.get('losing_trades', 0)}회")

                # 거래가 발생했는지 확인
                if metrics.get('total_trades', 0) > 0:
                    print("\n✅ 전략 신호가 정상적으로 생성되고 있습니다!")

                    # 최근 거래 내역 표시
                    if 'trades' in metrics and metrics['trades']:
                        print("\n최근 거래 내역:")
                        for i, trade in enumerate(metrics['trades'][:5], 1):
                            print(f"  {i}. {trade.get('date', 'N/A')} - "
                                  f"{trade.get('type', 'N/A')} "
                                  f"{trade.get('code', 'N/A')} "
                                  f"{trade.get('shares', 0)}주 @ "
                                  f"{trade.get('price', 0):,.0f}원")
                else:
                    print("\n⚠️ 거래가 발생하지 않았습니다.")
                    print("가능한 원인:")
                    print("1. 전략 조건이 너무 엄격함")
                    print("2. 데이터가 충분하지 않음")
                    print("3. 신호 생성 로직 확인 필요")

            else:
                print("❌ 백테스트 결과 형식 오류")
                print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")

        else:
            print(f"❌ 백테스트 실패: {response.status_code}")
            print(f"오류: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ 백테스트 시간 초과 (30초)")
    except Exception as e:
        print(f"❌ 백테스트 오류: {e}")

def test_simple_strategy():
    """간단한 전략으로 테스트 (조건 완화)"""
    print("\n" + "="*60)
    print("3. 간단한 전략 테스트 (조건 완화)")
    print("="*60)

    # 더 느슨한 조건으로 테스트
    simple_request = {
        "strategy_id": "simple-test",
        "stock_codes": ["005930"],  # 삼성전자만
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 10000000,
        "commission": 0.00015,
        "slippage": 0.001,
        "parameters": {
            "indicators": [
                {"type": "RSI", "params": {"period": 14}}
            ],
            "buyConditions": [
                {
                    "indicator": "rsi",
                    "operator": "<",
                    "value": 40  # 더 느슨한 조건
                }
            ],
            "sellConditions": [
                {
                    "indicator": "rsi",
                    "operator": ">",
                    "value": 60  # 더 느슨한 조건
                }
            ]
        }
    }

    print("간단한 전략:")
    print("- 매수: RSI < 40")
    print("- 매도: RSI > 60")
    print("\n실행 중...")

    try:
        response = requests.post(
            f"{NAS_URL}/api/backtest/run",
            json=simple_request,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            if 'results' in result:
                metrics = result['results']
                print(f"\n거래 발생: {metrics.get('total_trades', 0)}회")
                print(f"매수: {metrics.get('buy_count', 0)}회")
                print(f"매도: {metrics.get('sell_count', 0)}회")

                if metrics.get('total_trades', 0) > 0:
                    print("✅ 신호 생성 확인!")
                else:
                    print("⚠️ 여전히 거래 없음 - 디버깅 필요")

    except Exception as e:
        print(f"오류: {e}")

def main():
    print("\n" + "="*60)
    print("NAS 백테스트 시스템 통합 테스트")
    print("="*60)
    print(f"서버 URL: {NAS_URL}")
    print("="*60)

    # 1. 서버 상태 확인
    if not test_health_check():
        print("\n서버가 응답하지 않습니다. NAS 설정을 확인해주세요:")
        print("1. Docker 컨테이너가 실행 중인지 확인")
        print("2. 포트가 올바른지 확인")
        print("3. 방화벽 설정 확인")
        return

    # 2. 전략 백테스트 테스트
    test_backtest_with_strategy()

    # 3. 간단한 전략 테스트
    test_simple_strategy()

    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)

if __name__ == "__main__":
    # NAS IP 주소 입력 안내
    print("\n현재 설정된 NAS URL:", NAS_URL)
    user_input = input("이 주소가 맞습니까? (Y/n): ")

    if user_input.lower() == 'n':
        new_ip = input("NAS IP 주소를 입력하세요 (예: 192.168.1.100): ")
        new_port = input("포트 번호를 입력하세요 (기본: 8000): ") or "8000"
        NAS_URL = f"http://{new_ip}:{new_port}"
        print(f"새 URL 설정: {NAS_URL}")

    main()