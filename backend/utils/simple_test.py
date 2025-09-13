"""
가장 간단한 테스트
"""
import win32com.client
import pythoncom

print("키움 COM 객체 테스트")
print("-"*40)

# COM 초기화
pythoncom.CoInitialize()

try:
    # COM 객체 생성
    kiwoom = win32com.client.Dispatch("KHOPENAPI.KHOpenAPICtrl.1")
    print("[OK] COM 객체 생성 성공")
    
    # 연결 상태
    state = kiwoom.GetConnectState()
    if state == 0:
        print("[INFO] 연결 안됨 - CommConnect() 호출 필요")
        
        # 로그인
        ret = kiwoom.CommConnect()
        print(f"CommConnect 결과: {ret}")
        
        # 수동으로 로그인 대기
        input("\n키움 로그인 창에서 로그인 후 Enter를 누르세요...")
        
        # 다시 확인
        state = kiwoom.GetConnectState()
        
    if state == 1:
        print("[OK] 연결됨!")
        
        # 계좌 정보
        account = kiwoom.GetLoginInfo("ACCNO")
        user_name = kiwoom.GetLoginInfo("USER_NAME")
        
        print(f"사용자: {user_name}")
        print(f"계좌: {account}")
        
        # 종목명 테스트
        name = kiwoom.GetMasterCodeName("005930")
        print(f"005930: {name}")
        
except Exception as e:
    print(f"[FAIL] 오류: {e}")

finally:
    pythoncom.CoUninitialize()

print("\n완료!")