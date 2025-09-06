"""
키움 OpenAPI+ 확장 데이터 다운로드
- 업종별 데이터
- 투자자별 매매동향
- 프로그램 매매
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

class ExtendedDataDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extended Data Downloader")
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
        self.extended_dir = "D:/Dev/auto_stock/data/extended"
        
        # 디렉토리 생성
        os.makedirs(self.extended_dir, exist_ok=True)
    
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
        print(f"  데이터 수신: {rqname}")
        
        if "투자자" in rqname:
            self.process_investor_data(trcode, recordname)
        elif "업종" in rqname:
            self.process_sector_data(trcode, recordname)
        elif "프로그램" in rqname:
            self.process_program_data(trcode, recordname)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_investor_data(self, trcode, recordname):
        """투자자별 매매동향"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(min(cnt, 30)):  # 최근 30일
                date = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "일자").strip()
                
                # 투자자별 순매수
                individual = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                 trcode, recordname, i, "개인투자자").strip()
                foreign = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                              trcode, recordname, i, "외국인투자자").strip()
                institution = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                 trcode, recordname, i, "기관계").strip()
                
                if date:
                    self.current_data.append({
                        'date': date,
                        'individual': int(individual) if individual else 0,
                        'foreign': int(foreign) if foreign else 0,
                        'institution': int(institution) if institution else 0
                    })
                    
        except Exception as e:
            print(f"  투자자 데이터 처리 오류: {e}")
    
    def process_sector_data(self, trcode, recordname):
        """업종별 데이터"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(min(cnt, 20)):  # 상위 20개 업종
                sector_name = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                  trcode, recordname, i, "업종명").strip()
                index = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, i, "현재가").strip()
                change_rate = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                                  trcode, recordname, i, "등락률").strip()
                volume = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                            trcode, recordname, i, "거래량").strip()
                
                if sector_name:
                    self.current_data.append({
                        'sector': sector_name,
                        'index': float(index) if index else 0,
                        'change_rate': float(change_rate) if change_rate else 0,
                        'volume': int(volume) if volume else 0,
                        'date': datetime.now().strftime("%Y%m%d")
                    })
                    
        except Exception as e:
            print(f"  업종 데이터 처리 오류: {e}")
    
    def process_program_data(self, trcode, recordname):
        """프로그램 매매"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(min(cnt, 30)):  # 최근 30일
                date = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "일자").strip()
                buy = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                         trcode, recordname, i, "매수수량").strip()
                sell = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "매도수량").strip()
                net = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                         trcode, recordname, i, "순매수수량").strip()
                
                if date:
                    self.current_data.append({
                        'date': date,
                        'program_buy': int(buy) if buy else 0,
                        'program_sell': int(sell) if sell else 0,
                        'program_net': int(net) if net else 0
                    })
                    
        except Exception as e:
            print(f"  프로그램 데이터 처리 오류: {e}")
    
    def login(self):
        """로그인"""
        print("\n로그인 중...")
        self.ocx.dynamicCall("CommConnect()")
        QTimer.singleShot(30000, self.login_loop.quit)
        self.login_loop.exec_()
        
        state = self.ocx.dynamicCall("GetConnectState()")
        return state == 1
    
    def download_investor_trend(self, code, name):
        """투자자별 매매동향 다운로드 (opt10059)"""
        self.current_data = []
        
        print(f"  투자자별 매매동향 조회...")
        
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "일자", datetime.now().strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "금액수량구분", "2")  # 수량
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")  # 순매수
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "단위구분", "1")  # 천주
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "투자자별일별", "opt10059", 0, "0104")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
            
            if self.current_data:
                csv_file = f"{self.extended_dir}/{code}_{name}_investor.csv"
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=['date', 'individual', 'foreign', 'institution'])
                    writer.writeheader()
                    writer.writerows(self.current_data)
                return True
        return False
    
    def download_sector_data(self):
        """업종별 지수 다운로드 (opt20003)"""
        self.current_data = []
        
        print(f"  업종별 지수 조회...")
        
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "시장구분", "0")  # 코스피
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "업종코드", "001")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "업종일봉", "opt20003", 0, "0105")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
            
            if self.current_data:
                csv_file = f"{self.extended_dir}/sector_index_{datetime.now().strftime('%Y%m%d')}.csv"
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=['sector', 'index', 'change_rate', 'volume', 'date'])
                    writer.writeheader()
                    writer.writerows(self.current_data)
                return True
        return False
    
    def download_program_trading(self, code, name):
        """프로그램 매매 추이 (opt10001과 결합)"""
        self.current_data = []
        
        print(f"  프로그램 매매 조회...")
        
        # 여기서는 기본 정보를 활용
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "프로그램매매", "opt10001", 0, "0106")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
            
            # 간단한 프로그램 매매 정보 저장
            csv_file = f"{self.extended_dir}/{code}_{name}_program.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["항목", "값", "날짜"])
                writer.writerow(["종목코드", code, datetime.now().strftime("%Y%m%d")])
                writer.writerow(["종목명", name, datetime.now().strftime("%Y%m%d")])
            return True
        return False
    
    def download_all_extended_data(self):
        """확장 데이터 다운로드"""
        # 주요 종목
        test_stocks = [
            ('005930', '삼성전자'),
            ('000660', 'SK하이닉스'),
            ('035720', '카카오')
        ]
        
        print("\n확장 데이터 다운로드")
        print("="*60)
        
        # 업종 데이터
        print("\n[업종별 지수]")
        if self.download_sector_data():
            print("  [OK] 업종 지수 저장")
        
        time.sleep(1)
        
        # 개별 종목별 데이터
        for i, (code, name) in enumerate(test_stocks):
            print(f"\n[{i+1}/{len(test_stocks)}] {code} {name}")
            
            try:
                # 투자자별 매매동향
                if self.download_investor_trend(code, name):
                    print(f"  [OK] 투자자별 매매동향 저장")
                
                time.sleep(0.5)
                
                # 프로그램 매매
                if self.download_program_trading(code, name):
                    print(f"  [OK] 프로그램 매매 정보 저장")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  [ERROR] {e}")
        
        print("\n" + "="*60)
        print("확장 데이터 다운로드 완료!")
        print(f"저장 위치: {self.extended_dir}")

def main():
    """메인 실행"""
    print("="*60)
    print("키움 확장 데이터 다운로드")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    downloader = ExtendedDataDownloader()
    downloader.show()
    
    # 로그인
    if downloader.login():
        user_name = downloader.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        print(f"사용자: {user_name}")
        
        # 다운로드 실행
        downloader.download_all_extended_data()
    else:
        print("로그인 실패")
    
    print("\n프로그램 종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()