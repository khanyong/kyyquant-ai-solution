"""종목 코드 제대로 확인"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

print("Testing different query methods...")
print("="*80)

# 방법 1: 전체 데이터 가져와서 파이썬에서 unique
print("\n1. Fetch all and get unique in Python:")
try:
    # 페이지네이션으로 모든 데이터 가져오기
    all_codes = set()
    page_size = 1000
    page = 0

    while True:
        response = supabase.table('kw_price_daily') \
            .select('stock_code') \
            .range(page * page_size, (page + 1) * page_size - 1) \
            .execute()

        if not response.data:
            break

        for item in response.data:
            if item.get('stock_code'):
                all_codes.add(item['stock_code'])

        page += 1

        if len(response.data) < page_size:
            break

        if page > 1000:  # 안전장치 (100만 레코드까지)
            break

    print(f"   Total unique stocks: {len(all_codes)}")
    print(f"   Sample (first 20): {sorted(list(all_codes))[:20]}")
except Exception as e:
    print(f"   Error: {e}")

# 방법 2: 샘플 데이터 확인
print("\n2. Sample random records:")
try:
    sample = supabase.table('kw_price_daily') \
        .select('stock_code, trade_date, close') \
        .limit(100) \
        .execute()

    if sample.data:
        unique_in_sample = set([item['stock_code'] for item in sample.data])
        print(f"   Unique stocks in 100 samples: {len(unique_in_sample)}")
        print(f"   Codes: {sorted(list(unique_in_sample))}")
except Exception as e:
    print(f"   Error: {e}")

# 방법 3: 특정 종목 존재 확인
print("\n3. Check specific stocks:")
test_stocks = ['005930', '000660', '035720', '005380', '051910']
for stock in test_stocks:
    try:
        result = supabase.table('kw_price_daily') \
            .select('stock_code, trade_date', count='exact') \
            .eq('stock_code', stock) \
            .limit(1) \
            .execute()

        if result.data:
            print(f"   {stock}: EXISTS ({result.count} records)")
        else:
            print(f"   {stock}: NOT FOUND")
    except Exception as e:
        print(f"   {stock}: Error - {e}")

print("\n" + "="*80)
