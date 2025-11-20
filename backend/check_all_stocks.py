"""kw_price_daily 테이블 전체 종목 확인"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

print("="*80)
print("kw_price_daily Full Analysis")
print("="*80)

# 전체 레코드 수
total_count = supabase.table('kw_price_daily') \
    .select('*', count='exact', head=True) \
    .execute()

print(f"\nTotal records: {total_count.count:,}")

# 날짜 범위 확인
date_range = supabase.table('kw_price_daily') \
    .select('trade_date') \
    .order('trade_date', desc=False) \
    .limit(1) \
    .execute()

latest_date = supabase.table('kw_price_daily') \
    .select('trade_date') \
    .order('trade_date', desc=True) \
    .limit(1) \
    .execute()

if date_range.data and latest_date.data:
    print(f"Date range: {date_range.data[0]['trade_date']} ~ {latest_date.data[0]['trade_date']}")

# 고유 종목 수 (정확한 카운트)
print("\nCounting unique stocks...")
all_stocks_data = supabase.table('kw_price_daily') \
    .select('stock_code') \
    .execute()

unique_stocks = list(set([item['stock_code'] for item in all_stocks_data.data if item['stock_code']]))
print(f"Total unique stocks: {len(unique_stocks)}")

# 샘플 종목 10개
print(f"\nSample stocks (first 10):")
for stock in sorted(unique_stocks)[:10]:
    print(f"  {stock}")

# 9월 14일 이후 데이터 확인 (샘플)
print(f"\nChecking recent data (sample 20 stocks)...")
print(f"{'Stock':<10} {'Latest Date':<15} {'Total Days':<12} {'Status'}")
print("-"*80)

sample_stocks = sorted(unique_stocks)[:20]
needs_update = []

for stock_code in sample_stocks:
    latest = supabase.table('kw_price_daily') \
        .select('trade_date') \
        .eq('stock_code', stock_code) \
        .order('trade_date', desc=True) \
        .limit(1) \
        .execute()

    count = supabase.table('kw_price_daily') \
        .select('*', count='exact', head=True) \
        .eq('stock_code', stock_code) \
        .execute()

    if latest.data:
        latest_date = latest.data[0]['trade_date']
        total_days = count.count

        # 2024-09-14 이후 확인
        has_recent = latest_date >= '2024-09-14'
        status = "OK" if has_recent else "OLD"

        print(f"{stock_code:<10} {latest_date:<15} {total_days:<12} {status}")

        if not has_recent:
            needs_update.append(stock_code)

print(f"\n{'='*80}")
print(f"Summary:")
print(f"  Total stocks in DB: {len(unique_stocks)}")
print(f"  Stocks checked: {len(sample_stocks)}")
print(f"  Stocks needing update: {len(needs_update)}")
print(f"{'='*80}")
