"""
실제 깨진 종목명 찾기
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
print("🔍 깨진 종목명 찾기")
print("="*50)

# 전체 데이터 조회
all_stocks = {}
page_size = 1000
offset = 0

while True:
    result = supabase.table('kw_financial_snapshot')\
        .select('stock_code, stock_name')\
        .range(offset, offset + page_size - 1)\
        .execute()
    
    if not result.data:
        break
    
    for r in result.data:
        all_stocks[r['stock_code']] = r['stock_name']
    
    if len(result.data) < page_size:
        break
    
    offset += page_size

print(f"\n총 {len(all_stocks)}개 종목 조회")

# 깨진 종목명 찾기 (더 넓은 범위)
broken = []
for code, name in all_stocks.items():
    if name:
        # 한글이 없고, 정상적인 영문도 아닌 경우
        has_korean = any('\uac00' <= c <= '\ud7af' for c in name)
        is_normal_english = all(ord(c) < 128 or c in ' .-&' for c in name)
        
        if not has_korean and not is_normal_english:
            broken.append((code, name))

print(f"\n깨진 종목명: {len(broken)}개")

if broken:
    print("\n깨진 종목명 리스트:")
    for code, name in broken[:50]:  # 최대 50개
        # 원본과 hex 값 출력
        hex_chars = [f"{ord(c):02x}" for c in name[:10]]
        print(f"  {code}: {name[:30]}")
        print(f"         hex: {' '.join(hex_chars)}")
    
    if len(broken) > 50:
        print(f"  ... 외 {len(broken) - 50}개 더")

# 특정 패턴 확인
print("\n특정 문자 패턴 확인:")
patterns = ['¶', '¸', '±', '°', '¿', 'À', 'Ã', '¼', '½', '¾']
for pattern in patterns:
    count = sum(1 for code, name in all_stocks.items() if pattern in (name or ''))
    if count > 0:
        print(f"  '{pattern}' 포함: {count}개")

print("\n" + "="*50)