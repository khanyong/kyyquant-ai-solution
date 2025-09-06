"""
종목명 강제 업데이트 - 키움에서 다시 가져오기
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
print("🔧 종목명 강제 업데이트")
print("="*50)

# PyQt 앱
app = QApplication.instance() or QApplication([])

# 키움 연결
kiwoom = Kiwoom()
if kiwoom.GetConnectState() == 0:
    print("키움 연결 중...")
    kiwoom.CommConnect()
    time.sleep(2)

# 깨진 것으로 알려진 종목들 (직접 입력)
known_broken_codes = [
    # 여기에 깨진 종목 코드 입력
]

# 또는 전체 종목에서 깨진 것 찾기
all_stocks = {}
page_size = 1000
offset = 0

print("\n전체 종목 조회 중...")
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

# 깨진 종목 찾기
broken_codes = []
for code, name in all_stocks.items():
    if name:
        # 특정 깨진 문자 포함
        if any(c in name for c in ['¶', '¸', '±', '°', '¿', 'À', 'Ã', '¼', '½', '¾', '¢', 'Â']):
            broken_codes.append(code)
            if len(broken_codes) <= 10:
                print(f"  깨진 종목: {code} - {name[:20]}")

print(f"\n총 {len(broken_codes)}개 깨진 종목 발견")

if broken_codes:
    print(f"\n수정을 시작하시겠습니까? (y/n): ", end="")
    if input().lower() == 'y':
        
        success = 0
        fail = 0
        
        for i, code in enumerate(broken_codes, 1):
            print(f"[{i}/{len(broken_codes)}] {code}", end=" ")
            
            try:
                # 키움에서 이름 가져오기
                raw_name = kiwoom.GetMasterCodeName(code)
                
                # 여러 인코딩 방법 시도
                fixed_name = None
                
                # 방법 1: Latin-1 → CP949
                try:
                    test_name = raw_name.encode('latin-1').decode('cp949')
                    if any('\uac00' <= c <= '\ud7af' for c in test_name):
                        fixed_name = test_name
                except:
                    pass
                
                # 방법 2: 그대로 사용 (영문인 경우)
                if not fixed_name:
                    if raw_name and raw_name.replace(' ', '').replace('.', '').replace('-', '').isascii():
                        if not any(c in raw_name for c in ['¶', '¸', '±', '°', '¿']):
                            fixed_name = raw_name
                
                # 방법 3: UTF-8 재인코딩
                if not fixed_name:
                    try:
                        test_name = raw_name.encode('utf-8', errors='ignore').decode('utf-8')
                        if test_name and not any(c in test_name for c in ['¶', '¸', '±']):
                            fixed_name = test_name
                    except:
                        pass
                
                if fixed_name:
                    # Supabase 업데이트
                    supabase.table('kw_financial_snapshot')\
                        .update({'stock_name': fixed_name})\
                        .eq('stock_code', code)\
                        .execute()
                    
                    success += 1
                    print(f"→ {fixed_name} ✅")
                else:
                    fail += 1
                    print(f"❌ 수정 실패")
                    
            except Exception as e:
                fail += 1
                print(f"❌ 오류: {str(e)[:30]}")
            
            time.sleep(0.1)
            
            if i % 50 == 0:
                print(f"  진행: {i}/{len(broken_codes)}")
                time.sleep(1)
        
        print(f"\n✅ 완료: 성공 {success}개 / 실패 {fail}개")

print("\n" + "="*50)