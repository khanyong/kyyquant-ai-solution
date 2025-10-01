"""
indicators 테이블 구조 확인
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def check_table_structure():
    """테이블 구조 확인"""

    # Supabase 연결
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_KEY must be set")
        return

    supabase = create_client(url, key)

    # 테이블 데이터 확인
    try:
        response = supabase.table('indicators').select('*').limit(1).execute()
        if response.data:
            print("Indicators table columns:")
            for key in response.data[0].keys():
                print(f"  - {key}")
        else:
            print("No data in indicators table")

            # 빈 테이블이면 구조 확인을 위해 빈 레코드 삽입 시도
            test_data = {
                'name': 'test_indicator',
                'calculation_type': 'custom_formula',
                'formula': '{}',
                'is_active': False
            }
            try:
                result = supabase.table('indicators').insert(test_data).execute()
                print("Successfully inserted test record")
                # 삭제
                supabase.table('indicators').delete().eq('name', 'test_indicator').execute()
            except Exception as e:
                print(f"Error inserting test record: {e}")

    except Exception as e:
        print(f"Error accessing indicators table: {e}")

if __name__ == "__main__":
    check_table_structure()