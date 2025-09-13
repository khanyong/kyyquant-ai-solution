"""
키움 OpenAPI+ 기술적 지표 다운로드
- 종목별, 일별 기술지표 계산 및 저장
- 이동평균선, RSI, MACD, 볼린저밴드 등
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

class TechnicalIndicatorDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Technical Indicator Downloader")
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
        self.price_data = []
        self.technical_data = []
        self.technical_dir = "D:/Dev/auto_stock/data/technical_indicators"
        self.progress_file = "technical_progress.json"
        
        # 진행 상태
        self.total_stocks = 0
        self.current_stock_idx = 0
        self.completed_stocks = []
        
        # 디렉토리 생성
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
        if "일봉" in rqname:
            self.process_price_data(trcode, recordname, prev_next)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_price_data(self, trcode, recordname, prev_next):
        """일봉 데이터 처리 (기술지표 계산용)"""
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
                    self.price_data.append({
                        'date': date,
                        'open': abs(int(open_price)) if open_price else 0,
                        'high': abs(int(high)) if high else 0,
                        'low': abs(int(low)) if low else 0,
                        'close': abs(int(close)) if close else 0,
                        'volume': int(volume) if volume else 0
                    })
                
        except Exception as e:
            print(f"  데이터 처리 오류: {e}")
    
    def calculate_technical_indicators(self):
        """기술적 지표 계산 (일별)"""
        if not self.price_data:
            return []
        
        # 가격 데이터를 날짜 역순으로 정렬 (최신 날짜가 앞으로)
        self.price_data.sort(key=lambda x: x['date'], reverse=True)
        
        result = []
        prices = [p['close'] for p in self.price_data]
        volumes = [p['volume'] for p in self.price_data]
        highs = [p['high'] for p in self.price_data]
        lows = [p['low'] for p in self.price_data]
        
        for idx, day_data in enumerate(self.price_data):
            indicators = {
                'date': day_data['date'],
                'close': day_data['close']
            }
            
            # 이동평균선 (MA)
            if idx + 5 <= len(prices):
                indicators['MA5'] = sum(prices[idx:idx+5]) / 5
            
            if idx + 10 <= len(prices):
                indicators['MA10'] = sum(prices[idx:idx+10]) / 10
            
            if idx + 20 <= len(prices):
                indicators['MA20'] = sum(prices[idx:idx+20]) / 20
            
            if idx + 60 <= len(prices):
                indicators['MA60'] = sum(prices[idx:idx+60]) / 60
            
            if idx + 120 <= len(prices):
                indicators['MA120'] = sum(prices[idx:idx+120]) / 120
            
            # 거래량 이동평균
            if idx + 5 <= len(volumes):
                indicators['VOL_MA5'] = sum(volumes[idx:idx+5]) / 5
            
            if idx + 20 <= len(volumes):
                indicators['VOL_MA20'] = sum(volumes[idx:idx+20]) / 20
            
            # RSI (14일)
            if idx + 15 <= len(prices):
                gains = []
                losses = []
                for i in range(idx, idx + 14):
                    change = prices[i] - prices[i+1]
                    if change > 0:
                        gains.append(change)
                        losses.append(0)
                    else:
                        gains.append(0)
                        losses.append(abs(change))
                
                avg_gain = sum(gains) / 14 if gains else 0
                avg_loss = sum(losses) / 14 if losses else 0
                
                if avg_loss > 0:
                    rs = avg_gain / avg_loss
                    indicators['RSI'] = round(100 - (100 / (1 + rs)), 2)
                else:
                    indicators['RSI'] = 100 if avg_gain > 0 else 50
            
            # MACD (12, 26, 9)
            if idx + 26 <= len(prices):
                ema12 = self.calculate_ema(prices[idx:idx+12], 12)
                ema26 = self.calculate_ema(prices[idx:idx+26], 26)
                indicators['MACD'] = round(ema12 - ema26, 2)
                
                # Signal Line (9일 EMA of MACD)
                if idx + 35 <= len(prices):
                    macd_values = []
                    for j in range(9):
                        if idx + j + 26 <= len(prices):
                            e12 = self.calculate_ema(prices[idx+j:idx+j+12], 12)
                            e26 = self.calculate_ema(prices[idx+j:idx+j+26], 26)
                            macd_values.append(e12 - e26)
                    
                    if len(macd_values) >= 9:
                        indicators['MACD_Signal'] = round(self.calculate_ema(macd_values, 9), 2)
                        indicators['MACD_Histogram'] = round(indicators['MACD'] - indicators['MACD_Signal'], 2)
            
            # 볼린저 밴드 (20일)
            if idx + 20 <= len(prices):
                ma20 = sum(prices[idx:idx+20]) / 20
                std20 = self.calculate_std(prices[idx:idx+20])
                indicators['BB_Upper'] = round(ma20 + (std20 * 2), 2)
                indicators['BB_Middle'] = round(ma20, 2)
                indicators['BB_Lower'] = round(ma20 - (std20 * 2), 2)
                
                # %B (볼린저 밴드 내 위치)
                bb_width = indicators['BB_Upper'] - indicators['BB_Lower']
                if bb_width > 0:
                    indicators['BB_PB'] = round((day_data['close'] - indicators['BB_Lower']) / bb_width, 3)
            
            # 스토캐스틱 (14일)
            if idx + 14 <= len(prices):
                period_high = max(highs[idx:idx+14])
                period_low = min(lows[idx:idx+14])
                
                if period_high - period_low > 0:
                    indicators['Stochastic_K'] = round(
                        ((day_data['close'] - period_low) / (period_high - period_low)) * 100, 2
                    )
                    
                    # Stochastic D (3일 이동평균)
                    if idx + 17 <= len(prices):
                        k_values = []
                        for j in range(3):
                            if idx + j + 14 <= len(highs):
                                ph = max(highs[idx+j:idx+j+14])
                                pl = min(lows[idx+j:idx+j+14])
                                if ph - pl > 0:
                                    k_values.append(((prices[idx+j] - pl) / (ph - pl)) * 100)
                        
                        if k_values:
                            indicators['Stochastic_D'] = round(sum(k_values) / len(k_values), 2)
            
            # ATR (Average True Range) - 14일
            if idx + 14 <= len(prices):
                tr_values = []
                for i in range(idx, min(idx + 14, len(prices) - 1)):
                    high_low = highs[i] - lows[i]
                    high_close = abs(highs[i] - prices[i+1])
                    low_close = abs(lows[i] - prices[i+1])
                    tr_values.append(max(high_low, high_close, low_close))
                
                if tr_values:
                    indicators['ATR'] = round(sum(tr_values) / len(tr_values), 2)
            
            # OBV (On Balance Volume)
            if idx > 0 and idx < len(prices):
                obv = 0
                for i in range(len(prices) - 1, idx - 1, -1):
                    if i > 0:
                        if prices[i-1] > prices[i]:
                            obv += volumes[i-1]
                        elif prices[i-1] < prices[i]:
                            obv -= volumes[i-1]
                indicators['OBV'] = obv
            
            result.append(indicators)
        
        return result
    
    def calculate_ema(self, data, period):
        """지수이동평균 계산"""
        if not data or len(data) < period:
            return 0
        
        multiplier = 2 / (period + 1)
        ema = sum(data[:period]) / period
        
        for price in data[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def calculate_std(self, data):
        """표준편차 계산"""
        if not data:
            return 0
        
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        return variance ** 0.5
    
    def login(self):
        """로그인"""
        print("\n로그인 중...")
        self.ocx.dynamicCall("CommConnect()")
        QTimer.singleShot(30000, self.login_loop.quit)
        self.login_loop.exec_()
        
        state = self.ocx.dynamicCall("GetConnectState()")
        return state == 1
    
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
                self.completed_stocks = progress.get('completed', [])
                return progress.get('last_index', 0)
        return 0
    
    def save_progress(self):
        """진행 상태 저장"""
        progress = {
            'last_index': self.current_stock_idx,
            'completed': self.completed_stocks,
            'total': self.total_stocks,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    
    def download_stock_technical_indicators(self, code, name, market):
        """종목별 기술지표 다운로드 (일별)"""
        self.price_data = []
        
        # 일봉 데이터 요청 (최대 600일)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", datetime.now().strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "일봉조회", "opt10081", 0, "0101")
        
        if ret == 0:
            # 데이터 수신 대기
            QTimer.singleShot(10000, self.data_loop.quit)
            self.data_loop.exec_()
            
            # 기술지표 계산
            technical_indicators = self.calculate_technical_indicators()
            
            if technical_indicators:
                # CSV 저장
                csv_file = f"{self.technical_dir}/{code}_{name}_{market}_technical.csv"
                
                # 컬럼 이름 정의
                fieldnames = ['date', 'close', 'MA5', 'MA10', 'MA20', 'MA60', 'MA120',
                            'VOL_MA5', 'VOL_MA20', 'RSI', 'MACD', 'MACD_Signal', 'MACD_Histogram',
                            'BB_Upper', 'BB_Middle', 'BB_Lower', 'BB_PB',
                            'Stochastic_K', 'Stochastic_D', 'ATR', 'OBV']
                
                with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(technical_indicators)
                
                return len(technical_indicators)
        
        return 0
    
    def download_all_technical_indicators(self):
        """전체 종목 기술지표 다운로드"""
        print("\n종목 리스트 조회 중...")
        all_stocks = self.get_all_stocks()
        self.total_stocks = len(all_stocks)
        
        print(f"전체 종목: {self.total_stocks}개")
        
        # 이전 진행 상태 로드
        start_idx = self.load_progress()
        if start_idx > 0:
            print(f"이전 진행: {start_idx}/{self.total_stocks}")
            print(f"완료된 종목: {len(self.completed_stocks)}개")
        
        print("\n기술지표 다운로드 시작...")
        print("="*60)
        
        # 다운로드 실행
        for idx in range(start_idx, min(self.total_stocks, start_idx + 100)):  # 테스트용 100개만
            stock = all_stocks[idx]
            code = stock['code']
            name = stock['name']
            market = stock['market']
            
            # 이미 완료된 종목 스킵
            if code in self.completed_stocks:
                continue
            
            self.current_stock_idx = idx
            
            # 진행률 표시
            percent = (idx / self.total_stocks) * 100
            print(f"\n[{idx+1}/{self.total_stocks}] {percent:.1f}% - {code} {name} ({market})")
            
            try:
                # 기술지표 다운로드
                days = self.download_stock_technical_indicators(code, name, market)
                
                if days > 0:
                    print(f"  OK: {days}일 기술지표 저장")
                    self.completed_stocks.append(code)
                else:
                    print(f"  SKIP: 데이터 없음")
                
                # 진행 상태 저장 (10개마다)
                if idx % 10 == 0:
                    self.save_progress()
                    print(f"  진행 상태 저장됨")
                
                # API 제한 대응
                time.sleep(0.2)
                
                # 1분에 100건 제한
                if (idx + 1) % 100 == 0:
                    print("\n[대기] API 제한 - 60초 대기...")
                    time.sleep(60)
                    
            except Exception as e:
                print(f"  ERROR: {e}")
            
            # 중단 확인
            QApplication.processEvents()
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*60)
        print(f"기술지표 다운로드 완료!")
        print(f"완료: {len(self.completed_stocks)}개")
        print(f"저장 위치: {self.technical_dir}")
        print("="*60)

def main():
    """메인 실행"""
    print("="*60)
    print("키움 기술지표 다운로드 (종목별, 일별)")
    print("="*60)
    print("\n다운로드 항목:")
    print("- 이동평균선 (5, 10, 20, 60, 120일)")
    print("- 거래량 이동평균 (5, 20일)")
    print("- RSI (14일)")
    print("- MACD (12, 26, 9)")
    print("- 볼린저밴드 (20일)")
    print("- 스토캐스틱 (14일)")
    print("- ATR (14일)")
    print("- OBV")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    downloader = TechnicalIndicatorDownloader()
    downloader.show()
    
    # 로그인
    if downloader.login():
        user_name = downloader.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        print(f"사용자: {user_name}")
        
        # 다운로드 실행
        downloader.download_all_technical_indicators()
    else:
        print("로그인 실패")
    
    print("\n프로그램 종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()