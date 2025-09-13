"""
종목명 업데이트 상태 분석
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
print("📊 종목명 업데이트 상태 분석")
print("="*50)

# 전체 데이터 조회
result = supabase.table('kw_financial_snapshot').select('stock_code, stock_name').execute()

# 분석
total_records = len(result.data)
unique_codes = {}
broken_names = []
normal_names = []
empty_names = []

for r in result.data:
    code = r['stock_code']
    name = r.get('stock_name', '')
    
    if code not in unique_codes:
        unique_codes[code] = name
    
    if not name or name == '' or name == 'None':
        empty_names.append(code)
    elif any(c in name for c in ['¿', '°', '±', 'Â', '½', '¾', 'À', 'Ã', '¼', '¢']):
        broken_names.append((code, name))
    elif any('\uac00' <= c <= '\ud7af' for c in name) or name.replace(' ', '').replace('.', '').isascii():
        normal_names.append((code, name))
    else:
        broken_names.append((code, name))

print(f"\n전체 레코드: {total_records}개")
print(f"고유 종목: {len(unique_codes)}개")
print(f"정상 종목명: {len(normal_names)}개")
print(f"깨진 종목명: {len(broken_names)}개")
print(f"빈 종목명: {len(empty_names)}개")

# 깨진 종목명 샘플
if broken_names:
    print(f"\n깨진 종목명 샘플 (최대 20개):")
    for code, name in broken_names[:20]:
        print(f"  {code}: {name[:30]}")

# 빈 종목명 샘플
if empty_names:
    print(f"\n빈 종목명 샘플 (최대 10개):")
    for code in empty_names[:10]:
        print(f"  {code}")

# 정상 종목명 샘플
if normal_names:
    print(f"\n정상 종목명 샘플 (최대 10개):")
    for code, name in normal_names[:10]:
        print(f"  {code}: {name}")

print("\n" + "="*50)