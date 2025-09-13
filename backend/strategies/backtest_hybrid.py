"""
하이브리드 백테스트 엔진 - 로컬 캐시 + Supabase
"""
import sys
import os
import platform
import csv
from datetime import datetime, timedelta
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

load_dotenv()

class HybridBacktest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hybrid Backtest")
        self.setGeometry(100, 100, 400, 300)
        
        # Supabase 연결
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
        # 로컬 캐시 디렉토리
        self.cache_dir = "D:/Dev/auto_stock/data/cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
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
    
    def get_stock_data(self, code, days=60):
        """3단계 데이터 조회"""
        print(f"\n조회: {code}")
        
        # 1단계: 로컬 캐시 확인
        local_data = self.check_local_cache(code, days)
        if local_data:
            print(f"  ✓ 로컬 캐시 사용")
            return local_data
        
        # 2단계: Supabase 확인
        supabase_data = self.check_supabase(code, days)
        if supabase_data:
            print(f"  ✓ Supabase 사용")
            # 로컬에도 저장
            self.save_to_local(code, supabase_data)
            return supabase_data
        
        # 3단계: 키움 실시간 조회
        print(f"  ✓ 키움 실시간 조회")
        kiwoom_data = self.fetch_from_kiwoom(code, days)
        
        if kiwoom_data:
            # 로컬 저장
            self.save_to_local(code, kiwoom_data)
            # Supabase 저장 (비동기)
            self.save_to_supabase(code, kiwoom_data)
            
        return kiwoom_data
    
    def check_local_cache(self, code, days):
        """로컬 캐시 확인"""
        cache_file = f"{self.cache_dir}/{code}_{days}d.csv"
        
        if os.path.exists(cache_file):
            # 파일 수정 시간 확인 (1일 이내면 사용)
            file_time = os.path.getmtime(cache_file)
            if (datetime.now().timestamp() - file_time) < 86400:  # 24시간
                data = []
                with open(cache_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        row['open'] = int(row['open'])
                        row['high'] = int(row['high'])
                        row['low'] = int(row['low'])
                        row['close'] = int(row['close'])
                        row['volume'] = int(row['volume'])
                        data.append(row)
                return data
        
        return None
    
    def check_supabase(self, code, days):
        """Supabase 확인"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            response = self.supabase.table('kw_daily_prices').select('*').eq(
                'stock_code', code
            ).gte(
                'date', start_date.strftime('%Y-%m-%d')
            ).order('date', desc=True).limit(days).execute()
            
            if response.data and len(response.data) >= days * 0.8:
                # 포맷 변환
                data = []
                for item in response.data:
                    data.append({
                        'date': item['date'].replace('-', ''),
                        'open': item['open'],
                        'high': item['high'],
                        'low': item['low'],
                        'close': item['close'],
                        'volume': item['volume']
                    })
                return data
                
        except Exception as e:
            print(f"  Supabase 오류: {e}")
        
        return None
    
    def fetch_from_kiwoom(self, code, days):
        """키움 실시간 조회"""
        self.price_data = []
        
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "기준일자", 
                           datetime.now().strftime("%Y%m%d"))
        self.ocx.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        
        ret = self.ocx.dynamicCall("CommRqData(QString, QString, int, QString)",
                                  "일봉조회", "opt10081", 0, "0101")
        
        if ret == 0:
            QTimer.singleShot(3000, self.data_loop.quit)
            self.data_loop.exec_()
            
            if self.price_data:
                return self.price_data[:days]
        
        return []
    
    def save_to_local(self, code, data):
        """로컬 캐시 저장"""
        try:
            days = len(data)
            cache_file = f"{self.cache_dir}/{code}_{days}d.csv"
            
            with open(cache_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['date', 'open', 'high', 'low', 'close', 'volume'])
                writer.writeheader()
                writer.writerows(data)
            
            print(f"  → 로컬 저장: {cache_file}")
            
        except Exception as e:
            print(f"  로컬 저장 실패: {e}")
    
    def save_to_supabase(self, code, data):
        """Supabase 저장 (백그라운드)"""
        try:
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
            
            print(f"  → Supabase 저장 완료")
            
        except Exception as e:
            print(f"  Supabase 저장 실패: {e}")

def main():
    """메인 실행"""
    print("="*60)
    print("하이브리드 백테스트 (로컬+Supabase)")
    print("="*60)
    print("\n데이터 우선순위:")
    print("  1. 로컬 캐시 (24시간 이내)")
    print("  2. Supabase")
    print("  3. 키움 실시간")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    engine = HybridBacktest()
    engine.show()
    
    QApplication.processEvents()
    
    if not engine.login():
        print("로그인 필요")
        sys.exit(1)
    
    # 테스트
    test_stocks = ['005930', '000660', '035720']
    
    for code in test_stocks:
        data = engine.get_stock_data(code, 60)
        if data:
            print(f"  데이터: {len(data)}일")
    
    print("\n캐시 디렉토리:", engine.cache_dir)
    print("종료...")
    sys.exit(0)

if __name__ == "__main__":
    main()