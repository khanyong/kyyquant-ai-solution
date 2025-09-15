import json
import requests
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase 연결
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

print("\n[템플릿] 스윙 트레이딩 전략 분석")
print("="*80)

# 스윙 트레이딩 전략 찾기
response = supabase.table('strategies').select("*").eq('name', '[템플릿] 스윙 트레이딩').execute()

if not response.data:
    print("스윙 트레이딩 전략을 찾을 수 없습니다.")
    exit(1)

strategy = response.data[0]
print(f"전략 ID: {strategy['id']}")
print(f"전략 이름: {strategy['name']}")
print(f"\n전략 설정:")

config = strategy.get('config', {})
print(json.dumps(config, indent=2, ensure_ascii=False))

# 지표 확인
print("\n지표 목록:")
indicators = config.get('indicators', [])
for ind in indicators:
    print(f"  - {ind.get('name')}: {ind.get('type')} (params: {ind.get('params')})")

# 매수 조건 확인
print("\n매수 조건:")
buy_conditions = config.get('buyConditions', [])
for i, cond in enumerate(buy_conditions, 1):
    print(f"  {i}. {cond.get('left')} {cond.get('operator')} {cond.get('right')}")

# 매도 조건 확인
print("\n매도 조건:")
sell_conditions = config.get('sellConditions', [])
for i, cond in enumerate(sell_conditions, 1):
    print(f"  {i}. {cond.get('left')} {cond.get('operator')} {cond.get('right')}")

# 백테스트 실행
print("\n백테스트 테스트 실행...")
print("-"*80)

# API 서버 URL (로컬 또는 NAS)
api_url = "http://localhost:8001"  # 로컬 테스트
# api_url = "http://192.168.50.150:8080"  # NAS

backtest_payload = {
    "strategy_id": strategy['id'],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "initial_capital": 10000000,
    "commission": 0.00015,
    "slippage": 0.001,
    "data_interval": "1d",
    "stock_codes": ["005930", "000660"],  # 삼성전자, SK하이닉스
    "use_cached_data": True
}

try:
    print(f"API 엔드포인트: {api_url}/api/backtest/run")
    print(f"테스트 종목: {backtest_payload['stock_codes']}")

    response = requests.post(
        f"{api_url}/api/backtest/run",
        json=backtest_payload,
        timeout=30
    )

    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print("\n백테스트 성공!")
            summary = result.get('summary', {})
            print(f"총 거래 횟수: {summary.get('total_trades', 0)}")
            print(f"승률: {summary.get('average_win_rate', 0):.2f}%")
            print(f"총 수익률: {summary.get('total_return', 0):.2f}%")

            # 개별 종목 결과 확인
            individual = result.get('individual_results', [])
            print(f"\n개별 종목 결과:")
            for stock in individual:
                print(f"  - {stock.get('stock_code')}: {stock.get('result', {}).get('total_trades', 0)} 거래")

                # 거래가 없는 경우 상세 분석
                if stock.get('result', {}).get('total_trades', 0) == 0:
                    print(f"    → 거래 없음 - 조건 미충족 가능성")

                    # 지표 값 확인
                    if 'debug_info' in stock.get('result', {}):
                        debug = stock['result']['debug_info']
                        print(f"    → 디버그 정보: {debug}")
        else:
            print(f"\n백테스트 실패: {result.get('error')}")
    else:
        print(f"\nAPI 오류: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"\n오류 발생: {e}")

print("\n분석 완료")
print("="*80)