"""
Simple RPC function test
"""

import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def test_simple_rpc():
    """간단한 RPC 함수 테스트"""

    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_ANON_KEY')
    )

    print("RPC Function Test")
    print("="*50)

    # 간단한 함수들 시도
    test_functions = [
        'get_user_api_key',
        'get_api_key',
        'decrypt_api_key',
        'get_kiwoom_api_key',
        'get_vault_secret'
    ]

    for func in test_functions:
        print(f"\nTesting {func}:")
        try:
            # 빈 파라미터로 시도
            result = supabase.rpc(func, {}).execute()
            print(f"Success: {result.data}")
        except Exception as e:
            error_msg = str(e)
            if "Could not find the function" in error_msg:
                print("Function not found")
            else:
                print(f"Error: {error_msg[:50]}")

        try:
            # provider 파라미터로 시도
            result = supabase.rpc(func, {'provider': 'kiwoom'}).execute()
            print(f"With provider param: {result.data}")
        except:
            pass

    print("\n" + "="*50)

if __name__ == "__main__":
    test_simple_rpc()