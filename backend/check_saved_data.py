"""
저장된 주식 데이터 확인
"""

from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def check_saved_data():
    """저장된 데이터 확인"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("kw_price_current 테이블 데이터 확인")
    print("=" * 60)

    try:
        # 최근 저장된 데이터 10개 조회
        result = supabase.table('kw_price_current').select('*').order('updated_at', desc=True).limit(10).execute()

        if result.data:
            print(f"\n최근 저장된 {len(result.data)}개 종목:")
            print("-" * 60)

            for i, item in enumerate(result.data, 1):
                print(f"\n{i}. 종목코드: {item['stock_code']}")
                print(f"   현재가: {item['current_price']:,}원")
                print(f"   등락: {item['change_price']:+,}원 ({item['change_rate']:+.2f}%)")
                print(f"   거래량: {item['volume']:,}주")
                print(f"   52주 최고: {item['high_52w']:,}원")
                print(f"   52주 최저: {item['low_52w']:,}원")
                print(f"   업데이트: {item['updated_at']}")

        # 전체 통계
        all_result = supabase.table('kw_price_current').select('stock_code', count='exact').execute()
        total_count = len(all_result.data) if all_result.data else 0

        print("\n" + "=" * 60)
        print(f"전체 저장된 종목 수: {total_count}개")

        # 오늘 업데이트된 종목 수
        today = datetime.now().strftime('%Y-%m-%d')
        today_result = supabase.table('kw_price_current').select('stock_code').gte('updated_at', today).execute()
        today_count = len(today_result.data) if today_result.data else 0

        print(f"오늘 업데이트된 종목: {today_count}개")
        print("=" * 60)

    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    check_saved_data()