"""
키움증권 OpenAPI 모의투자 연결 테스트
32비트 Python 환경에서 실행 필요
"""

import sys
import time
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer
from PyQt5.QtWidgets import QApplication
import pythoncom

class KiwoomMockTest:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ocx = None
        self.connected = False
        self.login_event_loop = QEventLoop()
        
    def create_ocx(self):
        """OCX 컨트롤 생성"""
        try:
            self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
            print("[OK] 키움 OpenAPI OCX 로드 성공")
            return True
        except Exception as e:
            print(f"[ERROR] OCX 로드 실패: {e}")
            print("\n해결 방법:")
            print("1. 키움 OpenAPI+ 설치 확인")
            print("2. 32비트 Python 사용 확인")
            print("3. 관리자 권한으로 실행")
            return False
    
    def connect_events(self):
        """이벤트 연결"""
        try:
            # OnEventConnect 이벤트를 처리할 메서드 연결
            self.ocx.OnEventConnect.connect(self.on_event_connect)
            self.ocx.OnReceiveTrData.connect(self.on_receive_tr_data)
            self.ocx.OnReceiveRealData.connect(self.on_receive_real_data)
            print("[OK] 이벤트 핸들러 연결 성공")
            return True
        except Exception as e:
            print(f"[ERROR] 이벤트 연결 실패: {e}")
            return False
    
    def on_event_connect(self, err_code):
        """로그인 이벤트 처리"""
        if err_code == 0:
            print("[OK] 키움증권 로그인 성공!")
            self.connected = True
        else:
            error_msg = {
                -1: "통신 실패",
                -100: "사용자 정보교환 실패",
                -101: "서버 접속 실패",
                -102: "버전처리 실패"
            }.get(err_code, f"알 수 없는 오류 ({err_code})")
            print(f"[FAIL] 로그인 실패: {error_msg}")
            self.connected = False
        
        self.login_event_loop.exit()
    
    def on_receive_tr_data(self, screen_no, rq_name, tr_code, record_name, prev_next, 
                          data_length, error_code, message, spare):
        """TR 데이터 수신 이벤트"""
        print(f"[DATA] {rq_name} 수신")
        
        if rq_name == "주식기본정보":
            종목코드 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           tr_code, "", 0, "종목코드").strip()
            종목명 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                         tr_code, "", 0, "종목명").strip()
            현재가 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                        tr_code, "", 0, "현재가").strip()
            전일대비 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          tr_code, "", 0, "전일대비").strip()
            거래량 = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                        tr_code, "", 0, "거래량").strip()
            
            print(f"     종목명: {종목명} ({종목코드})")
            print(f"     현재가: {abs(int(현재가)):,}원")
            print(f"     전일대비: {int(전일대비):,}원")
            print(f"     거래량: {int(거래량):,}주")
    
    def on_receive_real_data(self, code, real_type, real_data):
        """실시간 데이터 수신"""
        if real_type == "주식체결":
            현재가 = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 10)
            전일대비 = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 11)
            등락율 = self.ocx.dynamicCall("GetCommRealData(QString, int)", code, 12)
            print(f"[실시간] {code} - 현재가: {현재가}, 전일대비: {전일대비}, 등락률: {등락율}%")
    
    def login(self):
        """로그인"""
        print("\n[1] 키움증권 로그인")
        print("-" * 40)
        
        ret = self.ocx.dynamicCall("CommConnect()")
        if ret == 0:
            print("로그인 창이 표시됩니다. 로그인해주세요...")
            self.login_event_loop.exec_()
            return self.connected
        else:
            print("[FAIL] 로그인 요청 실패")
            return False
    
    def get_account_info(self):
        """계좌 정보 조회"""
        if not self.connected:
            return
        
        print("\n[2] 계좌 정보 조회")
        print("-" * 40)
        
        # 전체 계좌 리스트
        account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCLIST")
        accounts = account_list.split(';')[:-1]
        
        # 사용자 정보
        user_id = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_ID")
        user_name = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        
        # 접속 서버 구분 (1: 모의투자, 나머지: 실거래)
        server = self.ocx.dynamicCall("GetLoginInfo(QString)", "GetServerGubun")
        server_type = "모의투자" if server == "1" else "실거래"
        
        print(f"[OK] 계좌 정보 조회 성공!")
        print(f"     사용자ID: {user_id}")
        print(f"     사용자명: {user_name}")
        print(f"     서버: {server_type}")
        print(f"     계좌 목록:")
        for i, acc in enumerate(accounts, 1):
            print(f"     {i}. {acc}")
        
        return accounts[0] if accounts else None
    
    def get_stock_info(self, stock_code="005930"):
        """주식 정보 조회 (삼성전자)"""
        if not self.connected:
            return
        
        print(f"\n[3] 주식 정보 조회 ({stock_code})")
        print("-" * 40)
        
        # TR 요청
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", 
                                  "주식기본정보", "OPT10001", 0, "0101")
        
        if ret == 0:
            print(f"[OK] 종목 정보 요청 성공 (응답 대기 중...)")
            # 실제로는 OnReceiveTrData 이벤트에서 처리됨
            QTimer.singleShot(2000, self.app.quit)  # 2초 후 종료
        else:
            print(f"[FAIL] 종목 정보 요청 실패: {ret}")
    
    def test_balance(self, account_no):
        """계좌 잔고 조회"""
        if not self.connected or not account_no:
            return
        
        print(f"\n[4] 계좌 잔고 조회 ({account_no})")
        print("-" * 40)
        
        # 계좌 잔고 조회 (OPW00001: 예수금상세현황요청)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "계좌번호", account_no)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "")
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)", 
                                  "계좌평가현황", "OPW00001", 0, "0102")
        
        if ret == 0:
            print("[OK] 잔고 조회 요청 성공")
        else:
            print(f"[FAIL] 잔고 조회 요청 실패: {ret}")
    
    def run_test(self):
        """전체 테스트 실행"""
        print("="*60)
        print("키움증권 OpenAPI 모의투자 연결 테스트")
        print("="*60)
        
        # OCX 생성
        if not self.create_ocx():
            return False
        
        # 이벤트 연결
        if not self.connect_events():
            return False
        
        # 로그인
        if not self.login():
            print("\n[해결 방법]")
            print("1. 키움증권 모의투자 신청 확인")
            print("2. HTS ID/PW로 로그인")
            print("3. 공인인증서 확인")
            return False
        
        # 계좌 정보 조회
        account = self.get_account_info()
        
        # 주식 정보 조회
        self.get_stock_info("005930")  # 삼성전자
        
        # 잔고 조회
        if account:
            self.test_balance(account)
        
        print("\n" + "="*60)
        print("[SUCCESS] 모의투자 연결 테스트 완료!")
        print("="*60)
        print("\n다음 단계:")
        print("1. 자동매매 전략 개발")
        print("2. 모의투자에서 테스트")
        print("3. 실전 적용")
        
        # 이벤트 루프 실행 (TR 응답 대기)
        self.app.exec_()
        
        return True

def check_environment():
    """실행 환경 체크"""
    import platform
    
    print("\n[환경 체크]")
    print(f"Python 버전: {sys.version}")
    print(f"아키텍처: {platform.architecture()[0]}")
    
    if "64" in platform.architecture()[0]:
        print("\n[WARNING] 64비트 Python 감지!")
        print("키움 OpenAPI는 32비트 Python이 필요합니다.")
        print("\n해결 방법:")
        print("1. 32비트 Python 설치")
        print("2. cd backend && setup_32bit_env.bat 실행")
        print("3. venv32\\Scripts\\activate")
        print("4. python test_kiwoom_mock.py")
        return False
    
    return True

def main():
    """메인 실행"""
    pythoncom.CoInitialize()
    
    try:
        # 환경 체크
        if not check_environment():
            return
        
        # 테스트 실행
        tester = KiwoomMockTest()
        tester.run_test()
        
    except Exception as e:
        print(f"\n[ERROR] 실행 오류: {e}")
        print("\n일반적인 해결 방법:")
        print("1. 키움 OpenAPI+ 설치 확인")
        print("2. 32비트 Python 사용")
        print("3. PyQt5 설치: pip install PyQt5")
        print("4. pywin32 설치: pip install pywin32")
    
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    main()