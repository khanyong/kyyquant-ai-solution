"""
전체 주식 데이터 다운로드 및 저장
NAS API에서 종목 리스트를 가져와 모든 종목의 현재가를 Supabase에 저장
"""

import requests
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
import time

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def download_all_stocks_data(test_mode=False, limit=None):
    """전체 주식 데이터 다운로드

    Args:
        test_mode: True면 처음 10개만 테스트
        limit: 다운로드할 최대 종목 수
    """

    # Configuration
    nas_url = "http://192.168.50.150:8080"
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("전체 주식 데이터 다운로드")
    print("=" * 60)

    # 1. NAS API에서 종목 리스트 가져오기
    print("\n1. 종목 리스트 가져오기...")
    try:
        response = requests.get(f"{nas_url}/api/market/stock-list")
        if response.status_code != 200:
            print(f"   ERROR: 종목 리스트 조회 실패 (HTTP {response.status_code})")
            return

        stock_list = response.json().get('data', [])
        print(f"   성공! 총 {len(stock_list)}개 종목")

        # 시장별 분류
        kospi = [s for s in stock_list if s['market'] == 'KOSPI']
        kosdaq = [s for s in stock_list if s['market'] == 'KOSDAQ']
        konex = [s for s in stock_list if s['market'] == 'KONEX']

        print(f"   - KOSPI: {len(kospi)}개")
        print(f"   - KOSDAQ: {len(kosdaq)}개")
        print(f"   - KONEX: {len(konex)}개")

    except Exception as e:
        print(f"   ERROR: {e}")
        return

    # 2. 테스트 모드 또는 제한 적용
    if test_mode:
        stock_list = stock_list[:10]
        print(f"\n   [테스트 모드] 처음 10개만 처리")
    elif limit:
        stock_list = stock_list[:limit]
        print(f"\n   [제한 모드] {limit}개만 처리")

    # 3. 각 종목 데이터 다운로드 및 저장
    print(f"\n2. 종목 데이터 다운로드 시작...")
    print(f"   처리할 종목 수: {len(stock_list)}개")

    success_count = 0
    fail_count = 0
    skip_count = 0
    batch_size = 50  # 50개마다 진행상황 표시

    start_time = datetime.now()

    for i, stock in enumerate(stock_list):
        stock_code = stock['code']
        stock_name = stock['name']
        market = stock['market']

        try:
            # 현재가 데이터 가져오기
            response = requests.post(
                f"{nas_url}/api/market/current-price",
                json={"stock_code": stock_code},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                if data.get('success') and data.get('data'):
                    # NAS API 응답 형식 변경됨
                    price_info = data['data']

                    # 실제 가격 확인
                    current_price = int(price_info.get('current_price', 0))

                    if current_price > 0:
                        # Supabase에 저장할 데이터
                        price_data = {
                            'stock_code': stock_code,
                            'current_price': current_price,
                            'change_price': int(price_info.get('change_price', 0)),
                            'change_rate': float(price_info.get('change_rate', 0)),
                            'volume': int(price_info.get('volume', 0)),
                            'trading_value': 0,  # pykrx에서 제공하지 않음
                            'high_52w': 0,  # pykrx에서 제공하지 않음
                            'low_52w': 0,  # pykrx에서 제공하지 않음
                            'market_cap': 0,  # 나중에 계산
                            'shares_outstanding': 0,
                            'foreign_ratio': 0.0,
                            'updated_at': datetime.now().isoformat()
                        }

                        # Supabase에 저장 (upsert)
                        result = supabase.table('kw_price_current').upsert(price_data).execute()
                        success_count += 1

                        # 상세 로그 (테스트 모드에서만)
                        if test_mode:
                            print(f"  [{market}] {stock_code} - {stock_name}: {current_price:,}원 (저장 완료)")
                    else:
                        skip_count += 1
                        if test_mode:
                            print(f"  [{market}] {stock_code} - {stock_name}: 가격 정보 없음 (건너뜀)")
                else:
                    fail_count += 1
                    if test_mode:
                        print(f"  [{market}] {stock_code} - {stock_name}: 데이터 조회 실패")
            else:
                fail_count += 1
                if test_mode:
                    print(f"  [{market}] {stock_code} - {stock_name}: HTTP {response.status_code}")

        except Exception as e:
            fail_count += 1
            if test_mode:
                print(f"  [{market}] {stock_code} - {stock_name}: 오류 - {e}")

        # 진행상황 표시 (50개마다)
        if not test_mode and (i + 1) % batch_size == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = (len(stock_list) - i - 1) / rate if rate > 0 else 0

            print(f"   진행: {i+1}/{len(stock_list)} ({(i+1)*100//len(stock_list)}%) "
                  f"- 성공: {success_count}, 실패: {fail_count}, 건너뜀: {skip_count} "
                  f"- 예상 남은 시간: {int(remaining//60)}분 {int(remaining%60)}초")

        # API 제한 방지 (0.5초 대기)
        time.sleep(0.5)

    # 4. 최종 결과
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("다운로드 완료!")
    print(f"  처리 종목: {len(stock_list)}개")
    print(f"  성공: {success_count}개")
    print(f"  실패: {fail_count}개")
    print(f"  건너뜀: {skip_count}개")
    print(f"  소요 시간: {int(total_time//60)}분 {int(total_time%60)}초")
    print("=" * 60)

    # 5. 데이터베이스 확인
    try:
        result = supabase.table('kw_price_current').select('stock_code', count='exact').execute()
        total_in_db = len(result.data) if result.data else 0
        print(f"\n현재 kw_price_current 테이블의 총 종목 수: {total_in_db}개")
    except Exception as e:
        print(f"\n데이터베이스 확인 실패: {e}")

if __name__ == "__main__":
    import sys

    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            download_all_stocks_data(test_mode=True)
        elif sys.argv[1].isdigit():
            download_all_stocks_data(limit=int(sys.argv[1]))
        else:
            print("사용법:")
            print("  python download_all_stocks_data.py        # 전체 다운로드")
            print("  python download_all_stocks_data.py test   # 10개만 테스트")
            print("  python download_all_stocks_data.py 100    # 100개만 다운로드")
    else:
        # 전체 다운로드
        download_all_stocks_data()