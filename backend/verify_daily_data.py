"""kw_price_daily 테이블 데이터 검증"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')
supabase = create_client(url, key)

# 삼성전자 데이터 조회
response = supabase.table('kw_price_daily') \
    .select('*') \
    .eq('stock_code', '005930') \
    .order('trade_date', desc=True) \
    .limit(10) \
    .execute()

print("=" * 60)
print("kw_price_daily 테이블 - 삼성전자 최근 10일")
print("=" * 60)

if response.data:
    print(f"\n총 {len(response.data)}개 레코드 조회")
    print()
    for item in response.data:
        print(f"날짜: {item['trade_date']}")
        print(f"  시가: {item['open']:,.0f}원")
        print(f"  고가: {item['high']:,.0f}원")
        print(f"  저가: {item['low']:,.0f}원")
        print(f"  종가: {item['close']:,.0f}원")
        print(f"  거래량: {item['volume']:,}")
        print(f"  등락률: {item['change_rate']}%")
        print()
else:
    print("데이터 없음")

# 전체 개수 확인
count_response = supabase.table('kw_price_daily') \
    .select('*', count='exact', head=True) \
    .eq('stock_code', '005930') \
    .execute()

print(f"삼성전자 전체 일봉 데이터: {count_response.count}개")
