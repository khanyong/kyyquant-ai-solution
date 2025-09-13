"""
실시간 백테스트 - 필요한 데이터만 실시간으로 가져와서 테스트
"""
import sys
import os
import time
from datetime import datetime, timedelta
import platform
import pandas as pd
import numpy as np

# 32비트 Python 확인
arch = platform.architecture()[0]
if arch != '32bit':
    print("[경고] 32비트 Python 필요!")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer

class BacktestEngine(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Backtest Engine")
        self.setGeometry(100, 100, 400, 300)
        
        # OCX 생성
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.setParent(self.central_widget)
        
        # 이벤트 연결
        self.ocx.OnEventConnect.connect(self.on_event_connect)
        self.ocx.OnReceiveTrData.connect(self.on_receive_tr_data)
        
        self.login_loop = QEventLoop()
        self.data_loop = QEventLoop()
        
        self.price_data = []
        
        # 캐시 (메모리에 저장)
        self.data_cache = {}
        
    def on_event_connect(self, err_code):
        if err_code == 0:
            print("[OK] 로그인 성공")
        self.login_loop.exit()
    
    def on_receive_tr_data(self, screen_no, rqname, trcode, recordname, 
                          prev_next, data_len, err_code, msg1, msg2):
        if "일봉" in rqname:
            self.process_price_data(trcode, recordname)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_price_data(self, trcode, recordname):
        """일봉 데이터 처리"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(cnt):
                date = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "일자").strip()
                close = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, i, "현재가").strip()
                volume = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                            trcode, recordname, i, "거래량").strip()
                
                if date and close:
                    self.price_data.append({
                        'date': date,
                        'close': abs(int(close)) if close else 0,
                        'volume': int(volume) if volume else 0
                    })
        except:
            pass
    
    def login(self):
        """로그인"""
        state = self.ocx.dynamicCall("GetConnectState()")
        if state == 1:
            print("[OK] 이미 로그인됨")
            return True
        return False
    
    def get_stock_data(self, code, days=60):
        """필요한 만큼만 데이터 가져오기"""
        
        # 캐시 확인
        cache_key = f"{code}_{days}"
        if cache_key in self.data_cache:
            print(f"  캐시에서 로드: {code}")
            return self.data_cache[cache_key]
        
        # 실시간 조회
        self.price_data = []
        
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", datetime.now().strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "일봉조회", "opt10081", 0, "0101")
        
        if ret == 0:
            QTimer.singleShot(3000, self.data_loop.quit)
            self.data_loop.exec_()
            
            if self.price_data:
                df = pd.DataFrame(self.price_data)
                df = df.head(days)  # 필요한 일수만
                
                # 캐시 저장
                self.data_cache[cache_key] = df
                return df
        
        return pd.DataFrame()
    
    def calculate_indicators(self, df, indicator_list):
        """필요한 지표만 계산"""
        result = df.copy()
        
        for indicator in indicator_list:
            if indicator == 'MA5':
                result['MA5'] = result['close'].rolling(window=5).mean()
            elif indicator == 'MA20':
                result['MA20'] = result['close'].rolling(window=20).mean()
            elif indicator == 'RSI':
                delta = result['close'].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
                rs = gain / loss
                result['RSI'] = 100 - (100 / (1 + rs))
            elif indicator == 'VOLUME_RATIO':
                result['VOLUME_RATIO'] = result['volume'] / result['volume'].rolling(window=20).mean()
            # 필요한 지표만 추가
        
        return result
    
    def run_strategy(self, code, strategy_func, start_date=None, end_date=None):
        """전략 실행"""
        print(f"\n백테스트: {code}")
        
        # 필요한 데이터만 가져오기
        df = self.get_stock_data(code, days=250)  # 1년치만
        
        if df.empty:
            return None
        
        # 필요한 지표만 계산
        required_indicators = strategy_func.__annotations__.get('indicators', ['MA5', 'MA20'])
        df = self.calculate_indicators(df, required_indicators)
        
        # 전략 실행
        signals = strategy_func(df)
        
        # 수익률 계산
        returns = self.calculate_returns(df, signals)
        
        return {
            'code': code,
            'returns': returns,
            'signals': signals,
            'data': df
        }
    
    def calculate_returns(self, df, signals):
        """수익률 계산"""
        if signals is None or len(signals) == 0:
            return 0
        
        total_return = 0
        position = 0
        entry_price = 0
        
        for i, signal in enumerate(signals):
            if signal == 'BUY' and position == 0:
                entry_price = df.iloc[i]['close']
                position = 1
            elif signal == 'SELL' and position == 1:
                exit_price = df.iloc[i]['close']
                total_return += (exit_price - entry_price) / entry_price
                position = 0
        
        return total_return * 100  # 퍼센트로 변환

# 전략 예시들
def golden_cross_strategy(df):
    """골든크로스 전략"""
    golden_cross_strategy.__annotations__ = {'indicators': ['MA5', 'MA20']}
    
    signals = []
    for i in range(1, len(df)):
        if pd.notna(df.iloc[i]['MA5']) and pd.notna(df.iloc[i]['MA20']):
            if df.iloc[i]['MA5'] > df.iloc[i]['MA20'] and df.iloc[i-1]['MA5'] <= df.iloc[i-1]['MA20']:
                signals.append('BUY')
            elif df.iloc[i]['MA5'] < df.iloc[i]['MA20'] and df.iloc[i-1]['MA5'] >= df.iloc[i-1]['MA20']:
                signals.append('SELL')
            else:
                signals.append('HOLD')
        else:
            signals.append('HOLD')
    
    return signals

def rsi_strategy(df):
    """RSI 과매도/과매수 전략"""
    rsi_strategy.__annotations__ = {'indicators': ['RSI']}
    
    signals = []
    for i in range(len(df)):
        if pd.notna(df.iloc[i]['RSI']):
            if df.iloc[i]['RSI'] < 30:  # 과매도
                signals.append('BUY')
            elif df.iloc[i]['RSI'] > 70:  # 과매수
                signals.append('SELL')
            else:
                signals.append('HOLD')
        else:
            signals.append('HOLD')
    
    return signals

def volume_breakout_strategy(df):
    """거래량 돌파 전략"""
    volume_breakout_strategy.__annotations__ = {'indicators': ['MA20', 'VOLUME_RATIO']}
    
    signals = []
    for i in range(len(df)):
        if pd.notna(df.iloc[i]['VOLUME_RATIO']) and pd.notna(df.iloc[i]['MA20']):
            # 거래량이 평균의 2배 이상이고 가격이 20일 이평선 위
            if df.iloc[i]['VOLUME_RATIO'] > 2 and df.iloc[i]['close'] > df.iloc[i]['MA20']:
                signals.append('BUY')
            elif df.iloc[i]['close'] < df.iloc[i]['MA20'] * 0.97:  # 3% 손절
                signals.append('SELL')
            else:
                signals.append('HOLD')
        else:
            signals.append('HOLD')
    
    return signals

def main():
    """메인 실행"""
    print("="*60)
    print("실시간 백테스트 엔진")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    engine = BacktestEngine()
    engine.show()
    
    QApplication.processEvents()
    time.sleep(1)
    
    if not engine.login():
        print("로그인 필요")
        sys.exit(1)
    
    # 테스트할 종목들
    test_stocks = [
        ('005930', '삼성전자'),
        ('000660', 'SK하이닉스'),
        ('035720', '카카오')
    ]
    
    # 전략 선택
    strategies = {
        '1': ('골든크로스', golden_cross_strategy),
        '2': ('RSI', rsi_strategy),
        '3': ('거래량 돌파', volume_breakout_strategy)
    }
    
    print("\n전략 선택:")
    for key, (name, _) in strategies.items():
        print(f"  {key}. {name}")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice in strategies:
        strategy_name, strategy_func = strategies[choice]
        print(f"\n선택된 전략: {strategy_name}")
        
        results = []
        
        for code, name in test_stocks:
            print(f"\n테스트: {name}")
            result = engine.run_strategy(code, strategy_func)
            
            if result:
                results.append(result)
                print(f"  수익률: {result['returns']:.2f}%")
                
                # 매매 신호 요약
                signals = result['signals']
                buy_cnt = signals.count('BUY')
                sell_cnt = signals.count('SELL')
                print(f"  매수: {buy_cnt}회, 매도: {sell_cnt}회")
            
            time.sleep(0.5)  # API 제한
        
        # 결과 요약
        print("\n" + "="*60)
        print("백테스트 결과 요약")
        print("="*60)
        
        for result in results:
            code = result['code']
            returns = result['returns']
            print(f"{code}: {returns:.2f}%")
        
        avg_return = sum(r['returns'] for r in results) / len(results)
        print(f"\n평균 수익률: {avg_return:.2f}%")
    
    print("\n프로그램 종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()