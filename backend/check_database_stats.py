"""
데이터베이스 통계 확인
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

print("="*50)
print("📊 데이터베이스 통계")
print("="*50)

# 1. 전체 레코드 수
result = supabase.table('kw_financial_snapshot').select('*', count='exact').execute()
print(f"\n전체 레코드 수: {result.count}개")

# 2. 고유 종목 수
result = supabase.table('kw_financial_snapshot').select('stock_code').execute()
unique_codes = set([r['stock_code'] for r in result.data])
print(f"고유 종목 수: {len(unique_codes)}개")

# 3. 날짜별 분포
result = supabase.table('kw_financial_snapshot').select('snapshot_date').execute()
from collections import Counter
date_counts = Counter([r['snapshot_date'] for r in result.data])
print(f"\n날짜별 레코드:")
for date, count in date_counts.items():
    print(f"  {date}: {count}개")

# 4. 중복 종목 확인
result = supabase.table('kw_financial_snapshot').select('stock_code').execute()
code_counts = Counter([r['stock_code'] for r in result.data])
duplicates = {k: v for k, v in code_counts.items() if v > 1}

if duplicates:
    print(f"\n중복된 종목: {len(duplicates)}개")
    print("상위 10개 중복:")
    for code, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
        # 종목명 확인
        name_result = supabase.table('kw_financial_snapshot')\
            .select('stock_name')\
            .eq('stock_code', code)\
            .limit(1)\
            .execute()
        name = name_result.data[0]['stock_name'] if name_result.data else '?'
        print(f"  {code} ({name}): {count}번")

# 5. 깨진 종목명 확인
result = supabase.table('kw_financial_snapshot').select('stock_code, stock_name').execute()
broken_count = 0
for r in result.data:
    name = r.get('stock_name', '')
    if name and any(c in name for c in ['¿', '°', '±', 'Â', '½', '¾', 'À', 'Ã']):
        broken_count += 1

print(f"\n깨진 종목명: {broken_count}개")

print("\n" + "="*50)