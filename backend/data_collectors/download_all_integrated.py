"""
키움 OpenAPI+ 통합 다운로드
- 일봉 가격 데이터 (10년)
- 기술적 지표 (일별 계산)
- 재무제표 (최신)
- 한 종목당 하나의 CSV 파일
"""
import sys
import os
import time
import json
import csv
import pandas as pd
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

class IntegratedDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kiwoom Integrated Data Downloader")
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
        self.financial_data = {}
        self.all_stocks = []
        self.progress_file = "download_progress_integrated.json"
        self.data_dir = "D:/Dev/auto_stock/data/integrated"
        
        # 진행 상태
        self.total_stocks = 0
        self.current_stock_idx = 0
        self.downloaded_stocks = []
        
        # 연속조회 플래그
        self.prev_next = ""
        self.target_date = ""
        self.current_request = ""
        
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
        self.current_request = rqname
        
        if "일봉" in rqname:
            self.prev_next = prev_next
            self.process_price_data(trcode, recordname, prev_next)
        elif "재무" in rqname or "기본정보" in rqname:
            self.process_financial_data(trcode, recordname)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_price_data(self, trcode, recordname, prev_next):
        """일봉 데이터 처리"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(cnt):
                date = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "일자").strip()
                
                # 목표 날짜보다 이전이면 중단
                if self.target_date and date and date < self.target_date:
                    self.prev_next = "0"
                    break
                    
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
            print(f"    가격 데이터 처리 오류: {e}")
    
    def process_financial_data(self, trcode, recordname):
        """재무 데이터 처리"""
        try:
            # 주요 재무 지표
            financial_fields = {
                'PER': 'PER',
                'PBR': 'PBR', 
                'ROE': 'ROE',
                'EPS': 'EPS',
                'BPS': 'BPS',
                '매출액': '매출액',
                '영업이익': '영업이익',
                '당기순이익': '당기순이익',
                '부채비율': '부채비율',
                '유동비율': '유동비율',
                '시가총액': '시가총액'
            }
            
            for key, field in financial_fields.items():
                try:
                    value = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                               trcode, recordname, 0, field).strip()
                    if value and value != '':
                        self.financial_data[key] = value
                except:
                    pass
                    
        except Exception as e:
            print(f"    재무 데이터 처리 오류: {e}")
    
    def calculate_technical_indicators(self, df):
        """기술적 지표 계산"""
        if df.empty:
            return df
            
        try:
            # 이동평균선
            df['MA5'] = df['close'].rolling(window=5).mean()
            df['MA10'] = df['close'].rolling(window=10).mean()
            df['MA20'] = df['close'].rolling(window=20).mean()
            df['MA60'] = df['close'].rolling(window=60).mean()
            df['MA120'] = df['close'].rolling(window=120).mean()
            
            # 거래량 이동평균
            df['VOL_MA5'] = df['volume'].rolling(window=5).mean()
            df['VOL_MA20'] = df['volume'].rolling(window=20).mean()
            
            # RSI (14일)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
            
            # 볼린저 밴드
            df['BB_Middle'] = df['close'].rolling(window=20).mean()
            std = df['close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Middle'] + (std * 2)
            df['BB_Lower'] = df['BB_Middle'] - (std * 2)
            df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
            df['BB_PB'] = (df['close'] - df['BB_Lower']) / df['BB_Width']
            
            # 스토캐스틱 (14일)
            low_min = df['low'].rolling(window=14).min()
            high_max = df['high'].rolling(window=14).max()
            df['Stochastic_K'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
            df['Stochastic_D'] = df['Stochastic_K'].rolling(window=3).mean()
            
            # ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift())
            low_close = abs(df['low'] - df['close'].shift())
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['ATR'] = true_range.rolling(window=14).mean()
            
            # OBV (On Balance Volume)
            df['OBV'] = (df['volume'] * (~df['close'].diff().le(0) * 2 - 1)).cumsum()
            
            # 변동률
            df['Change_Rate'] = df['close'].pct_change() * 100
            df['Volume_Rate'] = df['volume'].pct_change() * 100
            
            # 일목균형표 (Ichimoku Cloud)
            # 전환선 (Conversion Line) - 9일
            nine_period_high = df['high'].rolling(window=9).max()
            nine_period_low = df['low'].rolling(window=9).min()
            df['Ichimoku_Conversion'] = (nine_period_high + nine_period_low) / 2
            
            # 기준선 (Base Line) - 26일
            period26_high = df['high'].rolling(window=26).max()
            period26_low = df['low'].rolling(window=26).min()
            df['Ichimoku_Base'] = (period26_high + period26_low) / 2
            
            # 선행스팬 A (Leading Span A) - (전환선 + 기준선) / 2, 26일 앞으로
            df['Ichimoku_SpanA'] = ((df['Ichimoku_Conversion'] + df['Ichimoku_Base']) / 2).shift(26)
            
            # 선행스팬 B (Leading Span B) - 52일 고저 평균, 26일 앞으로
            period52_high = df['high'].rolling(window=52).max()
            period52_low = df['low'].rolling(window=52).min()
            df['Ichimoku_SpanB'] = ((period52_high + period52_low) / 2).shift(26)
            
            # 후행스팬 (Lagging Span) - 종가를 26일 뒤로
            df['Ichimoku_Lagging'] = df['close'].shift(-26)
            
            # 구름대 두께
            df['Ichimoku_Cloud_Thickness'] = abs(df['Ichimoku_SpanA'] - df['Ichimoku_SpanB'])
            
            # 구름대 위치 (1: 가격이 구름 위, 0: 구름 안, -1: 구름 아래)
            df['Ichimoku_Position'] = 0
            df.loc[df['close'] > df[['Ichimoku_SpanA', 'Ichimoku_SpanB']].max(axis=1), 'Ichimoku_Position'] = 1
            df.loc[df['close'] < df[['Ichimoku_SpanA', 'Ichimoku_SpanB']].min(axis=1), 'Ichimoku_Position'] = -1
            
            # 피봇 포인트 (Pivot Points)
            df['Pivot_Point'] = (df['high'] + df['low'] + df['close']) / 3
            df['Pivot_R1'] = 2 * df['Pivot_Point'] - df['low']  # 저항선 1
            df['Pivot_S1'] = 2 * df['Pivot_Point'] - df['high']  # 지지선 1
            df['Pivot_R2'] = df['Pivot_Point'] + (df['high'] - df['low'])  # 저항선 2
            df['Pivot_S2'] = df['Pivot_Point'] - (df['high'] - df['low'])  # 지지선 2
            
            # Williams %R (14일)
            williams_period = 14
            highest_high = df['high'].rolling(window=williams_period).max()
            lowest_low = df['low'].rolling(window=williams_period).min()
            df['Williams_R'] = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
            
            # CCI (Commodity Channel Index) - 20일
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            ma_typical = typical_price.rolling(window=20).mean()
            mad = typical_price.rolling(window=20).apply(lambda x: (x - x.mean()).abs().mean())
            df['CCI'] = (typical_price - ma_typical) / (0.015 * mad)
            
            # MFI (Money Flow Index) - 14일
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            raw_money_flow = typical_price * df['volume']
            
            positive_flow = pd.Series(0, index=df.index)
            negative_flow = pd.Series(0, index=df.index)
            
            for i in range(1, len(df)):
                if typical_price.iloc[i] > typical_price.iloc[i-1]:
                    positive_flow.iloc[i] = raw_money_flow.iloc[i]
                elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                    negative_flow.iloc[i] = raw_money_flow.iloc[i]
            
            positive_mf = positive_flow.rolling(window=14).sum()
            negative_mf = negative_flow.rolling(window=14).sum()
            mfi_ratio = positive_mf / negative_mf
            df['MFI'] = 100 - (100 / (1 + mfi_ratio))
            
            # 추가 이동평균선
            df['MA3'] = df['close'].rolling(window=3).mean()
            df['MA7'] = df['close'].rolling(window=7).mean()
            df['MA15'] = df['close'].rolling(window=15).mean()
            df['MA30'] = df['close'].rolling(window=30).mean()
            df['MA50'] = df['close'].rolling(window=50).mean()
            df['MA75'] = df['close'].rolling(window=75).mean()
            df['MA100'] = df['close'].rolling(window=100).mean()
            df['MA150'] = df['close'].rolling(window=150).mean()
            df['MA200'] = df['close'].rolling(window=200).mean()
            df['MA250'] = df['close'].rolling(window=250).mean()
            
            # EMA (지수이동평균)
            df['EMA5'] = df['close'].ewm(span=5, adjust=False).mean()
            df['EMA10'] = df['close'].ewm(span=10, adjust=False).mean()
            df['EMA20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['EMA60'] = df['close'].ewm(span=60, adjust=False).mean()
            df['EMA120'] = df['close'].ewm(span=120, adjust=False).mean()
            
            # 이동평균 이격도
            df['MA5_Disparity'] = (df['close'] / df['MA5'] - 1) * 100
            df['MA20_Disparity'] = (df['close'] / df['MA20'] - 1) * 100
            df['MA60_Disparity'] = (df['close'] / df['MA60'] - 1) * 100
            
            # 골든크로스/데드크로스 신호
            df['Golden_Cross'] = ((df['MA5'] > df['MA20']) & (df['MA5'].shift(1) <= df['MA20'].shift(1))).astype(int)
            df['Death_Cross'] = ((df['MA5'] < df['MA20']) & (df['MA5'].shift(1) >= df['MA20'].shift(1))).astype(int)
            
            # Parabolic SAR
            def calculate_sar(df, acceleration=0.02, maximum=0.2):
                high = df['high']
                low = df['low']
                close = df['close']
                
                sar = close.copy()
                ep = high.copy()  # Extreme Point
                af = pd.Series([acceleration] * len(df), index=df.index)  # Acceleration Factor
                trend = pd.Series([1] * len(df), index=df.index)  # 1: uptrend, -1: downtrend
                
                for i in range(1, len(df)):
                    if trend.iloc[i-1] == 1:  # Uptrend
                        sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - sar.iloc[i-1])
                        sar.iloc[i] = min(sar.iloc[i], low.iloc[i-1], low.iloc[i-2] if i > 1 else low.iloc[i-1])
                        
                        if low.iloc[i] <= sar.iloc[i]:
                            trend.iloc[i] = -1
                            sar.iloc[i] = ep.iloc[i-1]
                            ep.iloc[i] = low.iloc[i]
                            af.iloc[i] = acceleration
                        else:
                            if high.iloc[i] > ep.iloc[i-1]:
                                ep.iloc[i] = high.iloc[i]
                                af.iloc[i] = min(af.iloc[i-1] + acceleration, maximum)
                            else:
                                ep.iloc[i] = ep.iloc[i-1]
                                af.iloc[i] = af.iloc[i-1]
                    else:  # Downtrend
                        sar.iloc[i] = sar.iloc[i-1] + af.iloc[i-1] * (ep.iloc[i-1] - sar.iloc[i-1])
                        sar.iloc[i] = max(sar.iloc[i], high.iloc[i-1], high.iloc[i-2] if i > 1 else high.iloc[i-1])
                        
                        if high.iloc[i] >= sar.iloc[i]:
                            trend.iloc[i] = 1
                            sar.iloc[i] = ep.iloc[i-1]
                            ep.iloc[i] = high.iloc[i]
                            af.iloc[i] = acceleration
                        else:
                            if low.iloc[i] < ep.iloc[i-1]:
                                ep.iloc[i] = low.iloc[i]
                                af.iloc[i] = min(af.iloc[i-1] + acceleration, maximum)
                            else:
                                ep.iloc[i] = ep.iloc[i-1]
                                af.iloc[i] = af.iloc[i-1]
                
                return sar, trend
            
            try:
                df['PSAR'], df['PSAR_Trend'] = calculate_sar(df)
            except:
                df['PSAR'] = df['close']
                df['PSAR_Trend'] = 0
            
            # ADX (Average Directional Index)
            def calculate_adx(df, period=14):
                high = df['high']
                low = df['low']
                close = df['close']
                
                plus_dm = high.diff()
                minus_dm = -low.diff()
                
                plus_dm = (plus_dm > minus_dm) * plus_dm
                minus_dm = (minus_dm > plus_dm) * minus_dm
                
                tr = pd.concat([high - low, 
                               abs(high - close.shift()), 
                               abs(low - close.shift())], axis=1).max(axis=1)
                
                atr = tr.rolling(window=period).mean()
                
                plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
                minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
                
                dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
                adx = dx.rolling(window=period).mean()
                
                return adx, plus_di, minus_di
            
            try:
                df['ADX'], df['Plus_DI'], df['Minus_DI'] = calculate_adx(df)
            except:
                df['ADX'] = 0
                df['Plus_DI'] = 0
                df['Minus_DI'] = 0
            
            # Envelope (엔벨로프)
            df['Envelope_Upper_3'] = df['MA20'] * 1.03
            df['Envelope_Lower_3'] = df['MA20'] * 0.97
            df['Envelope_Upper_5'] = df['MA20'] * 1.05
            df['Envelope_Lower_5'] = df['MA20'] * 0.95
            
            # Price Channel
            df['PC_Upper_20'] = df['high'].rolling(window=20).max()
            df['PC_Lower_20'] = df['low'].rolling(window=20).min()
            df['PC_Middle_20'] = (df['PC_Upper_20'] + df['PC_Lower_20']) / 2
            
            # Donchian Channel
            df['DC_Upper'] = df['high'].rolling(window=20).max()
            df['DC_Lower'] = df['low'].rolling(window=20).min()
            df['DC_Middle'] = (df['DC_Upper'] + df['DC_Lower']) / 2
            
            # Keltner Channel
            ema = df['close'].ewm(span=20, adjust=False).mean()
            atr = true_range.rolling(window=10).mean()
            df['KC_Upper'] = ema + (atr * 2)
            df['KC_Lower'] = ema - (atr * 2)
            df['KC_Middle'] = ema
            
            # 거래량 관련 지표
            df['Volume_Ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
            df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
            
            # 심리도 (Psychological Line)
            df['Psychological'] = df['close'].diff().apply(lambda x: 1 if x > 0 else 0).rolling(window=12).sum() / 12 * 100
            
            # Chaikin Oscillator
            adl = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']) * df['volume']
            adl = adl.cumsum()
            df['Chaikin_Oscillator'] = adl.ewm(span=3, adjust=False).mean() - adl.ewm(span=10, adjust=False).mean()
            
            # Elder Ray
            ema13 = df['close'].ewm(span=13, adjust=False).mean()
            df['Bull_Power'] = df['high'] - ema13
            df['Bear_Power'] = df['low'] - ema13
            
            # Force Index
            df['Force_Index'] = df['close'].diff() * df['volume']
            df['Force_Index_EMA'] = df['Force_Index'].ewm(span=13, adjust=False).mean()
            
            # Ease of Movement
            distance_moved = (df['high'] + df['low']) / 2 - (df['high'].shift(1) + df['low'].shift(1)) / 2
            emv = distance_moved / (df['volume'] / 100000000) / ((df['high'] - df['low']))
            df['EMV'] = emv.rolling(window=14).mean()
            
            # Mass Index
            single_ema = (df['high'] - df['low']).ewm(span=9, adjust=False).mean()
            double_ema = single_ema.ewm(span=9, adjust=False).mean()
            mass_index = (single_ema / double_ema).rolling(window=25).sum()
            df['Mass_Index'] = mass_index
            
            # Aroon Indicator
            df['Aroon_Up'] = df['high'].rolling(window=25).apply(lambda x: x.argmax() / 24 * 100)
            df['Aroon_Down'] = df['low'].rolling(window=25).apply(lambda x: x.argmin() / 24 * 100)
            df['Aroon_Oscillator'] = df['Aroon_Up'] - df['Aroon_Down']
            
        except Exception as e:
            print(f"    기술지표 계산 오류: {e}")
            
        return df
    
    def login(self):
        """로그인"""
        print("\n연결 상태 확인 중...")
        state = self.ocx.dynamicCall("GetConnectState()")
        
        if state == 1:
            print("[OK] 연결 확인 - KOA Studio 로그인 상태")
            return True
        else:
            print("[경고] 연결되지 않음")
            return False
    
    def get_all_stocks(self):
        """전체 종목 리스트"""
        stocks = []
        
        # KOSPI
        kospi = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "0")
        kospi_list = kospi.split(';')[:-1]
        
        for code in kospi_list:
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
            if name and not any(x in name for x in ['스팩', 'ETN', '리츠']):
                stocks.append({'code': code, 'name': name, 'market': 'KOSPI'})
        
        # KOSDAQ
        kosdaq = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "10")
        kosdaq_list = kosdaq.split(';')[:-1]
        
        for code in kosdaq_list:
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
            if name and not any(x in name for x in ['스팩', 'ETN', '리츠']):
                stocks.append({'code': code, 'name': name, 'market': 'KOSDAQ'})
        
        return stocks
    
    def download_stock_integrated_data(self, code, name, market):
        """통합 데이터 다운로드 (일봉 + 기술지표 + 재무)"""
        print(f"  1) 일봉 데이터 다운로드...")
        
        # 초기화
        self.price_data = []
        self.financial_data = {}
        
        # 10년 전 날짜
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3650)
        self.target_date = start_date.strftime("%Y%m%d")
        
        # 1. 일봉 데이터 (연속조회)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", end_date.strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "일봉조회", "opt10081", 0, "0101")
        
        if ret == 0:
            QTimer.singleShot(5000, self.data_loop.quit)
            self.data_loop.exec_()
            
            # 연속조회
            query_count = 1
            while self.prev_next == "2" and query_count < 20:
                time.sleep(0.2)
                
                ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                          "일봉조회", "opt10081", 2, "0101")
                
                if ret == 0:
                    QTimer.singleShot(5000, self.data_loop.quit)
                    self.data_loop.exec_()
                    query_count += 1
                else:
                    break
                    
                if self.price_data and self.price_data[-1]['date'] <= self.target_date:
                    break
        
        print(f"     {len(self.price_data)}일 가격 데이터")
        
        # 2. 재무 데이터
        print(f"  2) 재무 데이터 다운로드...")
        time.sleep(0.3)
        
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "기본정보", "opt10001", 0, "0102")
        
        if ret == 0:
            QTimer.singleShot(3000, self.data_loop.quit)
            self.data_loop.exec_()
        
        print(f"     {len(self.financial_data)}개 재무 지표")
        
        # 3. 데이터 통합 및 기술지표 계산
        if self.price_data:
            print(f"  3) 기술지표 계산...")
            
            # DataFrame 생성
            df = pd.DataFrame(self.price_data)
            df = df.sort_values('date')  # 날짜순 정렬
            
            # 기술지표 계산
            df = self.calculate_technical_indicators(df)
            
            # 재무 데이터 추가 (모든 행에 동일한 값)
            for key, value in self.financial_data.items():
                try:
                    # 숫자로 변환 시도
                    if value and value.replace('-', '').replace('.', '').isdigit():
                        df[f'Financial_{key}'] = float(value)
                    else:
                        df[f'Financial_{key}'] = value
                except:
                    df[f'Financial_{key}'] = value
            
            # 종목 정보 추가
            df['stock_code'] = code
            df['stock_name'] = name
            df['market'] = market
            
            # CSV 저장
            csv_file = f"{self.data_dir}/{code}_{name}_integrated.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            
            print(f"  4) 저장 완료: {len(df)}행 x {len(df.columns)}열")
            return len(df)
        
        return 0
    
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
        
        print("\n통합 데이터 다운로드 시작...")
        print("포함 내용: 일봉(10년) + 기술지표 + 재무제표")
        print("="*60)
        
        # 다운로드 실행
        for idx in range(start_idx, self.total_stocks):
            stock = self.all_stocks[idx]
            code = stock['code']
            name = stock['name']
            market = stock['market']
            
            if code in self.downloaded_stocks:
                continue
            
            self.current_stock_idx = idx
            
            # 진행률 표시
            percent = (idx / self.total_stocks) * 100
            print(f"\n[{idx+1}/{self.total_stocks}] {percent:.1f}% - {code} {name} ({market})")
            
            try:
                # 통합 다운로드
                rows = self.download_stock_integrated_data(code, name, market)
                
                if rows > 0:
                    self.downloaded_stocks.append(code)
                else:
                    print(f"  SKIP: 데이터 없음")
                
                # 진행 상태 저장 (5개마다)
                if idx % 5 == 0:
                    self.save_progress()
                
                # API 제한 대응
                time.sleep(1.5)  # 1.5초 대기
                
                # 20개마다 30초 휴식
                if (idx + 1) % 20 == 0:
                    print("\n[대기] API 제한 - 30초 대기...")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"  ERROR: {e}")
            
            QApplication.processEvents()
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*60)
        print("통합 다운로드 완료!")
        print(f"완료: {len(self.downloaded_stocks)}/{self.total_stocks}")
        print(f"저장 위치: {self.data_dir}")
        print("="*60)

def main():
    """메인 실행"""
    print("="*60)
    print("키움 통합 데이터 다운로드")
    print("일봉(10년) + 기술지표 + 재무제표")
    print("="*60)
    
    # pandas 설치 확인
    try:
        import pandas
    except ImportError:
        print("\n[경고] pandas 설치 필요!")
        print("실행: pip install pandas")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    
    downloader = IntegratedDownloader()
    downloader.show()
    
    QApplication.processEvents()
    time.sleep(1)
    
    if downloader.login():
        user_name = downloader.ocx.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        print(f"사용자: {user_name}")
        
        downloader.download_all()
    else:
        print("로그인 실패")
    
    print("\n프로그램 종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()