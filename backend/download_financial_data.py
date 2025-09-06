"""
키움 OpenAPI+ 재무제표 및 기술지표 다운로드
"""
import sys
import os
import time
import json
import csv
from datetime import datetime
import platform

# 32비트 Python 확인
arch = platform.architecture()[0]
if arch != '32bit':
    print("[경고] 32비트 Python 필요!")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer

class FinancialDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Data Downloader")
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
        self.current_data = {}
        self.financial_dir = "D:/Dev/auto_stock/data/financial"
        self.technical_dir = "D:/Dev/auto_stock/data/technical"
        
        # 디렉토리 생성
        os.makedirs(self.financial_dir, exist_ok=True)
        os.makedirs(self.technical_dir, exist_ok=True)
    
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
        print(f"  데이터 수신: {rqname} / {trcode}")
        
        if "재무" in rqname:
            self.process_financial_data(trcode, recordname)
        elif "기본" in rqname:
            self.process_fundamental_data(trcode, recordname)
        elif "기술" in rqname:
            self.process_technical_data(trcode, recordname)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_financial_data(self, trcode, recordname):
        """재무제표 데이터 처리"""
        try:
            # 주요 재무 데이터
            fields = {
                "매출액": "매출액",
                "영업이익": "영업이익",
                "순이익": "당기순이익",
                "자산총계": "자산총계",
                "부채총계": "부채총계",
                "자본총계": "자본총계",
                "ROE": "ROE(%)",
                "PER": "PER",
                "PBR": "PBR",
                "EPS": "EPS",
                "BPS": "BPS"
            }
            
            for key, field in fields.items():
                value = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, 0, field).strip()
                self.current_data[key] = value
                
        except Exception as e:
            print(f"  재무 데이터 처리 오류: {e}")
    
    def process_fundamental_data(self, trcode, recordname):
        """기본적 분석 데이터 처리"""
        try:
            # 기본적 분석 지표
            indicators = {
                "시가총액": "시가총액",
                "시가총액비중": "시가총액비중",
                "외국인소진률": "외국인소진률",
                "대주주지분율": "대주주지분율",
                "상장주식": "상장주식",
                "유동주식": "유동주식",
                "유동비율": "유동비율",
                "부채비율": "부채비율",
                "영업이익률": "영업이익률",
                "순이익률": "순이익률"
            }
            
            for key, field in indicators.items():
                value = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, 0, field).strip()
                self.current_data[key] = value
                
        except Exception as e:
            print(f"  기본 데이터 처리 오류: {e}")
    
    def process_technical_data(self, trcode, recordname):
        """기술적 지표 계산 (일봉 데이터 기반)"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            prices = []
            volumes = []
            
            # 최근 60일 데이터 수집
            for i in range(min(cnt, 60)):
                close = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, i, "현재가").strip()
                volume = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                            trcode, recordname, i, "거래량").strip()
                
                if close:
                    prices.append(abs(int(close)))
                    volumes.append(int(volume) if volume else 0)
            
            if prices:
                # 이동평균선
                self.current_data["MA5"] = sum(prices[:5]) / min(5, len(prices))
                self.current_data["MA20"] = sum(prices[:20]) / min(20, len(prices))
                self.current_data["MA60"] = sum(prices[:60]) / min(60, len(prices))
                
                # 거래량 평균
                self.current_data["VOL_AVG20"] = sum(volumes[:20]) / min(20, len(volumes))
                
                # 변동성 (최근 20일)
                if len(prices) >= 20:
                    high_20 = max(prices[:20])
                    low_20 = min(prices[:20])
                    self.current_data["VOLATILITY"] = (high_20 - low_20) / low_20 * 100
                
                # RSI 계산 (14일)
                if len(prices) >= 15:
                    gains = []
                    losses = []
                    for i in range(14):
                        change = prices[i] - prices[i+1]
                        if change > 0:
                            gains.append(change)
                            losses.append(0)
                        else:
                            gains.append(0)
                            losses.append(abs(change))
                    
                    avg_gain = sum(gains) / 14
                    avg_loss = sum(losses) / 14
                    
                    if avg_loss > 0:
                        rs = avg_gain / avg_loss
                        self.current_data["RSI"] = 100 - (100 / (1 + rs))
                
        except Exception as e:
            print(f"  기술 지표 계산 오류: {e}")
    
    def login(self):
        """로그인"""
        print("\n로그인 중...")
        self.ocx.dynamicCall("CommConnect()")
        QTimer.singleShot(30000, self.login_loop.quit)
        self.login_loop.exec_()
        
        state = self.ocx.dynamicCall("GetConnectState()")
        return state == 1
    
    def download_financial_info(self, code, name):
        """재무제표 다운로드 (opt10001: 주식기본정보)"""
        self.current_data = {}
        
        print(f"  재무제표 조회...")
        
        # 주식기본정보 조회
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "주식기본정보", "opt10001", 0, "0101")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
            
        # 주식재무정보 조회 (opt10015)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "결산월", "")
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "재무정보", "opt10015", 0, "0102")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
        
        # 저장
        if self.current_data:
            csv_file = f"{self.financial_dir}/{code}_{name}_financial.csv"
            
            # 데이터를 행으로 변환
            rows = []
            rows.append(["항목", "값", "날짜"])
            for key, value in self.current_data.items():
                rows.append([key, value, datetime.now().strftime("%Y%m%d")])
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            return True
        return False
    
    def download_technical_indicators(self, code, name):
        """기술적 지표 계산 및 저장"""
        self.current_data = {}
        
        print(f"  기술지표 계산...")
        
        # 일봉 데이터로 기술지표 계산
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", datetime.now().strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "기술지표", "opt10081", 0, "0103")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
        
        # 저장
        if self.current_data:
            csv_file = f"{self.technical_dir}/{code}_{name}_technical.csv"
            
            rows = []
            rows.append(["지표", "값", "날짜"])
            for key, value in self.current_data.items():
                rows.append([key, value, datetime.now().strftime("%Y%m%d")])
            
            with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            
            return True
        return False
    
    def download_all_data(self):
        """전체 재무/기술 데이터 다운로드"""
        # 주요 종목만 테스트 (전체는 시간이 오래 걸림)
        test_stocks = [
            ('005930', '삼성전자'),
            ('000660', 'SK하이닉스'),
            ('035720', '카카오'),
            ('005380', '현대차'),
            ('051910', 'LG화학'),
            ('006400', '삼성SDI'),
            ('035420', 'NAVER'),
            ('003550', 'LG'),
            ('105560', 'KB금융'),
            ('055550', '신한지주')
        ]
        
        print("\n재무제표 및 기술지표 다운로드")
        print("="*60)
        
        for i, (code, name) in enumerate(test_stocks):
            print(f"\n[{i+1}/{len(test_stocks)}] {code} {name}")
            
            try:
                # 재무제표
                if self.download_financial_info(code, name):
                    print(f"  [OK] 재무제표 저장")
                
                time.sleep(0.5)
                
                # 기술지표
                if self.download_technical_indicators(code, name):
                    print(f"  [OK] 기술지표 저장")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  [ERROR] {e}")
        
        print("\n" + "="*60)
        print("다운로드 완료!")
        print(f"재무제표: {self.financial_dir}")
        print(f"기술지표: {self.technical_dir}")

def main():
    """메인 실행"""
    print("="*60)
    print("키움 재무제표 & 기술지표 다운로드")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    downloader = FinancialDownloader()
    downloader.show()
    
    # 로그인
    if downloader.login():
        user_name = downloader.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        print(f"사용자: {user_name}")
        
        # 다운로드 실행
        downloader.download_all_data()
    else:
        print("로그인 실패")
    
    print("\n프로그램 종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()