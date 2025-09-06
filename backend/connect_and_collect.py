"""
키움 OpenAPI 연결 후 데이터 수집
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

# Supabase
from supabase import create_client

# PyQt5
try:
    from PyQt5.QWidgets import QApplication
    from PyQt5.QtCore import QEventLoop
except ImportError:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QEventLoop

# pykiwoom
from pykiwoom.kiwoom import Kiwoom

class KiwoomConnector:
    def __init__(self):
        print("\n" + "="*50)
        print("🚀 키움 OpenAPI 연결 및 데이터 수집")
        print("="*50)
        
        # Supabase 연결
        print("📡 Supabase 연결...", end="", flush=True)
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        print(" ✅")
        
        # PyQt 앱 초기화
        print("🖥️ PyQt 초기화...", end="", flush=True)
        self.app = QApplication.instance() or QApplication(sys.argv)
        print(" ✅")
        
        # 키움 객체 생성
        print("📈 키움 OpenAPI 초기화...", end="", flush=True)
        self.kiwoom = Kiwoom()
        print(" ✅")
        
        # 연결 상태 확인
        print("\n연결 상태 확인...", end="", flush=True)
        state = self.kiwoom.GetConnectState()
        print(f" 상태 코드: {state}")
        
        if state == 0:
            print("⚠️ 미연결 상태입니다. 연결을 시작합니다...")
            print("📌 로그인 창이 나타나면 로그인해주세요.")
            
            # 연결 시작
            self.kiwoom.CommConnect()
            
            # 연결 완료 대기 (최대 30초)
            for i in range(30):
                time.sleep(1)
                state = self.kiwoom.GetConnectState()
                if state == 1:
                    print(f"\n✅ 연결 성공! (대기 시간: {i+1}초)")
                    break
                else:
                    print(f".", end="", flush=True)
            else:
                print("\n❌ 연결 시간 초과 (30초)")
                sys.exit(1)
        else:
            print("✅ 이미 연결되어 있습니다!")
        
        self.snapshot_date = datetime.now().strftime("%Y-%m-%d")
        self.snapshot_time = datetime.now().strftime("%H:%M:%S")
        
        print("\n" + "-"*50)
        print(f"📅 데이터 수집 시작: {self.snapshot_date} {self.snapshot_time}")
        print("-"*50)
    
    def collect_stock_data(self, code, name):
        """종목 데이터 수집"""
        try:
            print(f"\n[{code}] {name}")
            print("  조회 중...", end="", flush=True)
            
            # opt10001 - 주식기본정보
            df = self.kiwoom.block_request("opt10001",
                종목코드=code,
                output="주식기본정보",
                next=0
            )
            
            if df is not None and not df.empty:
                data = df.iloc[0]
                
                # 데이터 추출
                market_cap = int(data.get('시가총액', 0))  # 억원
                per = float(data.get('PER', 0))
                pbr = float(data.get('PBR', 0))
                roe = float(data.get('ROE', 0))
                current_price = abs(int(data.get('현재가', 0)))
                
                print(" 완료")
                print(f"  시가총액: {market_cap:,}억원")
                print(f"  현재가: {current_price:,}원")
                print(f"  PER: {per}, PBR: {pbr}, ROE: {roe}%")
                
                # Supabase 저장
                result = {
                    'stock_code': code,
                    'stock_name': name,
                    'snapshot_date': self.snapshot_date,
                    'snapshot_time': self.snapshot_time,
                    'market_cap': market_cap,
                    'per': per,
                    'pbr': pbr,
                    'roe': roe,
                    'current_price': current_price,
                    'change_rate': float(data.get('등락율', 0)),
                    'volume': int(data.get('거래량', 0)),
                    'created_at': datetime.now().isoformat()
                }
                
                self.supabase.table('kw_financial_snapshot').insert(result).execute()
                print(f"  ✅ DB 저장 완료")
                return True
                
            else:
                print(" ❌ 데이터 없음")
                return False
                
        except Exception as e:
            print(f" ❌ 오류: {e}")
            return False
    
    def collect_major_stocks(self):
        """주요 종목 수집"""
        stocks = [
            ('005930', '삼성전자'),
            ('000660', 'SK하이닉스'),
            ('035720', '카카오'),
            ('035420', '네이버'),
            ('005380', '현대차'),
            ('051910', 'LG화학'),
            ('006400', '삼성SDI'),
            ('003550', 'LG'),
            ('105560', 'KB금융'),
            ('055550', '신한지주'),
        ]
        
        print(f"\n📊 주요 {len(stocks)}개 종목 수집 시작")
        print("="*50)
        
        success = 0
        for code, name in stocks:
            if self.collect_stock_data(code, name):
                success += 1
            time.sleep(0.5)  # API 제한
        
        print("\n" + "="*50)
        print(f"📊 수집 완료")
        print(f"✅ 성공: {success}/{len(stocks)} 종목")
        print(f"📅 수집 시점: {self.snapshot_date} {self.snapshot_time}")
        print("="*50)

if __name__ == "__main__":
    try:
        connector = KiwoomConnector()
        connector.collect_major_stocks()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        print("\n프로그램 종료")
        sys.exit(0)