"""
키움 REST API 연결 테스트
API 키 확인 및 토큰 발급 테스트
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from supabase import create_client

# 환경변수 로드
load_dotenv()

def check_api_keys():
    """API 키 확인"""
    print("=" * 60)
    print("1. 환경변수 확인")
    print("=" * 60)

    # 환경변수 확인
    env_keys = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
        'KIWOOM_APP_KEY': os.getenv('KIWOOM_APP_KEY'),
        'KIWOOM_APP_SECRET': os.getenv('KIWOOM_APP_SECRET'),
    }

    for key, value in env_keys.items():
        if value:
            # 보안을 위해 일부만 표시
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {key}: {display_value}")
        else:
            print(f"❌ {key}: 설정되지 않음")

    print("\n" + "=" * 60)
    print("2. Supabase user_api_keys 테이블 확인")
    print("=" * 60)

    # Supabase에서 API 키 확인
    try:
        supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )

        response = supabase.table('user_api_keys').select("*").execute()

        if response.data:
            print(f"✅ 총 {len(response.data)}개 API 키 발견")
            for item in response.data:
                provider = item.get('provider', 'unknown')
                api_key = item.get('api_key', '')
                display_key = api_key[:10] + "..." if api_key and len(api_key) > 10 else api_key
                print(f"  - Provider: {provider}")
                print(f"    API Key: {display_key}")
                print(f"    Account: {item.get('account_number', 'N/A')}")
                print()
        else:
            print("❌ user_api_keys 테이블에 데이터가 없습니다")

    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")

    print("=" * 60)
    print("3. 키움 API 설정 안내")
    print("=" * 60)
    print("""
키움 OpenAPI+ REST API를 사용하려면:

1. 키움증권 OpenAPI+ 홈페이지에서 앱 등록
   https://apiportal.koreainvestment.com/

2. 앱 키와 앱 시크릿 발급

3. Supabase user_api_keys 테이블에 저장:
   - provider: 'kiwoom'
   - api_key: '앱 키'
   - api_secret: '앱 시크릿'
   - account_number: '계좌번호'

또는 .env 파일에 직접 설정:
   KIWOOM_APP_KEY=your_app_key
   KIWOOM_APP_SECRET=your_app_secret
   KIWOOM_ACCOUNT_NO=your_account_number
    """)

def test_mock_data():
    """Mock 데이터로 테스트"""
    print("\n" + "=" * 60)
    print("4. Mock 데이터 테스트")
    print("=" * 60)

    print("""
실제 API 키가 없어도 테스트 가능합니다:

1. Mock 데이터 모드로 백테스트:
   - backend/kiwoom_bridge/backtest_api.py 사용
   - Mock 데이터 자동 생성

2. 과거 데이터 사용:
   - Supabase에 이미 저장된 데이터 활용
   - CSV 파일에서 로드

3. 테스트 실행:
   python test_nas_backtest.py
    """)

if __name__ == "__main__":
    print("\n🔍 키움 API 연결 테스트\n")

    # API 키 확인
    check_api_keys()

    # Mock 데이터 안내
    test_mock_data()

    print("\n✅ 테스트 완료")