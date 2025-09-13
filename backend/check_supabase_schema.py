"""
Supabase 테이블 스키마 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_table_schema():
    """Supabase 테이블 구조 확인"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_KEY')
    )

    print("=" * 60)
    print("Supabase 테이블 스키마 확인")
    print("=" * 60)

    # 1. kw_price_current 테이블 확인
    print("\n1. kw_price_current 테이블:")
    try:
        # 데이터 1개만 조회해서 컬럼 확인
        result = supabase.table('kw_price_current').select("*").limit(1).execute()
        if result.data:
            print("   컬럼 목록:")
            for key in result.data[0].keys():
                print(f"   - {key}")
        else:
            print("   데이터 없음 - 빈 테이블")

        # 테스트 데이터 삽입 시도
        test_data = {
            'stock_code': '005930',
            'current_price': 71900,
            'change_rate': -0.69,
            'volume': 1234567,
            'updated_at': '2024-01-15T12:00:00'
        }

        print("\n   테스트 데이터 삽입 시도...")
        result = supabase.table('kw_price_current').upsert(test_data).execute()
        print("   ✅ 삽입 성공")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 2. kw_price_daily 테이블 확인
    print("\n2. kw_price_daily 테이블:")
    try:
        result = supabase.table('kw_price_daily').select("*").limit(1).execute()
        if result.data:
            print("   컬럼 목록:")
            for key in result.data[0].keys():
                print(f"   - {key}")
        else:
            print("   데이터 없음 - 빈 테이블")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    # 3. kw_stock_master 테이블 확인
    print("\n3. kw_stock_master 테이블:")
    try:
        result = supabase.table('kw_stock_master').select("*").limit(1).execute()
        if result.data:
            print("   컬럼 목록:")
            for key in result.data[0].keys():
                print(f"   - {key}")
        else:
            print("   데이터 없음 - 빈 테이블")

    except Exception as e:
        print(f"   ❌ 오류: {e}")

    print("\n" + "=" * 60)
    print("해결 방법:")
    print("1. Supabase 대시보드에서 테이블 스키마 확인")
    print("2. 필요한 컬럼 추가 또는 데이터 형식 맞추기")
    print("=" * 60)

if __name__ == "__main__":
    check_table_schema()