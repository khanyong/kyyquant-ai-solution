"""
32비트 Python용 간단한 키움 데이터 다운로드
"""
import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom
import time

print("="*60)
print("키움 OpenAPI+ 데이터 다운로드 (32비트)")
print("="*60)
print(f"Python: {sys.version}")

# PyQt5 앱 생성
app = QApplication(sys.argv)

# 키움 객체 생성
kiwoom = Kiwoom()

print("키움 OpenAPI+ 연결 중...")
kiwoom.CommConnect()

# 연결 대기
for i in range(10):
    if kiwoom.GetConnectState() == 1:
        print("✓ 연결 성공!")
        break
    print(f"연결 대기 중... {i+1}/10")
    time.sleep(1)

if kiwoom.GetConnectState() != 1:
    print("✗ 연결 실패! 키움 OpenAPI+를 실행하고 로그인하세요.")
    sys.exit(1)

# 계좌 정보
accounts = kiwoom.GetLoginInfo("ACCNO")
user_name = kiwoom.GetLoginInfo("USER_NAME")
print(f"\n사용자: {user_name}")
print(f"계좌: {accounts}")

# 주요 종목 리스트
stocks = [
    ('005930', '삼성전자'),
    ('000660', 'SK하이닉스'),
    ('035720', '카카오'),
    ('035420', '네이버'),
    ('005380', '현대차'),
]

print(f"\n{len(stocks)}개 종목 다운로드 시작")
print("-"*40)

# CSV 저장 폴더
output_dir = "D:/Dev/auto_stock/data/csv"
os.makedirs(output_dir, exist_ok=True)

for code, name in stocks:
    print(f"\n[{code}] {name}")
    
    try:
        # 현재가 조회
        kiwoom.SetInputValue("종목코드", code)
        kiwoom.CommRqData("opt10001_req", "opt10001", 0, "0101")
        time.sleep(0.5)
        
        # 일봉 데이터 조회 (최근 100일)
        df = kiwoom.block_request("opt10081",
            종목코드=code,
            기준일자=datetime.now().strftime("%Y%m%d"),
            수정주가구분=1,
            output="주식일봉차트",
            next=0
        )
        
        if df is not None and not df.empty:
            # CSV 저장
            csv_file = f"{output_dir}/{code}_{name}.csv"
            df.to_csv(csv_file, encoding='utf-8-sig')
            print(f"  ✓ 저장: {csv_file}")
            print(f"  ✓ 데이터: {len(df)}일")
        else:
            print(f"  ✗ 데이터 없음")
            
    except Exception as e:
        print(f"  ✗ 오류: {e}")
    
    time.sleep(1)  # API 제한

print("\n" + "="*60)
print("다운로드 완료!")
print(f"저장 위치: {output_dir}")
print("="*60)

app.exit()