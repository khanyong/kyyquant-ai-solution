"""
Supabase 데이터 확인
"""
import os
from dotenv import load_dotenv

load_dotenv()

print('=' * 70)
print('Checking Supabase Connection and Data')
print('=' * 70)

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

print(f'SUPABASE_URL: {url}')
print(f'SUPABASE_KEY: {key[:20] + "..." if key else "None"}')

if url and key:
    from supabase import create_client

    supabase = create_client(url, key)
    print('\n[OK] Supabase client created')

    # kw_price_daily 데이터 확인
    print('\n' + '=' * 70)
    print('Checking kw_price_daily table for 005930')
    print('=' * 70)

    # 전체 행 수
    response = supabase.table('kw_price_daily').select('trade_date', count='exact').eq('stock_code', '005930').execute()
    print(f'Total rows for 005930: {response.count}')

    # 최근 5일
    response = supabase.table('kw_price_daily').select('*').eq('stock_code', '005930').order('trade_date', desc=True).limit(5).execute()

    print(f'\nLatest 5 rows:')
    for row in response.data:
        print(f"  {row['trade_date']}: close={row['close']}, volume={row['volume']}")

    # 날짜 범위
    earliest = supabase.table('kw_price_daily').select('trade_date').eq('stock_code', '005930').order('trade_date', desc=False).limit(1).execute()
    latest = supabase.table('kw_price_daily').select('trade_date').eq('stock_code', '005930').order('trade_date', desc=True).limit(1).execute()

    if earliest.data and latest.data:
        print(f'\nDate range: {earliest.data[0]["trade_date"]} to {latest.data[0]["trade_date"]}')

    # 60일치 데이터 조회 테스트
    from datetime import datetime, timedelta

    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    print('\n' + '=' * 70)
    print(f'Testing 60-day query ({start_date.date()} to {end_date.date()})')
    print('=' * 70)

    response = supabase.table('kw_price_daily').select('*').eq('stock_code', '005930').gte('trade_date', start_date.strftime('%Y-%m-%d')).lte('trade_date', end_date.strftime('%Y-%m-%d')).order('trade_date').execute()

    print(f'Found {len(response.data)} rows')

    if len(response.data) > 0:
        print(f'First date: {response.data[0]["trade_date"]}')
        print(f'Last date: {response.data[-1]["trade_date"]}')
        print(f'Last close: {response.data[-1]["close"]}')

        # MA(20) 계산 가능 여부
        if len(response.data) >= 20:
            print(f'\n[OK] Sufficient data for MA(20) calculation ({len(response.data)} >= 20)')
        else:
            print(f'\n[ERROR] Insufficient data for MA(20) calculation ({len(response.data)} < 20)')

else:
    print('[ERROR] SUPABASE_URL or SUPABASE_KEY not found in environment')
