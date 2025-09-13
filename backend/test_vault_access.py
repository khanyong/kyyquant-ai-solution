"""
Supabase Vault에서 API 키 읽기 테스트
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_vault_access():
    """Vault에서 시크릿 읽기 테스트"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("Supabase Vault 접근 테스트")
    print("=" * 60)

    try:
        # 힌트에서 제안된 get_user_api_key 함수 사용
        result = supabase.rpc('get_user_api_key', {'provider_name': 'kiwoom'}).execute()
        print("get_user_api_key 결과:")
        print(result.data)

        if result.data:
            print(f"키 정보 조회 성공!")
            print(f"제공자: {result.data.get('provider', 'N/A')}")
            print(f"API 키 존재: {'Yes' if result.data.get('api_key') else 'No'}")
        else:
            print("키 정보가 없습니다.")

    except Exception as e:
        print(f"get_user_api_key 오류: {e}")
        print("다른 방법으로 시도...")

        try:
            # 직접 Vault SQL 쿼리
            result = supabase.postgrest.from_('vault').select('*').execute()
            print("Vault 테이블 직접 조회:")
            print(result.data)
        except Exception as e2:
            print(f"Vault 테이블 오류: {e2}")

            # 사용 가능한 RPC 함수들 조회
            try:
                result = supabase.postgrest.rpc('').execute()
            except Exception as e3:
                print("사용 가능한 함수를 확인해보세요.")

    print("=" * 60)

if __name__ == "__main__":
    test_vault_access()