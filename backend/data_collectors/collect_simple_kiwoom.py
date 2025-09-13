"""
간단한 키움 데이터 수집 - 로그인 없이 기존 연결 사용
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

# PyQt5 - 조건부 import
try:
    from PyQt5.QWidgets import QApplication
except:
    QApplication = None

# pykiwoom
from pykiwoom.kiwoom import Kiwoom

class SimpleKiwoomCollector:
    def __init__(self, skip_login=True):
        print("\n" + "="*50)
        print("🚀 키움 데이터 수집 (간소화 버전)")
        print("="*50)
        
        # Supabase 연결
        print("📡 Supabase 연결...", end="", flush=True)
        self.supabase = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        print(" ✅")
        
        # PyQt 앱
        if QApplication:
            self.app = QApplication.instance() or QApplication(sys.argv)
        
        # 키움 연결 (로그인 건너뛰기 옵션)
        print("📈 키움 OpenAPI+ 확인...", end="", flush=True)
        self.kiwoom = Kiwoom()
        
        # 연결 상태 체크
        connect_state = self.kiwoom.GetConnectState()
        print(f" (상태: {connect_state})", end="", flush=True)
        
        if connect_state == 0:  # 미연결 상태
            if not skip_login:
                print(" 연결 중...", end="", flush=True)
                self.kiwoom.CommConnect()
                # 연결 대기
                import time
                time.sleep(2)
            else:
                print(" ⚠️ 미연결 상태! KOA Studio 로그인 필요", end="")
        else:
            print(" 연결됨", end="", flush=True)
            
        print(" ✅")
        
        self.snapshot_date = datetime.now().strftime("%Y-%m-%d")
        self.snapshot_time = datetime.now().strftime("%H:%M:%S")
        
    def collect_stock_basic(self, code):
        """종목 기본 정보만 수집"""
        try:
            # 종목명
            name = self.kiwoom.GetMasterCodeName(code)
            
            # 간단한 정보만
            print(f"\n📊 {code} - {name if name else '종목명 조회 실패'}")
            
            # 연결 상태 재확인
            if self.kiwoom.GetConnectState() == 0:
                print("  ❌ 키움 연결이 끊어짐")
                return False
            
            # opt10001 - 주식기본정보
            print("  데이터 요청 중...", end="", flush=True)
            df = self.kiwoom.block_request("opt10001",
                종목코드=code,
                output="주식기본정보",
                next=0
            )
            
            if df is not None and not df.empty:
                data = df.iloc[0]
                
                # 핵심 정보만 추출
                result = {
                    'stock_code': code,
                    'stock_name': name,
                    'snapshot_date': self.snapshot_date,
                    'market_cap': int(data.get('시가총액', 0)),  # 억원
                    'per': float(data.get('PER', 0)),
                    'pbr': float(data.get('PBR', 0)),
                    'roe': float(data.get('ROE', 0)),
                    'current_price': abs(int(data.get('현재가', 0))),
                    'created_at': datetime.now().isoformat()
                }
                
                # 출력
                print(f"  시가총액: {result['market_cap']:,}억원")
                print(f"  PER: {result['per']}, PBR: {result['pbr']}, ROE: {result['roe']}%")
                print(f"  현재가: {result['current_price']:,}원")
                
                # Supabase 저장
                self.supabase.table('kw_financial_snapshot').insert(result).execute()
                print(f"  ✅ 저장 완료")
                
                return True
                
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            return False
            
    def collect_major_stocks(self):
        """주요 종목만 수집"""
        stocks = [
            ('005930', '삼성전자'),
            ('000660', 'SK하이닉스'),
            ('035720', '카카오'),
            ('035420', '네이버'),
            ('005380', '현대차'),
        ]
        
        print(f"\n📊 주요 {len(stocks)}개 종목 수집")
        print("-"*40)
        
        success = 0
        for code, name in stocks:
            if self.collect_stock_basic(code):
                success += 1
            time.sleep(0.5)  # API 제한
            
        print("\n" + "="*50)
        print(f"✅ 완료: {success}/{len(stocks)} 종목")
        print("="*50)

if __name__ == "__main__":
    # skip_login=True로 로그인 창 방지
    collector = SimpleKiwoomCollector(skip_login=True)
    collector.collect_major_stocks()