"""
누락된 종목 추가 수집
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import time

# 환경변수 로드
from dotenv import load_dotenv
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

from supabase import create_client
from PyQt5.QtWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom

class MissingStocksCollector:
    def __init__(self):
        print("\n" + "="*50)
        print("🔄 누락 종목 추가 수집")
        print("="*50)
        
        # Supabase 연결
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
        # PyQt 앱
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # 키움 연결
        self.kiwoom = Kiwoom()
        if self.kiwoom.GetConnectState() == 0:
            self.kiwoom.CommConnect()
            time.sleep(2)
        
        self.snapshot_date = datetime.now().strftime("%Y-%m-%d")
        self.snapshot_time = datetime.now().strftime("%H:%M:%S")
    
    def get_existing_codes(self):
        """이미 수집된 종목 코드"""
        result = self.supabase.table('kw_financial_snapshot')\
            .select('stock_code')\
            .execute()
        return set([r['stock_code'] for r in result.data])
    
    def get_all_market_codes(self):
        """전체 시장 종목 코드"""
        print("\n📊 전체 종목 리스트 조회 중...")
        
        kospi = self.kiwoom.GetCodeListByMarket("0")
        kosdaq = self.kiwoom.GetCodeListByMarket("10")
        
        all_codes = []
        
        # ETF, 스팩 등 제외
        for code in kospi + kosdaq:
            name = self.kiwoom.GetMasterCodeName(code)
            if name and not any(exc in name.upper() for exc in 
                ['KODEX', 'TIGER', 'KBSTAR', 'ARIRANG', '스팩', 'ETF', 'ETN']):
                market = 'KOSPI' if code in kospi else 'KOSDAQ'
                all_codes.append((code, name, market))
        
        return all_codes
    
    def fix_encoding(self, text):
        """인코딩 수정"""
        if not text:
            return text
        try:
            # Latin-1 → CP949
            if any(ord(c) > 127 and ord(c) < 256 for c in text):
                return text.encode('latin-1').decode('cp949')
        except:
            pass
        return text
    
    def collect_missing(self):
        """누락된 종목만 수집"""
        existing = self.get_existing_codes()
        print(f"기존 종목: {len(existing)}개")
        
        all_stocks = self.get_all_market_codes()
        print(f"전체 종목: {len(all_stocks)}개")
        
        # 누락된 종목
        missing = [(code, name, market) for code, name, market in all_stocks 
                   if code not in existing]
        print(f"누락 종목: {len(missing)}개")
        
        if not missing:
            print("✅ 모든 종목이 이미 수집되었습니다.")
            return
        
        print(f"\n누락된 {len(missing)}개 종목을 수집하시겠습니까? (y/n): ", end="")
        if input().lower() != 'y':
            return
        
        success = 0
        fail = 0
        
        for i, (code, raw_name, market) in enumerate(missing, 1):
            print(f"[{i}/{len(missing)}] {code}", end=" ")
            
            try:
                # 종목명 인코딩 수정
                name = self.fix_encoding(raw_name)
                
                # 기본 정보 조회
                df = self.kiwoom.block_request("opt10001",
                    종목코드=code,
                    output="주식기본정보",
                    next=0
                )
                
                if df is not None and not df.empty:
                    data = df.iloc[0]
                    
                    def safe_float(val, default=0):
                        try:
                            return float(val) if val and val != '' else default
                        except:
                            return default
                    
                    def safe_int(val, default=0):
                        try:
                            return abs(int(val)) if val and val != '' else default
                        except:
                            return default
                    
                    result = {
                        'stock_code': code,
                        'stock_name': name,
                        'market': market,
                        'snapshot_date': self.snapshot_date,
                        'snapshot_time': self.snapshot_time,
                        'market_cap': safe_int(data.get('시가총액', 0)),
                        'per': safe_float(data.get('PER', 0)),
                        'pbr': safe_float(data.get('PBR', 0)),
                        'eps': safe_int(data.get('EPS', 0)),
                        'bps': safe_int(data.get('BPS', 0)),
                        'roe': safe_float(data.get('ROE', 0)),
                        'current_price': safe_int(data.get('현재가', 0)),
                        'change_rate': safe_float(data.get('등락율', 0)),
                        'volume': safe_int(data.get('거래량', 0)),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    self.supabase.table('kw_financial_snapshot').insert(result).execute()
                    success += 1
                    print(f"→ {name} ✅")
                else:
                    fail += 1
                    print("❌ 데이터 없음")
                    
            except Exception as e:
                fail += 1
                print(f"❌ {str(e)[:30]}")
            
            time.sleep(0.2)  # API 제한
            
            if i % 100 == 0:
                print(f"\n  💾 {i}개 완료. 잠시 대기...")
                time.sleep(3)
        
        print(f"\n{'='*50}")
        print(f"✅ 누락 종목 수집 완료")
        print(f"  성공: {success}개")
        print(f"  실패: {fail}개")
        print(f"{'='*50}")

if __name__ == "__main__":
    collector = MissingStocksCollector()
    collector.collect_missing()