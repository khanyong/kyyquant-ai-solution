"""
실제 Supabase 데이터 조회 테스트
"""
from dotenv import load_dotenv
import os
from supabase import create_client
import pandas as pd

load_dotenv()

# Supabase 연결
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

print(f"URL: {url[:40]}...")
print(f"KEY: {key[:40]}...")

supabase = create_client(url, key)

# 005930 데이터 조회
stock_code = "005930"
start_date = "2024-01-01"
end_date = "2024-12-31"

print(f"\n=== {stock_code} 데이터 조회 ===")
print(f"기간: {start_date} ~ {end_date}")

try:
    # 전체 데이터 개수 확인
    count_response = supabase.table('kw_price_daily').select('*', count='exact').eq('stock_code', stock_code).execute()
    print(f"전체 데이터: {count_response.count}개")

    # 기간별 조회
    response = supabase.table('kw_price_daily').select('*').eq(
        'stock_code', stock_code
    ).gte('trade_date', start_date).lte('trade_date', end_date).order('trade_date').execute()

    if response.data:
        print(f"조회된 데이터: {len(response.data)}개")
        df = pd.DataFrame(response.data)
        print(f"\n컬럼: {df.columns.tolist()}")
        print(f"\n최근 5일 데이터:")
        print(df[['trade_date', 'close', 'volume']].tail())
    else:
        print("데이터 없음")

        # 다른 형식 시도
        print("\n다른 종목코드 형식 시도...")
        for alt_code in ["A005930", "KR7005930003", "SSNLF"]:
            test = supabase.table('kw_price_daily').select('*').eq('stock_code', alt_code).limit(1).execute()
            if test.data:
                print(f"[OK] {alt_code} 형식으로 데이터 존재!")
                break
        else:
            # 아무 종목이나 확인
            print("\n테이블의 샘플 데이터:")
            sample = supabase.table('kw_price_daily').select('*').limit(5).execute()
            if sample.data:
                for row in sample.data:
                    print(f"  {row.get('stock_code')}: {row.get('trade_date')}")
            else:
                print("테이블이 비어있음")

except Exception as e:
    print(f"오류: {e}")