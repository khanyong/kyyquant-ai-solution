"""
중복 레코드 완전 제거 - 각 종목당 1개만 남기기
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from collections import defaultdict

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

print("="*50)
print("🧹 중복 레코드 완전 제거")
print("="*50)

# 1. 전체 데이터 조회 (페이지네이션)
print("\n1. 전체 데이터 조회 중...")
all_records = []
page_size = 1000
offset = 0

while True:
    result = supabase.table('kw_financial_snapshot')\
        .select('id, stock_code, stock_name, snapshot_date, market_cap')\
        .range(offset, offset + page_size - 1)\
        .execute()
    
    if not result.data:
        break
    
    all_records.extend(result.data)
    print(f"  {len(all_records)}개 조회...")
    
    if len(result.data) < page_size:
        break
    
    offset += page_size

print(f"\n✅ 총 {len(all_records)}개 레코드 조회 완료")

# 2. 중복 분석
print("\n2. 중복 분석 중...")
stock_groups = defaultdict(list)

for record in all_records:
    stock_groups[record['stock_code']].append(record)

# 중복 통계
unique_count = len(stock_groups)
duplicate_count = sum(1 for records in stock_groups.values() if len(records) > 1)
total_duplicates = sum(len(records) - 1 for records in stock_groups.values() if len(records) > 1)

print(f"  고유 종목: {unique_count}개")
print(f"  중복된 종목: {duplicate_count}개")
print(f"  삭제할 중복 레코드: {total_duplicates}개")

# 중복 샘플 출력
print("\n  중복 예시 (상위 5개):")
duplicate_samples = [(code, records) for code, records in stock_groups.items() if len(records) > 1][:5]
for code, records in duplicate_samples:
    print(f"    {code}: {len(records)}개 - {records[0]['stock_name']}")

# 3. 중복 제거
print(f"\n3. 중복 제거를 시작하시겠습니까? (y/n): ", end="")
if input().lower() == 'y':
    
    deleted_count = 0
    error_count = 0
    
    for code, records in stock_groups.items():
        if len(records) > 1:
            # 가장 최신 것 또는 시가총액이 있는 것을 남기고 나머지 삭제
            # 정렬: snapshot_date 내림차순, market_cap 있는 것 우선
            sorted_records = sorted(records, 
                key=lambda x: (
                    x.get('snapshot_date', ''),
                    x.get('market_cap', 0) is not None and x.get('market_cap', 0) > 0
                ), 
                reverse=True
            )
            
            # 첫 번째 것을 제외하고 나머지 삭제
            keep_record = sorted_records[0]
            delete_records = sorted_records[1:]
            
            for record in delete_records:
                try:
                    supabase.table('kw_financial_snapshot')\
                        .delete()\
                        .eq('id', record['id'])\
                        .execute()
                    deleted_count += 1
                    
                    if deleted_count % 100 == 0:
                        print(f"    {deleted_count}개 삭제 중...")
                        
                except Exception as e:
                    error_count += 1
                    if error_count <= 5:
                        print(f"    ❌ 삭제 실패 ID {record['id']}: {e}")
    
    print(f"\n✅ 중복 제거 완료!")
    print(f"  삭제된 레코드: {deleted_count}개")
    print(f"  오류: {error_count}개")
    
    # 4. 결과 확인
    print("\n4. 최종 결과 확인...")
    result = supabase.table('kw_financial_snapshot').select('*', count='exact').execute()
    print(f"  남은 전체 레코드: {result.count}개")
    
    # 샘플 확인
    test_codes = ['005930', '000660', '035720']
    print("\n  샘플 확인:")
    for code in test_codes:
        result = supabase.table('kw_financial_snapshot')\
            .select('stock_code, stock_name')\
            .eq('stock_code', code)\
            .execute()
        print(f"    {code}: {len(result.data)}개 - {result.data[0]['stock_name'] if result.data else 'N/A'}")

print("\n" + "="*50)