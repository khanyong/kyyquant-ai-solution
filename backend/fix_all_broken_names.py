"""
모든 깨진 종목명 수정 - 키움 API에서 다시 가져오기
"""
import os
import sys
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
try:
    from PyQt5.QtWidgets import QApplication
    from pykiwoom.kiwoom import Kiwoom
except ImportError:
    print("32비트 Python으로 실행해주세요:")
    print(r"C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe fix_all_broken_names.py")
    sys.exit(1)

print("="*50)
print("🔧 모든 깨진 종목명 수정")
print("="*50)

# PyQt 앱
app = QApplication.instance() or QApplication([])

# 키움 연결
kiwoom = Kiwoom()
if kiwoom.GetConnectState() == 0:
    print("키움 연결 중...")
    kiwoom.CommConnect()
    time.sleep(2)

# 전체 데이터 조회
print("\n전체 종목 조회 중...")
all_stocks = []
page_size = 1000
offset = 0

while True:
    result = supabase.table('kw_financial_snapshot')\
        .select('id, stock_code, stock_name')\
        .range(offset, offset + page_size - 1)\
        .execute()
    
    if not result.data:
        break
    
    all_stocks.extend(result.data)
    
    if len(result.data) < page_size:
        break
    
    offset += page_size

print(f"총 {len(all_stocks)}개 종목 조회 완료")

# 깨진 종목 찾기
broken_stocks = []
for stock in all_stocks:
    name = stock.get('stock_name', '')
    if name:
        # 한글이 없고 정상적인 영문/숫자도 아닌 경우
        has_korean = any('\uac00' <= c <= '\ud7af' for c in name)
        is_normal_ascii = all(ord(c) < 128 or c in ' .-&()' for c in name)
        
        # 특수 문자 패턴 확인
        has_broken_chars = any(c in name for c in ['¿', '¤', '¡', '©', '¦', 'õ', 'ì', '¹', 'Ã', 'Æ', 'Ç', 'Ð', 'Ï', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', '×', 'Ø', 'Ù', 'Ú', 'Û', 'Ü'])
        
        if (not has_korean and not is_normal_ascii) or has_broken_chars:
            broken_stocks.append(stock)

print(f"\n깨진 종목: {len(broken_stocks)}개 발견")

if broken_stocks:
    print("\n깨진 종목 예시 (상위 10개):")
    for stock in broken_stocks[:10]:
        print(f"  {stock['stock_code']}: {stock['stock_name'][:30]}")
    
    print(f"\n수정을 시작하시겠습니까? (y/n): ", end="")
    response = input()
    
    if response.lower() == 'y':
        print("\n수정 시작...")
        print("-"*40)
        
        success = 0
        fail = 0
        
        for i, stock in enumerate(broken_stocks, 1):
            code = stock['stock_code']
            broken_name = stock['stock_name']
            
            if i % 50 == 0:
                print(f"\n진행: {i}/{len(broken_stocks)}")
            
            try:
                # 키움에서 올바른 이름 가져오기
                correct_name = kiwoom.GetMasterCodeName(code)
                
                if correct_name and correct_name.strip():
                    # 정상적인 이름인지 확인
                    if not any(c in correct_name for c in ['¿', '¤', '¡', '©', '¦', 'õ', 'ì', '¹']):
                        # Supabase 업데이트
                        supabase.table('kw_financial_snapshot')\
                            .update({'stock_name': correct_name})\
                            .eq('id', stock['id'])\
                            .execute()
                        
                        success += 1
                        print(f"✅ {code}: {broken_name[:15]} → {correct_name}")
                    else:
                        # 여전히 깨진 경우 인코딩 변환 시도
                        try:
                            fixed_name = correct_name.encode('latin-1').decode('cp949')
                            if any('\uac00' <= c <= '\ud7af' for c in fixed_name):
                                supabase.table('kw_financial_snapshot')\
                                    .update({'stock_name': fixed_name})\
                                    .eq('id', stock['id'])\
                                    .execute()
                                success += 1
                                print(f"✅ {code}: {broken_name[:15]} → {fixed_name}")
                            else:
                                fail += 1
                                print(f"❌ {code}: 여전히 깨짐")
                        except:
                            fail += 1
                            print(f"❌ {code}: 변환 실패")
                else:
                    fail += 1
                    print(f"❌ {code}: 조회 실패")
                    
            except Exception as e:
                fail += 1
                print(f"❌ {code}: 오류 - {str(e)[:30]}")
            
            # API 제한 대기
            time.sleep(0.2)
            
            # 100개마다 잠시 대기
            if i % 100 == 0:
                time.sleep(2)
        
        print("\n" + "="*50)
        print(f"✅ 완료: 성공 {success}개 / 실패 {fail}개")
        
        # 최종 확인
        print("\n최종 확인 중...")
        remaining_broken = []
        
        # 다시 전체 조회
        all_stocks = []
        offset = 0
        while True:
            result = supabase.table('kw_financial_snapshot')\
                .select('stock_code, stock_name')\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            for r in result.data:
                name = r.get('stock_name', '')
                if name and any(c in name for c in ['¿', '¤', '¡', '©', '¦', 'õ', 'ì', '¹']):
                    remaining_broken.append((r['stock_code'], name))
            
            if len(result.data) < page_size:
                break
            
            offset += page_size
        
        if remaining_broken:
            print(f"\n⚠️ 여전히 {len(remaining_broken)}개 깨진 종목이 남아있습니다")
            print("\n직접 매핑이 필요한 종목:")
            for code, name in remaining_broken[:20]:
                print(f"  '{code}': '',  # {name[:20]}")
        else:
            print("\n✅ 모든 종목명이 정상화되었습니다!")

print("\n" + "="*50)