"""
키움 로그인 테스트만
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop

print("키움 로그인 테스트")
print("-"*40)

app = QApplication(sys.argv)

# OCX 직접 생성
try:
    ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
    print("[OK] OCX created successfully")
except Exception as e:
    print(f"[FAIL] OCX creation failed: {e}")
    print("\n해결 방법:")
    print("1. 키움 OpenAPI+ 설치 확인")
    print("2. 32비트 Python 사용")
    print("3. 관리자 권한으로 실행")
    sys.exit(1)

# 이벤트 루프
login_loop = QEventLoop()

def on_connect(err_code):
    if err_code == 0:
        print("[OK] Login successful!")
    else:
        print(f"[FAIL] Login failed: error code {err_code}")
    login_loop.exit()

# 이벤트 연결
ocx.OnEventConnect.connect(on_connect)

# 로그인 시도
print("로그인 시도 중...")
ocx.dynamicCall("CommConnect()")

# 대기 (최대 30초)
from PyQt5.QtCore import QTimer
QTimer.singleShot(30000, login_loop.quit)
login_loop.exec_()

# 연결 상태 확인
state = ocx.dynamicCall("GetConnectState()")
if state == 1:
    print("\n[OK] Connection status: Connected")
    
    # 계좌 정보
    account = ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
    user_id = ocx.dynamicCall("GetLoginInfo(QString)", "USER_ID")
    user_name = ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
    
    print(f"사용자: {user_name} ({user_id})")
    print(f"계좌: {account}")
else:
    print("\n[FAIL] Connection failed")

print("\n테스트 완료")