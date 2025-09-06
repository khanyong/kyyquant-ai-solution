"""
초경량 백테스트 엔진 - 최소한의 데이터만 실시간 조회
"""
import sys
import os
import platform
from datetime import datetime, timedelta
import json

# 32비트 Python 확인
arch = platform.architecture()[0]
if arch != '32bit':
    print("[경고] 32비트 Python 필요!")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer

class LightBacktest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Light Backtest")
        self.setGeometry(100, 100, 300, 200)
        
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
        self.cache = {}  # 메모리 캐시
        
    def on_event_connect(self, err_code):
        if err_code == 0:
            print("[OK] 로그인 성공")
        self.login_loop.exit()
    
    def on_receive_tr_data(self, screen_no, rqname, trcode, recordname, 
                          prev_next, data_len, err_code, msg1, msg2):
        if "일봉" in rqname:
            self.process_data(trcode, recordname)
        
        if self.data_loop.isRunning():
            self.data_loop.exit()
    
    def process_data(self, trcode, recordname):
        """최소한의 데이터만 추출"""
        try:
            cnt = self.ocx.dynamicCall("GetRepeatCnt(QString, QString)", trcode, recordname)
            
            for i in range(cnt):
                date = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                          trcode, recordname, i, "일자").strip()
                close = self.ocx.dynamicCall("GetCommData(QString, QString, int, QString)", 
                                           trcode, recordname, i, "현재가").strip()
                
                if date and close:
                    self.price_data.append({
                        'date': date,
                        'close': abs(int(close)) if close else 0
                    })
        except:
            pass
    
    def login(self):
        """로그인 체크"""
        state = self.ocx.dynamicCall("GetConnectState()")
        if state == 1:
            print("[OK] 이미 연결됨")
            return True
        return False
    
    def get_data(self, code, days=20):
        """필요한 일수만 조회"""
        
        # 캐시 확인
        cache_key = f"{code}_{days}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        self.price_data = []
        
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", datetime.now().strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "일봉조회", "opt10081", 0, "0101")
        
        if ret == 0:
            QTimer.singleShot(2000, self.data_loop.quit)
            self.data_loop.exec_()
            
            if self.price_data:
                # 필요한 일수만 잘라서 캐시
                data = self.price_data[:days]
                self.cache[cache_key] = data
                return data
        
        return []
    
    def simple_ma_strategy(self, code):
        """단순 이동평균 전략"""
        print(f"\n테스트: {code}")
        
        # 20일치만 가져오기
        data = self.get_data(code, 20)
        
        if len(data) < 20:
            print("  데이터 부족")
            return 0
        
        # MA5, MA20 계산
        prices = [d['close'] for d in data]
        ma5 = sum(prices[-5:]) / 5
        ma20 = sum(prices) / 20
        
        # 신호 생성
        signal = "BUY" if ma5 > ma20 else "SELL"
        
        print(f"  MA5: {ma5:.0f}, MA20: {ma20:.0f} → {signal}")
        
        # 간단한 수익률 계산
        if signal == "BUY":
            return (prices[-1] - prices[-5]) / prices[-5] * 100
        else:
            return 0
    
    def momentum_strategy(self, code):
        """모멘텀 전략"""
        print(f"\n테스트: {code}")
        
        # 10일치만 가져오기
        data = self.get_data(code, 10)
        
        if len(data) < 10:
            print("  데이터 부족")
            return 0
        
        prices = [d['close'] for d in data]
        
        # 10일 모멘텀
        momentum = (prices[-1] - prices[0]) / prices[0] * 100
        
        # 신호 생성
        signal = "BUY" if momentum > 5 else ("SELL" if momentum < -5 else "HOLD")
        
        print(f"  10일 수익률: {momentum:.2f}% → {signal}")
        
        return momentum if signal == "BUY" else 0

def main():
    """실행"""
    print("="*60)
    print("초경량 백테스트 (실시간 조회)")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    engine = LightBacktest()
    engine.show()
    
    QApplication.processEvents()
    
    if not engine.login():
        print("로그인 필요")
        sys.exit(1)
    
    # 테스트 종목 (소수만)
    test_stocks = [
        '005930',  # 삼성전자
        '000660',  # SK하이닉스
        '035720',  # 카카오
        '035420',  # NAVER
        '051910'   # LG화학
    ]
    
    print("\n전략 선택:")
    print("  1. 단순 이동평균")
    print("  2. 모멘텀")
    
    choice = input("선택 (1-2): ").strip()
    
    results = []
    
    if choice == '1':
        print("\n[단순 이동평균 전략]")
        for code in test_stocks:
            ret = engine.simple_ma_strategy(code)
            results.append(ret)
    elif choice == '2':
        print("\n[모멘텀 전략]")
        for code in test_stocks:
            ret = engine.momentum_strategy(code)
            results.append(ret)
    
    # 결과
    print("\n" + "="*60)
    print("백테스트 결과")
    print("="*60)
    
    for i, code in enumerate(test_stocks):
        print(f"{code}: {results[i]:.2f}%")
    
    avg = sum(results) / len(results)
    print(f"\n평균: {avg:.2f}%")
    
    print("\n종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()