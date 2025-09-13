"""
수집 로그 및 진행 파일 확인
"""
import os
import json
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
print("📊 데이터 수집 상태 확인")
print("="*50)

# 1. 진행 파일 확인
print("\n1. 로컬 진행 파일 확인:")
print("-"*40)
progress_files = [f for f in os.listdir('.') if 'collection_progress' in f and f.endswith('.json')]
if progress_files:
    for pf in progress_files:
        try:
            with open(pf, 'r') as f:
                data = json.load(f)
                print(f"\n파일: {pf}")
                print(f"  처리: {data.get('processed', 'N/A')}개")
                print(f"  전체: {data.get('total', 'N/A')}개")
                print(f"  성공: {data.get('success', 'N/A')}개")
                print(f"  실패: {data.get('fail', 'N/A')}개")
                print(f"  시간: {data.get('timestamp', 'N/A')}")
        except:
            pass
else:
    print("진행 파일이 없습니다.")

# 2. Supabase 데이터 확인
print("\n2. Supabase 데이터 상태:")
print("-"*40)

# 날짜별 레코드 수
result = supabase.table('kw_financial_snapshot').select('snapshot_date').execute()
from collections import Counter
date_counts = Counter([r['snapshot_date'] for r in result.data])

print("날짜별 레코드:")
for date, count in sorted(date_counts.items()):
    print(f"  {date}: {count}개")

# 전체 통계
result = supabase.table('kw_financial_snapshot').select('*', count='exact').execute()
print(f"\n전체 레코드: {result.count}개")

# 고유 종목
result = supabase.table('kw_financial_snapshot').select('stock_code').execute()
unique = set([r['stock_code'] for r in result.data])
print(f"고유 종목: {len(unique)}개")

# 3. 수집 로그 테이블 확인
print("\n3. 수집 로그 (kw_collection_log):")
print("-"*40)
try:
    result = supabase.table('kw_collection_log').select('*').order('created_at', desc=True).limit(5).execute()
    if result.data:
        for log in result.data:
            print(f"\n수집일: {log.get('snapshot_date')} {log.get('snapshot_time')}")
            print(f"  전체: {log.get('total_stocks')}개")
            print(f"  성공: {log.get('success_count')}개")
            print(f"  실패: {log.get('fail_count')}개")
            print(f"  완료: {log.get('completed_at')}")
    else:
        print("수집 로그가 없습니다.")
except Exception as e:
    print(f"로그 테이블 오류: {e}")

print("\n" + "="*50)