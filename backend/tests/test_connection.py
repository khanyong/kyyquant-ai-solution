"""
키움 연결 간단 테스트
"""
import sys
import win32com.client
import pythoncom
import time

print("="*50)
print("키움 COM 연결 테스트")
print("="*50)

# COM 초기화
pythoncom.CoInitialize()

try:
    print("\n1. COM 객체 생성 시도...")
    kiwoom = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
    print("   [OK] COM 객체 생성 성공")
    
    print("\n2. 연결 상태 확인...")
    state = kiwoom.GetConnectState()
    if state == 0:
        print("   [INFO] 미연결 상태 - 로그인 필요")
        print("\n3. 로그인 시도...")
        ret = kiwoom.CommConnect()
        print(f"   CommConnect 결과: {ret}")
        
        print("\n   키움 로그인 창에서 로그인하세요...")
        print("   로그인 후 Enter를 누르세요...")
        input()
        
        # 재확인
        state = kiwoom.GetConnectState()
    
    if state == 1:
        print("\n[OK] 연결 성공!")
        
        # 계좌 정보
        account = kiwoom.GetLoginInfo("ACCNO")
        user_name = kiwoom.GetLoginInfo("USER_NAME")
        
        print(f"\n사용자: {user_name}")
        print(f"계좌: {account}")
        
        # 간단한 테스트
        name = kiwoom.GetMasterCodeName("005930")
        print(f"\n005930 종목명: {name}")
        
        print("\n" + "="*50)
        print("테스트 성공! 다운로드 준비 완료")
        print("="*50)
    else:
        print("\n[FAIL] 연결 실패")
        
except Exception as e:
    print(f"\n[ERROR] 오류 발생: {e}")
    print("\n해결 방법:")
    print("1. 키움 OpenAPI+ 실행 확인")
    print("2. 32비트 Python 사용 확인")
    print("3. 관리자 권한으로 실행")

finally:
    pythoncom.CoUninitialize()
    
print("\nEnter를 눌러 종료...")
input()