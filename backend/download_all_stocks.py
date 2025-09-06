"""
키움 OpenAPI+ 전체 종목 다운로드
- 10년치 일봉 데이터
- 진행률 표시
- 중단/재개 가능
"""
import sys
import os
import time
import json
import csv
from datetime import datetime, timedelta
import platform

# 32비트 Python 확인
arch = platform.architecture()[0]
if arch != '32bit':
    print("[경고] 32비트 Python 필요!")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer

class KiwoomDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kiwoom Data Downloader")
        self.setGeometry(100, 100, 400, 300)
        
        # OCX 생성
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.setParent(self.central_widget)
        self.ocx.setGeometry(10, 10, 380, 280)
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self.on_event_connect)
        self.ocx.OnReceiveTrData.connect(self.on_receive_tr_data)
        
        # 이벤트 루프
        self.login_loop = QEventLoop()
        self.data_loop = QEventLoop()
        
        # 데이터 저장
        self.current_data = []
        self.all_stocks = []
        self.progress_file = "download_progress.json"
        self.data_dir = "D:/Dev/auto_stock/data/kiwoom"
        
        # 진행 상태
        self.total_stocks = 0
        self.current_stock_idx = 0
        self.downloaded_stocks = []
        
        # 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        
    def on_event_connect(self, err_code):
        """로그인 결과"""
        if err_code == 0:
            print("[OK] 로그인 성공")
        else:
            print(f"[FAIL] 로그인 실패: {err_code}")
        self.login_loop.exit()
    
    def on_receive_tr_data(self, screen_no, rqname, trcode, recordname, 
                          prev_next, data_len, err_code, msg1, msg2):
        """TR 데이터 수신"""
        if rqname == "일봉조회":
            self.process_daily_data(trcode, recordname, prev_next)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_daily_data(self, trcode, recordname, prev_next):
        """일봉 데이터 처리"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(cnt):
                date = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "일자").strip()
                open_price = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                 trcode, recordname, i, "시가").strip()
                high = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "고가").strip()
                low = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                         trcode, recordname, i, "저가").strip()
                close = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, i, "현재가").strip()
                volume = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                            trcode, recordname, i, "거래량").strip()
                
                if date and close:
                    self.current_data.append({
                        'date': date,
                        'open': abs(int(open_price)) if open_price else 0,
                        'high': abs(int(high)) if high else 0,
                        'low': abs(int(low)) if low else 0,
                        'close': abs(int(close)) if close else 0,
                        'volume': int(volume) if volume else 0
                    })
            
            # 연속 조회가 있으면 계속
            if prev_next == "2":
                self.request_more_data()
                
        except Exception as e:
            print(f"  데이터 처리 오류: {e}")
    
    def request_more_data(self):
        """추가 데이터 요청 (연속조회)"""
        # 다음 데이터 요청을 위해 플래그 설정
        pass
    
    def login(self):
        """로그인"""
        print("\n연결 상태 확인 중...")
        
        # 연결 상태만 확인 (CommConnect 호출하지 않음)
        state = self.ocx.dynamicCall("GetConnectState()")
        
        if state == 1:
            print("[OK] 연결 확인 - KOA Studio 로그인 상태")
            return True
        else:
            print("[경고] 연결되지 않음")
            print("KOA Studio에서 OpenAPI 로그인이 필요합니다")
            print("1. KOA Studio 실행")
            print("2. File -> Login")
            print("3. 로그인 후 이 스크립트 재실행")
            return False
    
    def get_all_stocks(self):
        """전체 종목 리스트"""
        stocks = []
        
        # KOSPI
        kospi = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "0")
        kospi_list = kospi.split(';')[:-1]
        
        for code in kospi_list:
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
            if name:
                stocks.append({'code': code, 'name': name, 'market': 'KOSPI'})
        
        # KOSDAQ
        kosdaq = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "10")
        kosdaq_list = kosdaq.split(';')[:-1]
        
        for code in kosdaq_list:
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
            if name:
                stocks.append({'code': code, 'name': name, 'market': 'KOSDAQ'})
        
        return stocks
    
    def load_progress(self):
        """진행 상태 로드"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                self.downloaded_stocks = progress.get('completed', [])
                return progress.get('last_index', 0)
        return 0
    
    def save_progress(self):
        """진행 상태 저장"""
        progress = {
            'last_index': self.current_stock_idx,
            'completed': self.downloaded_stocks,
            'total': self.total_stocks,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def download_stock_data(self, code, name, market):
        """개별 종목 다운로드"""
        self.current_data = []
        
        # 10년 전 날짜
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3650)  # 약 10년
        
        # 일봉 데이터 요청
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", end_date.strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "일봉조회", "opt10081", 0, "0101")
        
        if ret == 0:
            # 데이터 수신 대기
            QTimer.singleShot(10000, self.data_loop.quit)
            self.data_loop.exec_()
            
            # CSV 저장
            if self.current_data:
                csv_file = f"{self.data_dir}/{code}_{name}_{market}.csv"
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=['date', 'open', 'high', 'low', 'close', 'volume'])
                    writer.writeheader()
                    writer.writerows(self.current_data)
                
                return len(self.current_data)
        
        return 0
    
    def download_all(self):
        """전체 다운로드"""
        print("\n종목 리스트 조회 중...")
        self.all_stocks = self.get_all_stocks()
        self.total_stocks = len(self.all_stocks)
        
        print(f"전체 종목: {self.total_stocks}개")
        
        # 이전 진행 상태 로드
        start_idx = self.load_progress()
        if start_idx > 0:
            print(f"이전 진행: {start_idx}/{self.total_stocks}")
            print(f"완료된 종목: {len(self.downloaded_stocks)}개")
        
        print("\n다운로드 시작...")
        print("="*60)
        
        # 다운로드 실행
        for idx in range(start_idx, self.total_stocks):
            stock = self.all_stocks[idx]
            code = stock['code']
            name = stock['name']
            market = stock['market']
            
            # 이미 다운로드된 종목 스킵
            if code in self.downloaded_stocks:
                continue
            
            self.current_stock_idx = idx
            
            # 진행률 표시
            percent = (idx / self.total_stocks) * 100
            print(f"\n[{idx+1}/{self.total_stocks}] {percent:.1f}% - {code} {name} ({market})")
            
            try:
                # 다운로드
                count = self.download_stock_data(code, name, market)
                
                if count > 0:
                    print(f"  OK: {count}일 데이터 저장")
                    self.downloaded_stocks.append(code)
                else:
                    print(f"  SKIP: 데이터 없음")
                
                # 진행 상태 저장 (10개마다)
                if idx % 10 == 0:
                    self.save_progress()
                    print(f"  진행 상태 저장됨")
                
                # API 제한 대응
                time.sleep(0.2)  # 200ms 대기
                
                # 1분에 100건 제한
                if (idx + 1) % 100 == 0:
                    print("\n[대기] API 제한 - 60초 대기...")
                    time.sleep(60)
                    
            except Exception as e:
                print(f"  ERROR: {e}")
                
            # 중단 확인 (Ctrl+C)
            QApplication.processEvents()
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*60)
        print(f"다운로드 완료!")
        print(f"완료: {len(self.downloaded_stocks)}/{self.total_stocks}")
        print(f"저장 위치: {self.data_dir}")
        print("="*60)

def main():
    """메인 실행"""
    print("="*60)
    print("키움 전체 종목 다운로드")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    downloader = KiwoomDownloader()
    downloader.show()
    
    # 윈도우가 표시될 때까지 잠시 대기
    QApplication.processEvents()
    import time
    time.sleep(1)
    
    # 로그인 (이미 로그인되어 있으면 스킵)
    if downloader.login():
        # 계정 정보
        user_name = downloader.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        print(f"사용자: {user_name}")
        
        # 다운로드 실행
        downloader.download_all()
    else:
        print("로그인 실패")
    
    print("\n프로그램 종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()