"""
NAS 서버를 통해 데이터를 다운로드하고 Supabase에 저장 테스트
"""

import requests
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

def test_data_pipeline():
    """NAS → Supabase 데이터 파이프라인 테스트"""

    # 설정
    nas_url = "http://192.168.50.150:8080"
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    print("=" * 60)
    print("데이터 파이프라인 테스트")
    print("=" * 60)

    # 1. NAS에서 현재가 조회
    print("\n1. NAS에서 현재가 조회")
    stock_code = '005930'  # 삼성전자

    response = requests.post(
        f"{nas_url}/api/market/current-price",
        json={"stock_code": stock_code}
    )

    if response.status_code == 200:
        data = response.json()
        output = data['data']['output']

        price_data = {
            'stock_code': stock_code,
            'current_price': int(output['stck_prpr']),
            'change_price': int(output.get('prdy_vrss', 0)),  # 전일대비
            'change_rate': float(output['prdy_ctrt']),
            'volume': int(output['acml_vol']),
            'trading_value': int(output.get('acml_tr_pbmn', 0)),  # 거래대금
            'high_52w': int(output.get('stck_mxpr', 0)),  # 52주 최고가
            'low_52w': int(output.get('stck_llam', 0)),  # 52주 최저가
            'market_cap': 0,  # 시가총액 (별도 계산 필요)
            'shares_outstanding': 0,  # 발행주식수 (별도 조회 필요)
            'foreign_ratio': 0.0,  # 외국인 비율 (별도 조회 필요)
            'updated_at': datetime.now().isoformat()
        }

        print(f"✅ 현재가: {price_data['current_price']:,}원")
        print(f"   등락률: {price_data['change_rate']}%")

        # 2. Supabase에 저장
        print("\n2. Supabase에 저장")
        try:
            supabase = create_client(supabase_url, supabase_key)
            result = supabase.table('kw_price_current').upsert(price_data).execute()
            print("✅ 저장 성공")

            # 3. 저장된 데이터 확인
            print("\n3. 저장된 데이터 확인")
            saved_data = supabase.table('kw_price_current').select("*").eq('stock_code', stock_code).execute()
            if saved_data.data:
                print(f"✅ 확인: {saved_data.data[0]['current_price']:,}원")
            else:
                print("❌ 데이터 조회 실패")

        except Exception as e:
            print(f"❌ Supabase 오류: {e}")

    else:
        print(f"❌ NAS API 오류: {response.status_code}")

    # 4. 백테스트 테스트
    print("\n4. 백테스트 실행 테스트")
    backtest_request = {
        "strategy_id": "test-strategy",
        "stock_codes": [stock_code],
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "initial_capital": 10000000,
        "parameters": {
            "indicators": [
                {"type": "RSI", "params": {"period": 14}}
            ],
            "buyConditions": [
                {
                    "indicator": "rsi",
                    "operator": "<",
                    "value": 30
                }
            ],
            "sellConditions": [
                {
                    "indicator": "rsi",
                    "operator": ">",
                    "value": 70
                }
            ]
        }
    }

    response = requests.post(
        f"{nas_url}/api/backtest/run",
        json=backtest_request
    )

    if response.status_code == 200:
        result = response.json()

        if result.get('success'):
            print(f"✅ 백테스트 성공!")

            # 요약 결과
            if 'summary' in result:
                summary = result['summary']
                print(f"\n   [요약 결과]")
                print(f"   총 수익률: {summary.get('total_return', 0):.2f}%")
                print(f"   승률: {summary.get('average_win_rate', 0):.2f}%")
                print(f"   샤프 비율: {summary.get('average_sharpe_ratio', 0):.2f}")
                print(f"   최대 낙폭: {summary.get('max_drawdown', 0):.2f}%")

            # 개별 종목 결과
            if 'individual_results' in result:
                print(f"\n   [개별 종목 결과]")
                for stock_result in result['individual_results']:
                    code = stock_result['stock_code']
                    res = stock_result['result']
                    print(f"   {code}: 수익률 {res['total_return']:.2f}%, 거래 {res.get('total_trades', 0)}회")
        else:
            print(f"❌ 백테스트 실패")
            print(f"   응답: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"❌ 백테스트 오류: {response.status_code}")
        print(f"   응답: {response.text[:200]}")

    print("\n" + "=" * 60)
    print("✅ 전체 파이프라인 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_data_pipeline()