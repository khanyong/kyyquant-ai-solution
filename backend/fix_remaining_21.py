"""
남은 21개 깨진 종목명 수정
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
print("🔧 남은 깨진 종목명 수정")
print("="*50)

# 전체 데이터에서 깨진 종목 찾기
result = supabase.table('kw_financial_snapshot')\
    .select('stock_code, stock_name')\
    .execute()

broken = []
for r in result.data:
    name = r.get('stock_name', '')
    if name and any(c in name for c in ['¶', '¸', '±', '°', '¿', 'À', 'Ã', '¼', '½', '¾', 'Å', 'Ä']):
        broken.append((r['stock_code'], name))

print(f"\n남은 깨진 종목: {len(broken)}개")
print("-"*40)

# 깨진 종목 리스트 출력
for code, name in broken:
    # CP949로 디코딩 시도
    try:
        # 바이트 문자열로 변환 후 CP949로 디코딩
        fixed = name.encode('latin-1').decode('cp949', errors='ignore')
        print(f"{code}: {name[:20]} → {fixed}")
    except:
        print(f"{code}: {name[:20]} → [변환실패]")

# 키움 연결
print("\n키움 API에서 올바른 이름 가져오기...")
app = QApplication.instance() or QApplication([])
kiwoom = Kiwoom()

if kiwoom.GetConnectState() == 0:
    print("키움 연결 중...")
    kiwoom.CommConnect()
    time.sleep(2)

print("\n수정 시작...")
print("-"*40)

success = 0
fail = 0

for code, broken_name in broken:
    try:
        # 키움에서 올바른 이름 가져오기
        correct_name = kiwoom.GetMasterCodeName(code)
        
        # 인코딩 수정 시도
        if correct_name:
            # Latin-1 → CP949 변환
            try:
                fixed_name = correct_name.encode('latin-1').decode('cp949')
                if any('\uac00' <= c <= '\ud7af' for c in fixed_name):
                    correct_name = fixed_name
            except:
                pass
            
            # 정상적인 이름이면 업데이트
            if correct_name and not any(c in correct_name for c in ['¶', '¸', '±', '°', '¿']):
                supabase.table('kw_financial_snapshot')\
                    .update({'stock_name': correct_name})\
                    .eq('stock_code', code)\
                    .execute()
                
                print(f"✅ {code}: {broken_name[:15]} → {correct_name}")
                success += 1
            else:
                print(f"❌ {code}: 여전히 깨짐")
                fail += 1
        else:
            print(f"❌ {code}: 조회 실패")
            fail += 1
            
    except Exception as e:
        print(f"❌ {code}: 오류 - {str(e)[:30]}")
        fail += 1
    
    time.sleep(0.1)

print("\n" + "="*50)
print(f"✅ 완료: 성공 {success}개 / 실패 {fail}개")

# 최종 확인
result = supabase.table('kw_financial_snapshot')\
    .select('stock_code, stock_name')\
    .execute()

still_broken = []
for r in result.data:
    name = r.get('stock_name', '')
    if name and any(c in name for c in ['¶', '¸', '±', '°', '¿', 'À', 'Ã', '¼', '½', '¾', 'Å', 'Ä']):
        still_broken.append((r['stock_code'], name))

if still_broken:
    print(f"\n⚠️ 여전히 {len(still_broken)}개 깨져있음")
    
    # 수동 매핑 제안
    print("\n다음 코드를 fix_by_direct_mapping.py에 추가하세요:")
    print("-"*40)
    for code, name in still_broken:
        print(f"    '{code}': '',  # {name[:20]}")
else:
    print("\n✅ 모든 종목명이 정상화되었습니다!")

print("="*50)