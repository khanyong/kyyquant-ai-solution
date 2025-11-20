"""kw_price_daily 테이블의 누락된 날짜 확인"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

print("=" * 80)
print("kw_price_daily 테이블 분석")
print("=" * 80)

# 1. 전체 종목 수 확인 (distinct stock_code)
all_data = supabase.table('kw_price_daily').select('stock_code').execute()
unique_stocks = sorted(list(set([item['stock_code'] for item in all_data.data if item['stock_code']])))

print(f"\n총 종목 수: {len(unique_stocks)}개")

# 2. 각 종목별 최신 날짜 확인
print(f"\n종목별 최신 데이터 날짜 (샘플 20개):")
print("-" * 80)

for i, stock_code in enumerate(unique_stocks[:20]):
    response = supabase.table('kw_price_daily') \
        .select('trade_date') \
        .eq('stock_code', stock_code) \
        .order('trade_date', desc=True) \
        .limit(1) \
        .execute()

    if response.data:
        latest_date = response.data[0]['trade_date']
        # 9월 14일 이후 데이터 확인
        if latest_date < '2024-09-14':
            status = "⚠️  9월 14일 이전"
        else:
            status = "✅ 최신"
        print(f"{stock_code}: {latest_date} {status}")

# 3. 9월 14일 이후 데이터가 없는 종목 찾기
print(f"\n9월 14일 이후 데이터 분석:")
print("-" * 80)

missing_stocks = []
updated_stocks = []

for stock_code in unique_stocks:
    response = supabase.table('kw_price_daily') \
        .select('trade_date') \
        .eq('stock_code', stock_code) \
        .order('trade_date', desc=True) \
        .limit(1) \
        .execute()

    if response.data:
        latest_date = response.data[0]['trade_date']
        if latest_date < '2024-09-14':
            missing_stocks.append((stock_code, latest_date))
        else:
            updated_stocks.append((stock_code, latest_date))

print(f"✅ 9월 14일 이후 데이터 있음: {len(updated_stocks)}개 종목")
print(f"⚠️  9월 14일 이전 데이터만 있음: {len(missing_stocks)}개 종목")

if missing_stocks:
    print(f"\n업데이트 필요 종목 목록 (최대 50개):")
    for stock_code, latest_date in missing_stocks[:50]:
        print(f"  {stock_code}: 최신 날짜 {latest_date}")

# 4. 삼성전자 상세 확인
print(f"\n삼성전자(005930) 상세 데이터:")
print("-" * 80)
samsung_response = supabase.table('kw_price_daily') \
    .select('trade_date, close, volume') \
    .eq('stock_code', '005930') \
    .order('trade_date', desc=True) \
    .limit(10) \
    .execute()

if samsung_response.data:
    for item in samsung_response.data:
        print(f"{item['trade_date']}: 종가 {item['close']:,.0f}원, 거래량 {item['volume']:,}")

    # 전체 개수
    count_response = supabase.table('kw_price_daily') \
        .select('*', count='exact', head=True) \
        .eq('stock_code', '005930') \
        .execute()
    print(f"\n총 {count_response.count}일치 데이터")

print("\n" + "=" * 80)
