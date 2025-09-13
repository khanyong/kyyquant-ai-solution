"""
kw_price_daily 테이블 데이터 현황 확인
"""

import os
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def check_data_status():
    """데이터 현황 확인"""

    # Supabase 클라이언트
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("kw_price_daily 테이블 현황")
    print("=" * 60)

    try:
        # 전체 레코드 수
        result = supabase.table('kw_price_daily').select('stock_code', count='exact').execute()
        total_records = result.count if hasattr(result, 'count') else 0
        print(f"\n전체 레코드 수: {total_records:,}개")

        # 종목별 데이터 확인 (상위 10개)
        result = supabase.table('kw_price_daily').select('stock_code').execute()

        if result.data:
            # 종목별 집계
            stock_counts = {}
            for row in result.data:
                code = row['stock_code']
                stock_counts[code] = stock_counts.get(code, 0) + 1

            # 정렬하여 상위 10개 표시
            sorted_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)

            print(f"\n종목 수: {len(stock_counts)}개")
            print("\n상위 10개 종목 (레코드 수):")
            print("-" * 30)
            for code, count in sorted_stocks[:10]:
                print(f"  {code}: {count}개")

            # 날짜 범위 확인
            first_date_result = supabase.table('kw_price_daily').select('trade_date').order('trade_date').limit(1).execute()
            last_date_result = supabase.table('kw_price_daily').select('trade_date').order('trade_date', desc=True).limit(1).execute()

            if first_date_result.data and last_date_result.data:
                first_date = first_date_result.data[0]['trade_date']
                last_date = last_date_result.data[0]['trade_date']
                print(f"\n데이터 기간: {first_date} ~ {last_date}")

            # 특정 날짜 종목 수 확인
            check_dates = ['2024-09-14', '2025-01-01', '2025-09-12']
            print("\n날짜별 종목 수:")
            print("-" * 30)
            for date in check_dates:
                result = supabase.table('kw_price_daily').select('stock_code', count='exact').eq('trade_date', date).execute()
                count = result.count if hasattr(result, 'count') else 0
                print(f"  {date}: {count}개 종목")

    except Exception as e:
        print(f"\n오류 발생: {e}")

if __name__ == "__main__":
    check_data_status()