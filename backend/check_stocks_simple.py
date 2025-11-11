"""kw_price_daily 테이블 간단 확인"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

print("="*80)
print("kw_price_daily Summary")
print("="*80)

# 전체 종목
all_data = supabase.table('kw_price_daily').select('stock_code').execute()
unique_stocks = sorted(list(set([item['stock_code'] for item in all_data.data if item['stock_code']])))

print(f"\nTotal stocks: {len(unique_stocks)}")
print(f"Stock codes: {', '.join(unique_stocks)}")

# 각 종목별 최신/최고 날짜
print(f"\n{'Stock':<10} {'Latest Date':<15} {'Count':<10} {'Status'}")
print("-"*80)

need_update = []
for stock_code in unique_stocks:
    response = supabase.table('kw_price_daily') \
        .select('trade_date') \
        .eq('stock_code', stock_code) \
        .order('trade_date', desc=True) \
        .limit(1) \
        .execute()

    count_response = supabase.table('kw_price_daily') \
        .select('*', count='exact', head=True) \
        .eq('stock_code', stock_code) \
        .execute()

    if response.data:
        latest_date = response.data[0]['trade_date']
        count = count_response.count

        # 2024-09-14 이후 데이터 체크
        needs_data = latest_date < '2024-09-14'
        status = "NEED UPDATE" if needs_data else "OK"

        print(f"{stock_code:<10} {latest_date:<15} {count:<10} {status}")

        if needs_data:
            need_update.append(stock_code)

print(f"\n{'='*80}")
print(f"Stocks needing update (before 2024-09-14): {len(need_update)}")
if need_update:
    print(f"Stock codes to update: {', '.join(need_update)}")
print(f"{'='*80}")
