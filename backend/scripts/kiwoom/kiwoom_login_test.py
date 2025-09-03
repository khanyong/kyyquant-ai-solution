"""
키움증권 OpenAPI 로그인 테스트
모의투자 서버 연결
"""

import sys
import os
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop, QTimer
import time

class KiwoomLogin:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.event_loop = QEventLoop()
        self.login_success = False
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self._on_event_connect)
        
    def _on_event_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            print("[성공] 로그인 성공!")
            self.login_success = True
        else:
            print(f"[실패] 로그인 실패 (에러코드: {err_code})")
            self.login_success = False
            
        # 로그인 정보 출력
        if self.login_success:
            # 사용자 정보 조회
            user_id = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_ID")
            user_name = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
            server_type = self.ocx.dynamicCall("GetLoginInfo(QString)", "GetServerGubun")
            
            print(f"\n[사용자 정보]")
            print(f"사용자 ID: {user_id}")
            print(f"사용자명: {user_name}")
            print(f"서버 구분: {server_type} (1: 모의투자, 0: 실서버)")
            
            # 계좌 정보 조회
            account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            accounts = account_list.split(';')[:-1]  # 마지막 세미콜론 제거
            
            print(f"\n[계좌 정보]")
            print(f"보유 계좌수: {len(accounts)}")
            for i, acc in enumerate(accounts, 1):
                print(f"계좌 {i}: {acc}")
                
        self.event_loop.exit()
        
    def login(self):
        """로그인 실행"""
        print("="*60)
        print("키움증권 OpenAPI 로그인")
        print("="*60)
        print()
        
        # 연결 상태 확인
        connect_state = self.ocx.dynamicCall("GetConnectState()")
        print(f"현재 연결 상태: {connect_state} (0: 미연결, 1: 연결됨)")
        
        if connect_state == 0:
            print("\n로그인 시도중...")
            print("(키움 로그인 창이 열립니다)")
            
            # 로그인 요청
            self.ocx.dynamicCall("CommConnect()")
            
            # 타임아웃 설정 (30초)
            QTimer.singleShot(30000, self.event_loop.exit)
            
            # 로그인 완료 대기
            self.event_loop.exec_()
            
        else:
            print("이미 연결되어 있습니다.")
            self.login_success = True
            
        return self.login_success
    
    def get_account_info(self):
        """계좌 정보 상세 조회"""
        if not self.login_success:
            print("로그인이 필요합니다.")
            return
            
        print("\n" + "="*60)
        print("계좌 상세 정보")
        print("="*60)
        
        # 전체 계좌 리스트
        account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        accounts = account_list.split(';')[:-1]
        
        for acc in accounts:
            print(f"\n계좌번호: {acc}")
            # 계좌 비밀번호 입력 대화상자 표시 (실제 거래시 필요)
            # self.ocx.dynamicCall("KOA_Functions(QString, QString)", "ShowAccountWindow", "")
            
    def disconnect(self):
        """연결 종료"""
        self.ocx.dynamicCall("CommTerminate()")
        print("\n연결이 종료되었습니다.")

def main():
    print("Python 버전:", sys.version)
    print()
    
    # 로그인 실행
    kiwoom = KiwoomLogin()
    
    if kiwoom.login():
        print("\n" + "="*60)
        print("로그인 성공! 추가 작업을 진행할 수 있습니다.")
        print("="*60)
        
        # 계좌 정보 조회
        kiwoom.get_account_info()
        
        # 연결 상태 유지 (필요시)
        # input("\nEnter를 누르면 연결을 종료합니다...")
        
    else:
        print("\n로그인에 실패했습니다.")
        
    print("\n프로그램을 종료합니다.")
    sys.exit(0)

if __name__ == "__main__":
    main()