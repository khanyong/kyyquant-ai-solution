"""
Supabase user_api_keys 테이블에서 키 정보 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def check_api_keys():
    """사용자 API 키 확인"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("User API Keys 테이블 확인")
    print("=" * 60)

    try:
        # user_api_keys 테이블 조회
        result = supabase.table('user_api_keys').select("*").execute()

        if result.data:
            print(f"총 {len(result.data)}개의 API 키 설정 발견")
            print("\n키 정보:")

            for key_info in result.data:
                print(f"- 사용자 ID: {key_info.get('user_id', 'N/A')}")
                print(f"  제공자: {key_info.get('provider', 'N/A')}")
                print(f"  생성일: {key_info.get('created_at', 'N/A')}")
                print(f"  키 존재: {'Yes' if key_info.get('api_key') else 'No'}")
                print(f"  시크릿 존재: {'Yes' if key_info.get('api_secret') else 'No'}")
                print()

        else:
            print("API 키 설정이 없습니다.")

    except Exception as e:
        print(f"오류: {e}")

    print("=" * 60)

if __name__ == "__main__":
    check_api_keys()