#!/usr/bin/env python3
"""
전략에 포함된 종목들만 일봉 데이터 다운로드
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import time

sys.path.append(os.path.dirname(__file__))
from api.kiwoom_client import get_kiwoom_client

load_dotenv()

def main():
    # Supabase 초기화
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)

    # Kiwoom API 초기화
    kiwoom = get_kiwoom_client()

    print("=" * 80)
    print("전략 종목 일봉 데이터 업데이트")
    print("=" * 80)

    # 활성화된 전략의 모든 종목 가져오기
    print("\n1. 활성 전략의 종목 조회 중...")
    result = supabase.rpc('get_active_strategies_with_universe').execute()

    if not result.data:
        print("활성화된 전략이 없습니다.")
        return

    # 모든 종목 코드 수집 (중복 제거)
    all_stocks = set()
    for strategy in result.data:
        filtered_stocks = strategy.get('filtered_stocks', [])
        for stock in filtered_stocks:
            if 'stock_code' in stock:
                all_stocks.add(stock['stock_code'])

    stock_list = sorted(list(all_stocks))
    print(f"   총 {len(stock_list)}개 종목 발견")

    # 각 종목의 일봉 데이터 다운로드
    print("\n2. 일봉 데이터 다운로드 중...")
    success_count = 0
    fail_count = 0

    for i, stock_code in enumerate(stock_list, 1):
        try:
            print(f"[{i}/{len(stock_list)}] {stock_code}", end=" ... ", flush=True)

            # 60일치 데이터 조회
            daily_data = kiwoom.get_daily_price(stock_code, days=60)

            if daily_data and len(daily_data) > 0:
                # Supabase에 저장 (upsert)
                supabase.table('kw_price_daily').upsert(
                    daily_data,
                    on_conflict='stock_code,trade_date'
                ).execute()

                print(f"OK: {len(daily_data)} records")
                success_count += 1
            else:
                print("SKIP: No data")
                fail_count += 1

        except Exception as e:
            print(f"ERROR: {e}")
            fail_count += 1

            # 429 에러면 잠시 대기
            if "429" in str(e):
                print("   ⏸️  Rate limit - 대기 중 (30초)...")
                import time
                time.sleep(30)

    # 결과 요약
    print("\n" + "=" * 80)
    print("완료!")
    print(f"  성공: {success_count}개")
    print(f"  실패: {fail_count}개")
    print("=" * 80)

if __name__ == '__main__':
    main()
