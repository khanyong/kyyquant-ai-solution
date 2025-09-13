"""
user_api_keys와 user_api_keys_view 테이블 구조 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def check_api_keys_tables():
    """두 API 키 테이블 구조 확인"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("API 키 테이블 구조 확인")
    print("=" * 60)

    # 1. user_api_keys 테이블
    print("\n1. user_api_keys 테이블:")
    try:
        result = supabase.table('user_api_keys').select("*").limit(3).execute()

        if result.data:
            print(f"   데이터 개수: {len(result.data)}")
            print("   컬럼 구조:")
            for key in result.data[0].keys():
                print(f"   - {key}")

            print("\n   샘플 데이터:")
            for i, row in enumerate(result.data[:2]):
                print(f"   [{i+1}] 사용자ID: {row.get('user_id', 'N/A')}")
                print(f"       제공자: {row.get('provider', 'N/A')}")
                print(f"       생성일: {row.get('created_at', 'N/A')}")
                print(f"       키 존재: {'Yes' if row.get('api_key') else 'No'}")
        else:
            print("   데이터 없음")

    except Exception as e:
        print(f"   오류: {e}")

    # 2. user_api_keys_view 테이블
    print("\n2. user_api_keys_view 테이블:")
    try:
        result = supabase.table('user_api_keys_view').select("*").limit(3).execute()

        if result.data:
            print(f"   데이터 개수: {len(result.data)}")
            print("   컬럼 구조:")
            for key in result.data[0].keys():
                print(f"   - {key}")

            print("\n   샘플 데이터:")
            for i, row in enumerate(result.data[:2]):
                print(f"   [{i+1}] 사용자ID: {row.get('user_id', 'N/A')}")
                print(f"       제공자: {row.get('provider', 'N/A')}")
                print(f"       생성일: {row.get('created_at', 'N/A')}")
                print(f"       키 존재: {'Yes' if row.get('api_key') else 'No'}")
        else:
            print("   데이터 없음")

    except Exception as e:
        print(f"   오류: {e}")

    # 3. 키움 제공자 전용 조회
    print("\n3. 키움(kiwoom) 제공자 데이터:")
    for table_name in ['user_api_keys', 'user_api_keys_view']:
        try:
            result = supabase.table(table_name).select("*").eq('provider', 'kiwoom').execute()
            print(f"   {table_name}: {len(result.data)}개")

            for row in result.data:
                print(f"     사용자: {row.get('user_id', 'N/A')}")
                print(f"     키 존재: {'Yes' if row.get('api_key') else 'No'}")
                print(f"     시크릿 존재: {'Yes' if row.get('api_secret') else 'No'}")
        except Exception as e:
            print(f"   {table_name} 오류: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_api_keys_tables()