"""
중복 레코드 정리
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

print("="*50)
print("🧹 중복 레코드 정리")
print("="*50)

# 모든 레코드 조회
result = supabase.table('kw_financial_snapshot').select('id, stock_code, snapshot_date').execute()
print(f"\n전체 레코드: {len(result.data)}개")

# 중복 찾기
code_dates = {}
for r in result.data:
    key = (r['stock_code'], r['snapshot_date'])
    if key not in code_dates:
        code_dates[key] = []
    code_dates[key].append(r['id'])

# 중복된 것들
duplicates = {k: v for k, v in code_dates.items() if len(v) > 1}
print(f"중복된 종목: {len(duplicates)}개")

if duplicates:
    print("\n중복 제거를 시작하시겠습니까? (y/n): ", end="")
    if input().lower() == 'y':
        deleted_count = 0
        
        for (code, date), ids in duplicates.items():
            # 첫 번째 것만 남기고 나머지 삭제
            ids_to_delete = ids[1:]  # 첫 번째 제외
            
            for id_to_delete in ids_to_delete:
                try:
                    supabase.table('kw_financial_snapshot')\
                        .delete()\
                        .eq('id', id_to_delete)\
                        .execute()
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ ID {id_to_delete} 삭제 실패: {e}")
        
        print(f"\n✅ {deleted_count}개 중복 레코드 삭제 완료")
        
        # 확인
        result = supabase.table('kw_financial_snapshot').select('*', count='exact').execute()
        print(f"남은 레코드: {result.count}개")