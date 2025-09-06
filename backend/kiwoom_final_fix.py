"""
키움 OpenAPI+ 최종 수정 버전
- 핸들 오류 해결
- 안정적인 연결 보장
"""
import sys
import os
import time
import ctypes
from datetime import datetime

# 32비트 Python 확인
import platform
arch = platform.architecture()[0]
if arch != '32bit':
    print("[경고] 64비트 Python 감지!")
    print("32비트 Python 필요: C:\\Users\\khanyong\\AppData\\Local\\Programs\\Python\\Python310-32\\python.exe")
    sys.exit(1)

print("키움 OpenAPI+ 연결 테스트")
print("="*50)
print(f"Python: {sys.executable}")
print(f"버전: {sys.version}")
print(f"플랫폼: {platform.machine()}")
print("="*50)

# PyQt5 임포트
try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
    from PyQt5.QAxContainer import QAxWidget
    from PyQt5.QtCore import QEventLoop, QTimer, QObject
    print("[OK] PyQt5 모듈 로드 성공")
except ImportError as e:
    print(f"[FAIL] PyQt5 설치 필요: {e}")
    print("실행: pip install PyQt5")
    sys.exit(1)

class KiwoomAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kiwoom API Connection")
        self.setGeometry(100, 100, 300, 200)
        
        print("\n1. OCX 컨트롤 생성 중...")
        
        # 중앙 위젯 생성
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        try:
            # OCX 생성 - QAxWidget 직접 사용
            self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
            self.ocx.setParent(self.central_widget)
            self.ocx.setGeometry(10, 10, 280, 180)
            
            print("[OK] OCX 생성 성공")
            
            # 핸들 확인
            hwnd = self.ocx.winId()
            if hwnd:
                print(f"[OK] 윈도우 핸들: {hwnd}")
            else:
                print("[경고] 윈도우 핸들 없음")
            
        except Exception as e:
            print(f"[FAIL] OCX 생성 실패: {e}")
            print("\n확인 사항:")
            print("1. 키움 OpenAPI+ 설치 확인")
            print("2. 32비트 Python 사용 확인")
            sys.exit(1)
        
        # 이벤트 연결
        self.setup_event_slots()
        
        # 이벤트 루프
        self.login_loop = QEventLoop()
        self.data_loop = QEventLoop()
        
        # 데이터 저장
        self.data = {}
        
    def setup_event_slots(self):
        """이벤트 연결"""
        print("\n2. 이벤트 연결 중...")
        
        try:
            # 로그인 이벤트
            self.ocx.OnEventConnect.connect(self.on_event_connect)
            print("[OK] OnEventConnect 연결")
            
            # 데이터 수신 이벤트
            self.ocx.OnReceiveTrData.connect(self.on_receive_tr_data)
            print("[OK] OnReceiveTrData 연결")
            
        except Exception as e:
            print(f"[FAIL] 이벤트 연결 실패: {e}")
    
    def on_event_connect(self, err_code):
        """로그인 결과 처리"""
        if err_code == 0:
            print("\n[OK] 로그인 성공!")
        else:
            print(f"\n[FAIL] 로그인 실패: 에러코드 {err_code}")
            error_msgs = {
                -100: "사용자 정보 교환 실패",
                -101: "서버 접속 실패", 
                -102: "버전 처리 실패",
                -103: "개인방화벽 실패",
                -104: "메모리 보호 실패",
                -105: "함수 입력값 오류",
                -106: "통신 연결 종료",
            }
            if err_code in error_msgs:
                print(f"  -> {error_msgs[err_code]}")
        
        self.login_loop.exit()
    
    def on_receive_tr_data(self, screen_no, rqname, trcode, recordname, 
                          prev_next, data_len, err_code, msg1, msg2):
        """TR 데이터 수신"""
        print(f"\n[데이터 수신] {rqname}")
        
        # 데이터 저장
        self.data['rqname'] = rqname
        self.data['trcode'] = trcode
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def comm_connect(self):
        """로그인 요청"""
        print("\n3. 로그인 요청 중...")
        print("   (키움 로그인창이 뜨면 로그인하세요)")
        
        try:
            ret = self.ocx.dynamicCall("CommConnect()")
            if ret == 0:
                print("[OK] CommConnect 호출 성공")
            else:
                print(f"[FAIL] CommConnect 실패: {ret}")
                return False
            
            # 타임아웃 30초
            QTimer.singleShot(30000, self.login_loop.quit)
            self.login_loop.exec_()
            
            return self.check_connected()
            
        except Exception as e:
            print(f"[FAIL] 로그인 요청 실패: {e}")
            return False
    
    def check_connected(self):
        """연결 상태 확인"""
        try:
            state = self.ocx.dynamicCall("GetConnectState()")
            if state == 1:
                print("[OK] 연결 상태: 연결됨")
                return True
            else:
                print("[FAIL] 연결 상태: 연결 안됨")
                return False
        except Exception as e:
            print(f"[FAIL] 상태 확인 실패: {e}")
            return False
    
    def get_login_info(self):
        """로그인 정보 조회"""
        print("\n4. 로그인 정보 조회...")
        
        try:
            user_id = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_ID")
            user_name = self.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
            account_list = self.ocx.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            server_type = self.ocx.dynamicCall("GetLoginInfo(QString)", "GetServerGubun")
            
            print(f"사용자ID: {user_id}")
            print(f"사용자명: {user_name}")
            print(f"계좌: {account_list}")
            print(f"서버: {'모의투자' if server_type == '1' else '실서버'}")
            
            return True
            
        except Exception as e:
            print(f"[FAIL] 정보 조회 실패: {e}")
            return False
    
    def test_data_request(self):
        """데이터 요청 테스트"""
        print("\n5. 데이터 요청 테스트...")
        
        try:
            # 삼성전자 종목명 조회
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", "005930")
            print(f"005930 종목명: {name}")
            
            # 현재가 조회
            self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", "005930")
            
            ret = self.ocx.dynamicCall(
                "CommRqData(QString, QString, int, QString)",
                "test_req", "opt10001", 0, "0101"
            )
            
            if ret == 0:
                print("[OK] 데이터 요청 성공")
                
                # 응답 대기 (5초)
                QTimer.singleShot(5000, self.data_loop.quit)
                self.data_loop.exec_()
                
                return True
            else:
                print(f"[FAIL] 데이터 요청 실패: {ret}")
                return False
                
        except Exception as e:
            print(f"[FAIL] 데이터 요청 오류: {e}")
            return False
    
    def get_stock_list(self):
        """전체 종목 리스트 조회"""
        print("\n6. 종목 리스트 조회...")
        
        try:
            # KOSPI
            kospi = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "0")
            kospi_list = kospi.split(';')[:-1]
            print(f"KOSPI: {len(kospi_list)}개")
            
            # KOSDAQ
            kosdaq = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "10")
            kosdaq_list = kosdaq.split(';')[:-1]
            print(f"KOSDAQ: {len(kosdaq_list)}개")
            
            total = len(kospi_list) + len(kosdaq_list)
            print(f"전체: {total}개")
            
            # 샘플 출력
            print("\n샘플 종목:")
            for code in kospi_list[:3]:
                name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
                print(f"  {code}: {name}")
            
            return True
            
        except Exception as e:
            print(f"[FAIL] 종목 조회 실패: {e}")
            return False

def main():
    """메인 실행"""
    print("\n" + "="*60)
    print("키움 OpenAPI+ 연결 테스트 (최종)")
    print("="*60)
    
    # QApplication 생성
    app = QApplication(sys.argv)
    
    # 키움 API 객체
    kiwoom = KiwoomAPI()
    kiwoom.show()  # 윈도우 표시
    
    # 연결 테스트
    if kiwoom.comm_connect():
        kiwoom.get_login_info()
        kiwoom.test_data_request()
        kiwoom.get_stock_list()
        
        print("\n" + "="*60)
        print("[성공] 모든 테스트 완료!")
        print("데이터 다운로드 준비 완료")
        print("="*60)
    else:
        print("\n[실패] 연결 실패")
    
    # 창 유지
    print("\n창을 닫으면 종료됩니다...")
    app.exec_()

if __name__ == "__main__":
    main()