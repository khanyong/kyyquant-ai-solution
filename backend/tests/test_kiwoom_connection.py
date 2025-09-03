"""
키움 OpenAPI 연결 테스트 스크립트
- 로그인 테스트
- 계좌 정보 조회
- 기본 연결 상태 확인
"""

import sys
import time
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication
import pythoncom

class KiwoomTest(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.connected = False
        
        # 이벤트 루프
        self.login_event_loop = QEventLoop()
        
        # 이벤트 연결 - dynamicCall 사용
        self.ocx.OnEventConnect[int].connect(self._on_event_connect)
        
    @pyqtSlot(int)
    def _on_event_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            print("[SUCCESS] 키움 OpenAPI 로그인 성공!")
            self.connected = True
        else:
            print(f"[ERROR] 키움 OpenAPI 로그인 실패 (에러코드: {err_code})")
            self.connected = False
        
        self.login_event_loop.exit()
    
    def comm_connect(self):
        """로그인 시도"""
        print("키움 OpenAPI 로그인 시도 중...")
        self.ocx.dynamicCall("CommConnect()")
        self.login_event_loop.exec_()
        return self.connected
    
    def get_login_info(self, tag):
        """로그인 정보 조회"""
        return self.ocx.dynamicCall("GetLoginInfo(QString)", tag)
    
    def test_connection(self):
        """연결 테스트 실행"""
        print("="*50)
        print("키움 OpenAPI 연결 테스트 시작")
        print("="*50)
        
        # 1. 로그인
        if not self.comm_connect():
            print("로그인 실패로 테스트 종료")
            return False
        
        # 2. 로그인 정보 확인
        print("\n== 로그인 정보 ==")
        
        # 사용자 ID
        user_id = self.get_login_info("USER_ID")
        print(f"  - 사용자 ID: {user_id}")
        
        # 사용자 이름
        user_name = self.get_login_info("USER_NAME")
        print(f"  - 사용자 이름: {user_name}")
        
        # 계좌 목록
        account_list = self.get_login_info("ACCLIST")
        if account_list:
            accounts = account_list.split(';')
            accounts = [acc for acc in accounts if acc]
            print(f"  - 보유 계좌: {len(accounts)}개")
            for i, acc in enumerate(accounts, 1):
                print(f"    {i}. {acc}")
        else:
            print("  - 계좌 정보를 가져올 수 없습니다.")
        
        # 키보드 보안 해제
        key_security = self.get_login_info("KEY_BSECGB")
        print(f"  - 키보드 보안: {'해제' if key_security == '0' else '설정'}")
        
        # 방화벽 설정
        firewall = self.get_login_info("FIREW_SECGB")
        print(f"  - 방화벽: {'미설정' if firewall == '0' else '설정'}")
        
        # 서버 구분
        server = self.get_login_info("GetServerGubun")
        server_type = "모의투자" if server == "1" else "실서버"
        print(f"  - 접속 서버: {server_type}")
        
        print("\n[SUCCESS] 키움 OpenAPI 연결 테스트 완료!")
        print("="*50)
        
        return True
    
    def disconnect(self):
        """연결 종료"""
        if self.connected:
            self.ocx.dynamicCall("CommTerminate()")
            print("키움 OpenAPI 연결 종료")

def main():
    """메인 실행 함수"""
    pythoncom.CoInitialize()
    
    try:
        tester = KiwoomTest()
        
        # 연결 테스트 실행
        success = tester.test_connection()
        
        if success:
            print("\n[SUCCESS] 키움 API 연동 준비 완료!")
            print("이제 실제 트레이딩 시스템을 구축할 수 있습니다.")
        else:
            print("\n[WARNING] 키움 API 연동에 문제가 있습니다.")
            print("다음 사항을 확인해주세요:")
            print("1. 키움 OpenAPI가 올바르게 설치되었는지")
            print("2. 키움증권 계정에 로그인이 가능한지")
            print("3. OpenAPI 사용 신청이 완료되었는지")
        
        # 종료 전 대기
        if success:
            input("\n엔터 키를 누르면 종료합니다...")
            tester.disconnect()
        
        # 앱 종료
        sys.exit(tester.app.exec_())
        
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        print("\n문제 해결 방법:")
        print("1. 관리자 권한으로 실행해보세요")
        print("2. 키움 OpenAPI가 C:\\OpenAPI에 설치되어 있는지 확인하세요")
        print("3. scripts/kiwoom/check_openapi_install.bat 실행해보세요")
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    main()