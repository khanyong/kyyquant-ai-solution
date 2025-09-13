"""
완전한 주식 데이터 다운로드 및 저장
현재가 + 기본정보를 모두 수집하여 Supabase에 저장
"""

import requests
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def download_complete_data():
    """완전한 주식 데이터 다운로드"""

    # Configuration
    nas_url = "http://192.168.50.150:8080"
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("완전한 주식 데이터 다운로드")
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
            # 1. 현재가 데이터 가져오기
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
                        # 2. 추가 정보 조회 (주식기본정보 - opt10001)
                        basic_info = get_stock_basic_info(nas_url, stock_code)

                        # 3. 외국인 지분율 조회 (별도 TR 필요)
                        foreign_info = get_foreign_holding_ratio(nas_url, stock_code)

                        # Supabase에 저장할 데이터 (완전한 데이터)
                        price_data = {
                            'stock_code': stock_code,
                            'current_price': current_price,
                            'change_price': int(output.get('prdy_vrss', 0)),
                            'change_rate': float(output.get('prdy_ctrt', 0)),
                            'volume': int(output.get('acml_vol', 0)),
                            'trading_value': int(output.get('acml_tr_pbmn', 0)) * 1000000,  # 백만원 -> 원
                            'high_52w': int(output.get('stck_mxpr', 0)),
                            'low_52w': int(output.get('stck_llam', 0)),
                            'market_cap': basic_info.get('market_cap', 0),
                            'shares_outstanding': basic_info.get('shares_outstanding', 0),
                            'foreign_ratio': foreign_info.get('foreign_ratio', 0.0),
                            'updated_at': datetime.now().isoformat()
                        }

                        # Supabase에 저장
                        result = supabase.table('kw_price_current').upsert(price_data).execute()

                        print(f"  OK 저장 완료:")
                        print(f"     현재가: {current_price:,}원")
                        print(f"     등락률: {price_data['change_rate']}%")
                        print(f"     거래량: {price_data['volume']:,}주")
                        if price_data['market_cap'] > 0:
                            print(f"     시가총액: {price_data['market_cap']/1000000000000:.1f}조원")
                        if price_data['shares_outstanding'] > 0:
                            print(f"     발행주식수: {price_data['shares_outstanding']:,}주")
                        if price_data['foreign_ratio'] > 0:
                            print(f"     외국인지분율: {price_data['foreign_ratio']:.2f}%")

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
    verify_saved_data(supabase)

def get_stock_basic_info(nas_url, stock_code):
    """주식 기본정보 조회 (opt10001)"""
    try:
        # NAS 서버에 주식기본정보 API 엔드포인트가 있다고 가정
        # 실제로는 이 엔드포인트를 NAS 서버에 구현해야 함
        response = requests.post(
            f"{nas_url}/api/stock/basic-info",
            json={"stock_code": stock_code, "tr_code": "opt10001"},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                output = data.get('data', {})
                return {
                    'market_cap': int(output.get('시가총액', 0)) * 100000000,  # 억원 -> 원
                    'shares_outstanding': int(output.get('유통주식수', 0)) * 1000  # 천주 -> 주
                }
    except:
        pass

    # 기본값 반환
    return {'market_cap': 0, 'shares_outstanding': 0}

def get_foreign_holding_ratio(nas_url, stock_code):
    """외국인 보유 비율 조회"""
    try:
        # NAS 서버에 외국인 보유 정보 API 엔드포인트가 있다고 가정
        response = requests.post(
            f"{nas_url}/api/stock/foreign-holding",
            json={"stock_code": stock_code},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return {
                    'foreign_ratio': float(data.get('data', {}).get('foreign_ratio', 0))
                }
    except:
        pass

    # 기본값 반환
    return {'foreign_ratio': 0.0}

def verify_saved_data(supabase):
    """저장된 데이터 검증"""
    print("\n저장된 데이터 검증 중...")
    result = supabase.table('kw_price_current').select("*").execute()

    if result.data:
        total = len(result.data)
        complete = 0
        partial = 0

        for item in result.data:
            if (item.get('market_cap', 0) > 0 and
                item.get('shares_outstanding', 0) > 0 and
                item.get('foreign_ratio', 0) > 0):
                complete += 1
            elif item.get('current_price', 0) > 0:
                partial += 1

        print(f"총 {total}개 종목 저장됨")
        print(f"  - 완전한 데이터: {complete}개")
        print(f"  - 부분 데이터: {partial}개")
        print(f"  - 데이터 없음: {total - complete - partial}개")

        if complete > 0:
            print("\n완전한 데이터 샘플 (최대 3개):")
            sample_count = 0
            for item in result.data:
                if (item.get('market_cap', 0) > 0 and
                    item.get('shares_outstanding', 0) > 0):
                    print(f"  {item['stock_code']}: 시총 {item['market_cap']/1000000000000:.1f}조원, "
                          f"외국인 {item.get('foreign_ratio', 0):.2f}%")
                    sample_count += 1
                    if sample_count >= 3:
                        break

if __name__ == "__main__":
    download_complete_data()