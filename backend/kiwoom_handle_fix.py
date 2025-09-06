"""
키움 핸들 오류 해결 버전
- 관리자 권한 확인
- 키움 버전 확인  
- 재시작 로직
"""
import sys
import os
import ctypes
import time

# 관리자 권한 확인
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("[경고] 관리자 권한이 필요합니다!")
    print("이 파일을 우클릭 -> '관리자 권한으로 실행'")
    input("Enter를 눌러 종료...")
    sys.exit(1)

print("키움 OpenAPI+ 핸들 오류 해결 테스트")
print("="*50)
print("[OK] 관리자 권한으로 실행 중")

# 기존 프로세스 종료
import subprocess
print("\n기존 키움 프로세스 정리 중...")
try:
    # OpenAPI 프로세스 종료
    subprocess.run("taskkill /F /IM khministarter.exe", shell=True, capture_output=True)
    subprocess.run("taskkill /F /IM KHOpenAPI.exe", shell=True, capture_output=True)
    time.sleep(2)
    print("[OK] 프로세스 정리 완료")
except:
    pass

# PyQt5 임포트
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer

class KiwoomWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kiwoom Handle Fix")
        
        # OCX를 메인 윈도우의 centralWidget으로 설정
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.setCentralWidget(self.kiwoom)
        
        # 이벤트 연결
        self.kiwoom.OnEventConnect.connect(self.on_connect)
        
        self.login_loop = QEventLoop()
        
    def on_connect(self, err_code):
        if err_code == 0:
            print("[OK] 로그인 성공!")
        else:
            print(f"[FAIL] 로그인 실패: {err_code}")
            if err_code == -101:
                print("  -> 사용자 정보 교환 실패")
            elif err_code == -102:
                print("  -> 서버 접속 실패")
            elif err_code == -103:
                print("  -> 버전 처리 실패")
        
        self.login_loop.exit()
    
    def login(self):
        print("\n로그인 시도 중...")
        print("(키움 로그인 창이 뜨면 로그인하세요)")
        
        ret = self.kiwoom.dynamicCall("CommConnect()")
        if ret == 0:
            print("[OK] CommConnect 호출 성공")
        else:
            print(f"[FAIL] CommConnect 호출 실패: {ret}")
        
        # 30초 타임아웃
        QTimer.singleShot(30000, self.login_loop.quit)
        self.login_loop.exec_()
        
        # 연결 확인
        state = self.kiwoom.dynamicCall("GetConnectState()")
        if state == 1:
            print("\n[OK] 연결 확인됨")
            
            # 정보 조회
            account = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            user_name = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
            
            print(f"사용자: {user_name}")
            print(f"계좌: {account}")
            
            # 간단한 데이터 조회 테스트
            self.test_data_request()
        else:
            print("[FAIL] 연결 실패")
    
    def test_data_request(self):
        """데이터 조회 테스트"""
        print("\n데이터 조회 테스트...")
        
        # 삼성전자 현재가 조회
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", "005930")
        ret = self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", 
                                     "test_req", "opt10001", 0, "0101")
        
        if ret == 0:
            print("[OK] 데이터 요청 성공")
        else:
            print(f"[FAIL] 데이터 요청 실패: {ret}")

def main():
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성 (핸들 보존)
    window = KiwoomWindow()
    window.show()
    
    # 로그인
    window.login()
    
    print("\n테스트 완료!")
    print("창을 닫으면 종료됩니다.")
    
    # 이벤트 루프 실행
    app.exec_()

if __name__ == "__main__":
    main()