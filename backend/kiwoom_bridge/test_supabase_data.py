"""
Supabase 주가 데이터 조회 테스트
"""
import os
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta

# Supabase 설정
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://kpnioqijldwmidguzwox.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtwbmlvcWlqbGR3bWlkZ3V6d294Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU2MDE4MzEsImV4cCI6MjA1MTE3NzgzMX0.oQa5XHmvuUasU9MxQwqtD_F5YaLRQkc4T5k8IQq0L_o')

print(f"=== Supabase 연결 테스트 ===")
print(f"URL: {SUPABASE_URL[:40]}...")
print(f"KEY: {SUPABASE_KEY[:40]}...")

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("[OK] Supabase 연결 성공")
except Exception as e:
    print(f"[ERROR] Supabase 연결 실패: {e}")
    exit(1)

# 테스트할 주식 코드와 기간
stock_code = "005930"  # 삼성전자
start_date = "2024-01-01"
end_date = "2024-01-31"

print(f"\n=== 주가 데이터 조회 ===")
print(f"종목 코드: {stock_code}")
print(f"기간: {start_date} ~ {end_date}")

try:
    # 1. 먼저 테이블 구조 확인
    print("\n1. 최근 데이터 1건 조회...")
    test_response = supabase.table('kw_price_daily').select('*').eq('stock_code', stock_code).limit(1).execute()

    if test_response.data:
        print(f"[OK] 데이터 존재 확인")
        print(f"  컬럼: {list(test_response.data[0].keys())}")
        print(f"  샘플: {test_response.data[0]}")
    else:
        print("[ERROR] 해당 종목 데이터 없음")

        # 다른 종목 코드 시도
        print("\n2. 다른 종목 코드 형식 시도...")
        alt_codes = ["A005930", "KR005930", "005930.KS", "SSNLF"]

        for alt_code in alt_codes:
            test_response = supabase.table('kw_price_daily').select('*').eq('stock_code', alt_code).limit(1).execute()
            if test_response.data:
                print(f"[OK] {alt_code} 형식으로 데이터 발견!")
                stock_code = alt_code
                break
        else:
            # 아무 데이터나 조회
            print("\n3. 테이블의 아무 데이터나 조회...")
            any_response = supabase.table('kw_price_daily').select('*').limit(5).execute()
            if any_response.data:
                print(f"[OK] 테이블에 데이터 존재")
                print(f"  사용 가능한 종목 코드:")
                for row in any_response.data:
                    print(f"    - {row.get('stock_code')}: {row.get('trade_date')}")
            else:
                print("[ERROR] 테이블이 비어있음")
                exit(1)

    # 2. 기간별 데이터 조회
    print(f"\n4. {stock_code}의 {start_date} ~ {end_date} 데이터 조회...")
    response = supabase.table('kw_price_daily').select('*').eq(
        'stock_code', stock_code
    ).gte('trade_date', start_date).lte('trade_date', end_date).order('trade_date').execute()

    if response.data:
        print(f"[OK] {len(response.data)}개 데이터 조회 성공")

        # DataFrame으로 변환
        df = pd.DataFrame(response.data)
        print(f"\n데이터 프레임 정보:")
        print(f"  Shape: {df.shape}")
        print(f"  컬럼: {df.columns.tolist()}")
        print(f"\n처음 5개 행:")
        print(df.head())

        # 필수 컬럼 확인
        required_cols = ['close', 'trade_date']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"\n[WARNING] 필수 컬럼 누락: {missing_cols}")
        else:
            print(f"\n[OK] 필수 컬럼 모두 존재")

    else:
        print(f"[ERROR] 해당 기간 데이터 없음")

        # 사용 가능한 날짜 범위 확인
        print("\n5. 사용 가능한 날짜 범위 확인...")
        date_range = supabase.table('kw_price_daily').select('trade_date').eq(
            'stock_code', stock_code
        ).order('trade_date', desc=False).limit(1).execute()

        if date_range.data:
            min_date = date_range.data[0]['trade_date']

            date_range = supabase.table('kw_price_daily').select('trade_date').eq(
                'stock_code', stock_code
            ).order('trade_date', desc=True).limit(1).execute()

            if date_range.data:
                max_date = date_range.data[0]['trade_date']
                print(f"[OK] 사용 가능한 날짜 범위: {min_date} ~ {max_date}")

                # 최근 30일 데이터 조회
                print(f"\n6. 최근 30일 데이터 조회...")
                recent_response = supabase.table('kw_price_daily').select('*').eq(
                    'stock_code', stock_code
                ).order('trade_date', desc=True).limit(30).execute()

                if recent_response.data:
                    print(f"[OK] 최근 {len(recent_response.data)}개 데이터")
                    df_recent = pd.DataFrame(recent_response.data)
                    print(df_recent[['trade_date', 'close']].head(10))

except Exception as e:
    print(f"[ERROR] 오류 발생: {e}")
    import traceback
    traceback.print_exc()