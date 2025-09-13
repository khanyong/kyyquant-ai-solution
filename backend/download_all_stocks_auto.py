"""
전체 종목 자동 다운로드 스크립트
종목 리스트를 하드코딩하지 않고 자동으로 가져와서 다운로드
"""

import requests
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def download_all_stocks_auto():
    """전체 종목 자동 다운로드"""

    # Configuration
    nas_url = "http://192.168.50.150:8080"
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("전체 종목 자동 다운로드")
    print("=" * 60)

    # 방법 1: NAS 서버에서 전체 종목 리스트 가져오기
    stocks = get_stock_list_from_nas(nas_url)

    # 방법 2: 데이터베이스에서 종목 리스트 가져오기 (NAS 실패시)
    if not stocks:
        stocks = get_stock_list_from_database(supabase)

    if not stocks:
        print("ERROR: 종목 리스트를 가져올 수 없습니다.")
        return

    print(f"\n총 {len(stocks)}개 종목 발견")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    # 진행 상황 파일 (중간에 중단되어도 이어서 진행 가능)
    progress_file = "download_progress.json"
    processed = load_progress(progress_file)

    for stock_code, stock_name in stocks.items():
        # 이미 처리한 종목은 건너뛰기
        if stock_code in processed:
            continue

        print(f"\n[{stock_code}] {stock_name} 처리 중...")

        try:
            # 현재가 데이터 가져오기
            response = requests.post(
                f"{nas_url}/api/market/current-price",
                json={"stock_code": stock_code},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('success') and data.get('data'):
                    output = data['data'].get('output', {})
                    current_price = int(output.get('stck_prpr', 0))

                    if current_price > 0:
                        # Supabase에 저장할 데이터
                        price_data = {
                            'stock_code': stock_code,
                            'current_price': current_price,
                            'change_price': int(output.get('prdy_vrss', 0)),
                            'change_rate': float(output.get('prdy_ctrt', 0)),
                            'volume': int(output.get('acml_vol', 0)),
                            'trading_value': int(output.get('acml_tr_pbmn', 0)) * 1000000,
                            'high_52w': int(output.get('stck_mxpr', 0)),
                            'low_52w': int(output.get('stck_llam', 0)),
                            'market_cap': 0,  # 추후 업데이트
                            'shares_outstanding': 0,
                            'foreign_ratio': 0.0,
                            'updated_at': datetime.now().isoformat()
                        }

                        # Supabase에 저장
                        result = supabase.table('kw_price_current').upsert(price_data).execute()

                        print(f"  OK: {current_price:,}원 (등락률: {price_data['change_rate']}%)")
                        success_count += 1

                        # 진행 상황 저장
                        processed.add(stock_code)
                        save_progress(progress_file, processed)
                    else:
                        print(f"  SKIP: 가격 데이터 없음")
                        fail_count += 1
                else:
                    print(f"  ERROR: API 응답 오류")
                    fail_count += 1
            else:
                print(f"  ERROR: HTTP {response.status_code}")
                fail_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            fail_count += 1

        # API 호출 제한 대응 (0.2초 대기)
        time.sleep(0.2)

        # 10개마다 진행 상황 출력
        if (success_count + fail_count) % 10 == 0:
            print(f"\n진행 상황: 성공 {success_count}, 실패 {fail_count}")

    print("\n" + "=" * 60)
    print(f"다운로드 완료!")
    print(f"  성공: {success_count}개 종목")
    print(f"  실패: {fail_count}개 종목")
    print(f"  전체: {len(stocks)}개 종목")
    print("=" * 60)

def get_stock_list_from_nas(nas_url):
    """NAS 서버에서 전체 종목 리스트 가져오기"""
    try:
        print("\nNAS 서버에서 종목 리스트 조회 중...")

        # NAS 서버의 종목 리스트 API 호출
        # 현재 이 엔드포인트는 NAS 서버에 구현이 필요합니다
        response = requests.get(
            f"{nas_url}/api/market/stock-list",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stocks = {}
                for item in data.get('data', []):
                    stocks[item['code']] = item['name']
                print(f"  NAS: {len(stocks)}개 종목 발견")
                return stocks
        else:
            print(f"  NAS API 응답: {response.status_code}")
            print("  /api/market/stock-list 엔드포인트가 NAS 서버에 구현되어야 합니다")
    except requests.exceptions.RequestException as e:
        print(f"  NAS 서버 연결 실패: {e}")
        print("  대신 데이터베이스에서 종목 리스트를 가져옵니다...")

    return None

def get_stock_list_from_database(supabase):
    """데이터베이스에서 종목 리스트 가져오기"""
    try:
        print("\n데이터베이스에서 종목 리스트 조회 중...")

        # stock_metadata 테이블에서 종목 정보 가져오기
        result = supabase.table('stock_metadata')\
            .select('stock_code, stock_name')\
            .execute()

        if result.data:
            stocks = {}
            for item in result.data:
                stocks[item['stock_code']] = item['stock_name']
            print(f"  DB: {len(stocks)}개 종목 발견")
            return stocks
        else:
            print("  DB: 종목 데이터 없음")

    except Exception as e:
        print(f"  DB 조회 실패: {e}")

    return None

def load_progress(filename):
    """진행 상황 불러오기"""
    try:
        with open(filename, 'r') as f:
            return set(json.load(f))
    except:
        return set()

def save_progress(filename, processed):
    """진행 상황 저장"""
    try:
        with open(filename, 'w') as f:
            json.dump(list(processed), f)
    except:
        pass

if __name__ == "__main__":
    download_all_stocks_auto()