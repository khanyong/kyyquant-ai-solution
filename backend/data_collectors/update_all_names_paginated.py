"""
페이지네이션을 사용한 전체 종목명 업데이트
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import time

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

# PyQt5
from PyQt5.QtWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom

print("="*50)
print("🔄 전체 종목명 업데이트 (페이지네이션)")
print("="*50)

# PyQt 앱
app = QApplication.instance() or QApplication([])

# 키움 연결
kiwoom = Kiwoom()
if kiwoom.GetConnectState() == 0:
    print("키움 연결 중...")
    kiwoom.CommConnect()
    time.sleep(2)

def fix_encoding(text):
    """인코딩 수정"""
    if not text:
        return text
    
    try:
        # Latin-1 → CP949
        if any(ord(c) > 127 and ord(c) < 256 for c in text):
            fixed = text.encode('latin-1').decode('cp949')
            if any('\uac00' <= c <= '\ud7af' for c in fixed):
                return fixed
    except:
        pass
    
    return text

# 전체 데이터를 페이지별로 조회
print("\n📊 전체 데이터 조회 중...")

all_stocks = {}
page_size = 1000
offset = 0

while True:
    # 페이지별 조회
    result = supabase.table('kw_financial_snapshot')\
        .select('stock_code, stock_name')\
        .range(offset, offset + page_size - 1)\
        .execute()
    
    if not result.data:
        break
    
    print(f"  페이지 {offset//page_size + 1}: {len(result.data)}개 조회")
    
    # 고유 종목만 저장 (중복 제거)
    for r in result.data:
        if r['stock_code'] not in all_stocks:
            all_stocks[r['stock_code']] = r['stock_name']
    
    if len(result.data) < page_size:
        break
    
    offset += page_size

print(f"\n✅ 총 {len(all_stocks)}개 고유 종목 확인")

# 깨진 종목명 찾기
broken_stocks = []
for code, name in all_stocks.items():
    if name and any(c in name for c in ['¿', '°', '±', 'Â', '½', '¾', 'À', 'Ã', '¼', '¢']):
        broken_stocks.append(code)

print(f"🔧 깨진 종목명: {len(broken_stocks)}개")

if broken_stocks:
    print(f"\n깨진 종목명을 수정하시겠습니까? (y/n): ", end="")
    if input().lower() == 'y':
        
        fixed_count = 0
        
        for i, code in enumerate(broken_stocks, 1):
            if i % 50 == 0:
                print(f"\n[{i}/{len(broken_stocks)}] 진행 중...")
            
            try:
                # 키움에서 올바른 이름 가져오기
                raw_name = kiwoom.GetMasterCodeName(code)
                fixed_name = fix_encoding(raw_name)
                
                # 정상적인 이름이면 업데이트
                if fixed_name and (
                    any('\uac00' <= c <= '\ud7af' for c in fixed_name) or  # 한글
                    (fixed_name.isascii() and not any(c in fixed_name for c in '¿°±'))  # 정상 영문
                ):
                    # 모든 레코드 업데이트 (같은 종목코드)
                    supabase.table('kw_financial_snapshot')\
                        .update({'stock_name': fixed_name})\
                        .eq('stock_code', code)\
                        .execute()
                    
                    fixed_count += 1
                    
                    if fixed_count <= 10 or fixed_count % 100 == 0:
                        print(f"  {code}: {all_stocks[code][:10]}... → {fixed_name}")
                
            except Exception as e:
                if i <= 5:
                    print(f"  ❌ {code}: {e}")
            
            time.sleep(0.05)
        
        print(f"\n✅ 수정 완료: {fixed_count}/{len(broken_stocks)}개")

# 결과 확인
print("\n📋 수정 결과 확인:")
test_codes = ['900100', '000020', '005930', '000660']
for code in test_codes:
    result = supabase.table('kw_financial_snapshot')\
        .select('stock_name')\
        .eq('stock_code', code)\
        .limit(1)\
        .execute()
    
    if result.data:
        print(f"  {code}: {result.data[0]['stock_name']}")

print("\n" + "="*50)