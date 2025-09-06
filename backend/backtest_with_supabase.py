"""
Supabase 연동 백테스트 엔진
- 실시간 조회 + Supabase 캐싱
- 백테스트 결과 저장
"""
import sys
import os
import platform
from datetime import datetime, timedelta
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# 32비트 Python 확인
arch = platform.architecture()[0]
if arch != '32bit':
    print("[경고] 32비트 Python 필요!")
    sys.exit(1)

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop, QTimer

# 환경 변수 로드
load_dotenv()

class SupabaseBacktest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Supabase Backtest Engine")
        self.setGeometry(100, 100, 400, 300)
        
        # Supabase 연결
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
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
        """가격 데이터 처리"""
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
    
    def login(self):
        """로그인"""
        state = self.ocx.dynamicCall("GetConnectState()")
        if state == 1:
            print("[OK] 이미 연결됨")
            return True
        return False
    
    def get_stock_data_from_supabase(self, code, days=60):
        """Supabase에서 먼저 조회"""
        try:
            # 최근 날짜 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Supabase 조회
            response = self.supabase.table('kw_daily_prices').select('*').eq(
                'stock_code', code
            ).gte(
                'date', start_date.strftime('%Y-%m-%d')
            ).order('date', desc=True).limit(days).execute()
            
            if response.data and len(response.data) >= days * 0.8:  # 80% 이상 데이터가 있으면 사용
                print(f"  Supabase에서 로드: {code} ({len(response.data)}일)")
                return response.data
            else:
                print(f"  Supabase 데이터 부족: {code}")
                return None
                
        except Exception as e:
            print(f"  Supabase 오류: {e}")
            return None
    
    def get_stock_data_from_kiwoom(self, code, days=60):
        """키움에서 실시간 조회"""
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
                data = self.price_data[:days]
                
                # Supabase에 저장 (백그라운드)
                self.save_to_supabase(code, data)
                
                return data
        
        return []
    
    def save_to_supabase(self, code, data):
        """Supabase에 데이터 저장"""
        try:
            # 종목 정보 저장/업데이트
            name = self.ocx.dynamicCall("GetMasterCodeName(QString)", code)
            
            self.supabase.table('kw_stocks').upsert({
                'code': code,
                'name': name,
                'market': 'KOSPI' if code in self.get_kospi_codes() else 'KOSDAQ',
                'updated_at': datetime.now().isoformat()
            }).execute()
            
            # 가격 데이터 저장
            for item in data:
                self.supabase.table('kw_daily_prices').upsert({
                    'stock_code': code,
                    'date': f"{item['date'][:4]}-{item['date'][4:6]}-{item['date'][6:8]}",
                    'open': item['open'],
                    'high': item['high'],
                    'low': item['low'],
                    'close': item['close'],
                    'volume': item['volume']
                }).execute()
                
            print(f"  Supabase 저장 완료: {code}")
            
        except Exception as e:
            print(f"  Supabase 저장 실패: {e}")
    
    def get_kospi_codes(self):
        """KOSPI 종목 코드 리스트"""
        kospi = self.ocx.dynamicCall("GetCodeListByMarket(QString)", "0")
        return kospi.split(';')[:-1]
    
    def get_stock_data(self, code, days=60):
        """데이터 조회 (Supabase 우선, 없으면 키움)"""
        
        # 1. Supabase에서 먼저 조회
        data = self.get_stock_data_from_supabase(code, days)
        
        # 2. Supabase에 없으면 키움에서 실시간 조회
        if data is None:
            print(f"  키움 실시간 조회: {code}")
            data = self.get_stock_data_from_kiwoom(code, days)
        
        return data
    
    def run_backtest(self, strategy_name, strategy_func, stock_codes):
        """백테스트 실행 및 결과 저장"""
        results = []
        
        for code in stock_codes:
            print(f"\n백테스트: {code}")
            
            # 데이터 조회
            data = self.get_stock_data(code, 60)
            
            if data:
                # 전략 실행
                signals, returns = strategy_func(data)
                
                results.append({
                    'code': code,
                    'returns': returns,
                    'signals': len([s for s in signals if s == 'BUY'])
                })
                
                # 백테스트 결과 Supabase에 저장
                self.save_backtest_result(code, strategy_name, returns, signals)
                
                print(f"  수익률: {returns:.2f}%")
        
        return results
    
    def save_backtest_result(self, code, strategy_name, returns, signals):
        """백테스트 결과 Supabase 저장"""
        try:
            buy_count = len([s for s in signals if s == 'BUY'])
            sell_count = len([s for s in signals if s == 'SELL'])
            
            self.supabase.table('kw_backtest_results').insert({
                'stock_code': code,
                'strategy_name': strategy_name,
                'returns': returns,
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'test_date': datetime.now().isoformat(),
                'parameters': {
                    'days': 60,
                    'type': 'realtime'
                }
            }).execute()
            
        except Exception as e:
            print(f"  결과 저장 실패: {e}")

def simple_ma_strategy(data):
    """단순 이동평균 전략"""
    signals = []
    
    if len(data) < 20:
        return signals, 0
    
    # 데이터를 리스트로 변환
    prices = [d['close'] for d in data]
    
    for i in range(20, len(data)):
        ma5 = sum(prices[i-5:i]) / 5
        ma20 = sum(prices[i-20:i]) / 20
        
        if ma5 > ma20 * 1.01:  # 1% 이상 위
            signals.append('BUY')
        elif ma5 < ma20 * 0.99:  # 1% 이하
            signals.append('SELL')
        else:
            signals.append('HOLD')
    
    # 수익률 계산
    total_return = 0
    position = 0
    entry_price = 0
    
    for i, signal in enumerate(signals):
        if signal == 'BUY' and position == 0:
            entry_price = prices[20+i]
            position = 1
        elif signal == 'SELL' and position == 1:
            exit_price = prices[20+i]
            total_return += (exit_price - entry_price) / entry_price
            position = 0
    
    return signals, total_return * 100

def main():
    """메인 실행"""
    print("="*60)
    print("Supabase 연동 백테스트")
    print("="*60)
    print("\n특징:")
    print("  1. Supabase에 캐시된 데이터 우선 사용")
    print("  2. 없는 데이터만 키움에서 실시간 조회")
    print("  3. 백테스트 결과 Supabase에 저장")
    print("  4. 다음 실행시 더 빠른 속도")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    engine = SupabaseBacktest()
    engine.show()
    
    QApplication.processEvents()
    
    if not engine.login():
        print("로그인 필요")
        sys.exit(1)
    
    # 테스트 종목
    test_stocks = ['005930', '000660', '035720']  # 삼성전자, SK하이닉스, 카카오
    
    # 백테스트 실행
    results = engine.run_backtest("Simple MA", simple_ma_strategy, test_stocks)
    
    # 결과 요약
    print("\n" + "="*60)
    print("백테스트 결과 (Supabase 저장완료)")
    print("="*60)
    
    for result in results:
        print(f"{result['code']}: {result['returns']:.2f}% (매수신호 {result['signals']}회)")
    
    avg_return = sum(r['returns'] for r in results) / len(results)
    print(f"\n평균 수익률: {avg_return:.2f}%")
    
    print("\n종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()