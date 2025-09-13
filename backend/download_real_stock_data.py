"""
실제 주식 데이터 다운로드 및 저장
여러 종목의 실제 가격 데이터를 키움 API에서 가져와 Supabase에 저장
"""

import requests
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def download_real_data():
    """실제 주식 데이터 다운로드"""

    # Configuration
    nas_url = "http://192.168.50.150:8080"
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("실제 주식 데이터 다운로드")
    print("=" * 60)

    # 주요 종목 리스트 (KOSPI 상위 종목들)
    stocks = {
        '005930': '삼성전자',
        '000660': 'SK하이닉스',
        '207940': '삼성바이오로직스',
        '005380': '현대차',
        '005935': '삼성전자우',
        '000270': '기아',
        '068270': '셀트리온',
        '035420': 'NAVER',
        '051910': 'LG화학',
        '006400': '삼성SDI',
        '003670': '포스코퓨처엠',
        '035720': '카카오',
        '012330': '현대모비스',
        '028260': '삼성물산',
        '066570': 'LG전자',
        '036570': 'NCsoft',
        '033780': 'KT&G',
        '003550': 'LG',
        '017670': 'SK텔레콤',
        '105560': 'KB금융'
    }

    success_count = 0
    fail_count = 0

    for stock_code, stock_name in stocks.items():
        print(f"\n[{stock_code}] {stock_name} 처리 중...")

        try:
            # 1. NAS 서버에서 현재가 데이터 가져오기
            response = requests.post(
                f"{nas_url}/api/market/current-price",
                json={"stock_code": stock_code},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('success') and data.get('data'):
                    output = data['data'].get('output', {})

                    # 실제 가격 확인
                    current_price = int(output.get('stck_prpr', 0))

                    if current_price > 0:
                        # Supabase에 저장할 데이터 (kw_price_current 테이블 스키마에 맞게)
                        price_data = {
                            'stock_code': stock_code,
                            'current_price': current_price,
                            'change_price': int(output.get('prdy_vrss', 0)),
                            'change_rate': float(output.get('prdy_ctrt', 0)),
                            'volume': int(output.get('acml_vol', 0)),
                            'trading_value': int(output.get('acml_tr_pbmn', 0)),
                            'high_52w': int(output.get('stck_mxpr', 0)),
                            'low_52w': int(output.get('stck_llam', 0)),
                            'market_cap': 0,  # 나중에 계산
                            'shares_outstanding': 0,
                            'foreign_ratio': 0.0,
                            'updated_at': datetime.now().isoformat()
                        }

                        # Supabase에 저장
                        result = supabase.table('kw_price_current').upsert(price_data).execute()

                        print(f"  OK 저장 완료:")
                        print(f"     현재가: {current_price:,}원")
                        print(f"     등락률: {price_data['change_rate']}%")
                        print(f"     거래량: {price_data['volume']:,}주")

                        success_count += 1
                    else:
                        print(f"  WARNING: 가격 데이터 없음")
                        fail_count += 1
                else:
                    print(f"  ERROR: API 응답 오류")
                    fail_count += 1
            else:
                print(f"  ERROR: HTTP 오류: {response.status_code}")
                fail_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            fail_count += 1

        # API 호출 제한 대응 (0.5초 대기)
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"다운로드 완료!")
    print(f"  성공: {success_count}개 종목")
    print(f"  실패: {fail_count}개 종목")
    print("=" * 60)

    # 저장된 데이터 검증
    print("\n저장된 데이터 검증 중...")
    result = supabase.table('kw_price_current').select("stock_code, current_price").execute()

    if result.data:
        prices = {item['stock_code']: item['current_price'] for item in result.data}
        unique_prices = set(prices.values())

        print(f"총 {len(prices)}개 종목 저장됨")
        print(f"고유 가격 수: {len(unique_prices)}개")

        if len(unique_prices) == 1:
            print("⚠️ 경고: 모든 종목이 동일한 가격입니다! Mock 데이터일 가능성 있음")
        else:
            print("✅ 다양한 가격이 저장되었습니다. 실제 데이터로 보입니다.")
            # 샘플 출력
            print("\n샘플 데이터 (5개):")
            for i, (code, price) in enumerate(list(prices.items())[:5]):
                print(f"  {code}: {price:,}원")

if __name__ == "__main__":
    download_real_data()