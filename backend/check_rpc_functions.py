"""
사용 가능한 RPC 함수들 확인
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def check_rpc_functions():
    """사용 가능한 RPC 함수들 확인"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("=" * 60)
    print("RPC 함수 테스트")
    print("=" * 60)

    # 키 관련 함수들 시도
    functions_to_test = [
        ('get_user_api_key', {'provider': 'kiwoom'}),
        ('get_api_key', {'provider_name': 'kiwoom'}),
        ('decrypt_api_key', {'provider': 'kiwoom'}),
        ('get_kiwoom_keys', {}),
        ('vault_decrypt_secret', {'name': 'kiwoom_app_key'}),
        ('get_decrypted_api_key', {'provider': 'kiwoom', 'key_type': 'app_key'}),
    ]

    for func_name, params in functions_to_test:
        print(f"\n{func_name} 함수 테스트:")
        try:
            result = supabase.rpc(func_name, params).execute()
            print(f"  ✅ 성공: {result.data}")

            # 성공한 함수가 있으면 자세히 출력
            if result.data:
                print(f"  결과 타입: {type(result.data)}")
                if isinstance(result.data, dict):
                    for key, value in result.data.items():
                        if 'key' in key.lower() or 'secret' in key.lower():
                            # 키 정보는 마스킹해서 출력
                            print(f"    {key}: {str(value)[:10]}..." if value else f"    {key}: None")
                        else:
                            print(f"    {key}: {value}")

        except Exception as e:
            print(f"  ❌ 실패: {str(e)[:100]}...")

    print("\n" + "=" * 60)
    print("성공한 함수를 사용하여 데이터 다운로더를 업데이트하세요!")
    print("=" * 60)

if __name__ == "__main__":
    check_rpc_functions()