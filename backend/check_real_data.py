"""
실제 데이터 확인 - 다양한 방법으로
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

print("="*50)
print("🔍 실제 데이터 확인")
print("="*50)

# 1. 전체 카운트 (정확한 방법)
print("\n1. 정확한 카운트 조회:")
try:
    result = supabase.table('kw_financial_snapshot').select('*', count='exact').execute()
    print(f"  전체 레코드 수: {result.count}개")
except Exception as e:
    print(f"  오류: {e}")

# 2. 날짜별 데이터
print("\n2. 날짜별 데이터:")
try:
    result = supabase.table('kw_financial_snapshot').select('snapshot_date, stock_code').execute()
    
    from collections import Counter
    date_counts = Counter([r['snapshot_date'] for r in result.data])
    
    for date, count in sorted(date_counts.items()):
        print(f"  {date}: {count}개")
    
    print(f"\n  조회된 총 레코드: {len(result.data)}개")
except Exception as e:
    print(f"  오류: {e}")

# 3. 최근 추가된 데이터 확인
print("\n3. 최근 추가된 데이터 (최신 10개):")
try:
    result = supabase.table('kw_financial_snapshot')\
        .select('stock_code, stock_name, created_at')\
        .order('created_at', desc=True)\
        .limit(10)\
        .execute()
    
    for r in result.data:
        print(f"  {r['stock_code']}: {r['stock_name']} - {r['created_at']}")
except Exception as e:
    print(f"  오류: {e}")

# 4. 특정 종목 확인 (방금 수집한 것)
print("\n4. 특정 종목 확인:")
test_codes = ['900100', '000020', '000030', '000040']
for code in test_codes:
    try:
        result = supabase.table('kw_financial_snapshot')\
            .select('stock_code, stock_name')\
            .eq('stock_code', code)\
            .execute()
        
        if result.data:
            print(f"  ✅ {code}: {result.data[0]['stock_name']}")
        else:
            print(f"  ❌ {code}: 없음")
    except Exception as e:
        print(f"  오류 {code}: {e}")

# 5. 페이징 없이 전체 조회
print("\n5. 전체 데이터 조회 (페이징 없이):")
try:
    # Range 지정하여 더 많은 데이터 조회
    result = supabase.table('kw_financial_snapshot')\
        .select('stock_code')\
        .range(0, 5000)\
        .execute()
    
    unique_codes = set([r['stock_code'] for r in result.data])
    print(f"  조회된 레코드: {len(result.data)}개")
    print(f"  고유 종목: {len(unique_codes)}개")
    
    # 일부 종목 출력
    codes_list = list(unique_codes)
    print(f"  첫 10개: {codes_list[:10]}")
    print(f"  마지막 10개: {codes_list[-10:]}")
    
except Exception as e:
    print(f"  오류: {e}")

print("\n" + "="*50)