"""
키움 OpenAPI+ 투자설정 데이터 수집
- 시가총액, PER, PBR, ROE 등 재무지표를 다운로드하여 Supabase에 저장
- 시계열 데이터로 저장하여 이력 관리
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd

# Try different import methods for compatibility
try:
    from PyQt5.QWidgets import QApplication
    from PyQt5.QtCore import QEventLoop, QTimer
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QEventLoop, QTimer
    except ImportError:
        # Fallback for direct Kiwoom API usage
        import win32com.client
        QApplication = None

# pykiwoom imports
try:
    from pykiwoom.kiwoom import Kiwoom
except ImportError:
    print("pykiwoom이 설치되어 있지 않습니다. 설치: pip install pykiwoom")
    sys.exit(1)

# Supabase imports
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경변수 로드 (상위 디렉토리의 .env 파일도 검색)
import os
from pathlib import Path

# .env 파일 찾기
env_path = Path('.env')
if not env_path.exists():
    env_path = Path('../.env')
if not env_path.exists():
    env_path = Path('D:/Dev/auto_stock/.env')

load_dotenv(env_path)

class InvestmentDataCollector:
    """투자설정 관련 데이터 수집기"""
    
    def __init__(self):
        """초기화"""
        print("\n" + "="*50)
        print("🚀 투자설정 데이터 수집기 시작...")
        print("="*50)
        
        # Supabase 연결
        print("📡 Supabase 연결 중...", end="", flush=True)
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')  # SUPABASE_KEY가 아닌 SUPABASE_ANON_KEY
        
        if not supabase_url or not supabase_key:
            print(f"\n❌ Supabase 환경변수 누락!")
            print(f"  SUPABASE_URL: {supabase_url[:30] if supabase_url else 'None'}")
            print(f"  SUPABASE_ANON_KEY: {'설정됨' if supabase_key else 'None'}")
            sys.exit(1)
            
        self.supabase: Client = create_client(supabase_url, supabase_key)
        print(" ✅")
        
        # PyQt 앱 생성 (QApplication이 있을 때만)
        if QApplication:
            print("🖥️  PyQt 초기화 중...", end="", flush=True)
            self.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
            print(" ✅")
        else:
            print("⚠️  PyQt 없이 실행 중...")
        
        # 키움 API 연결
        print("📈 키움 OpenAPI+ 연결 중...", end="", flush=True)
        self.kiwoom = Kiwoom()
        
        # 이미 연결되어 있는지 확인
        if self.kiwoom.GetConnectState() == 0:
            print(" 새로 연결...", end="", flush=True)
            self.kiwoom.CommConnect()
        else:
            print(" 이미 연결됨!", end="", flush=True)
        print(" ✅")
        
        # 데이터 수집 시점
        self.snapshot_date = datetime.now().strftime("%Y-%m-%d")
        self.snapshot_time = datetime.now().strftime("%H:%M:%S")
        
        print("\n" + "-"*50)
        print("✅ 시스템 준비 완료!")
        print(f"📅 데이터 수집 시점: {self.snapshot_date} {self.snapshot_time}")
        print("-"*50)
        
    def get_all_stocks(self) -> List[str]:
        """전체 종목 코드 조회"""
        print("\n📊 전체 종목 리스트 조회 중...")
        
        kospi = self.kiwoom.GetCodeListByMarket("0")  # KOSPI
        kosdaq = self.kiwoom.GetCodeListByMarket("10")  # KOSDAQ
        
        all_codes = []
        
        # ETF, 스팩 등 제외
        for code in kospi + kosdaq:
            name = self.kiwoom.GetMasterCodeName(code)
            if name and not any(exc in name for exc in ['KODEX', 'TIGER', 'KBSTAR', '스팩']):
                all_codes.append(code)
                
        print(f"✅ {len(all_codes)}개 종목 조회 완료")
        return all_codes
    
    def get_fundamental_data(self, code: str) -> Optional[Dict]:
        """
        종목별 재무지표 조회
        TR: opt10001 (주식기본정보)
        """
        try:
            # 주식기본정보 조회
            df = self.kiwoom.block_request("opt10001",
                종목코드=code,
                output="주식기본정보",
                next=0
            )
            
            if df is None or df.empty:
                return None
                
            # 첫 번째 행 데이터 추출
            data = df.iloc[0].to_dict()
            
            # 종목명 조회
            name = self.kiwoom.GetMasterCodeName(code)
            market = "KOSPI" if code in self.kiwoom.GetCodeListByMarket("0") else "KOSDAQ"
            
            # 1. kw_price_current 테이블용 데이터
            current_price_data = {
                'stock_code': code,
                'current_price': abs(int(data.get('현재가', 0))),
                'change_price': int(data.get('전일대비', 0)),
                'change_rate': float(data.get('등락율', 0)),
                'volume': int(data.get('거래량', 0)),
                'trading_value': int(data.get('거래대금', 0)),
                'high_52w': int(data.get('250최고', 0)),
                'low_52w': int(data.get('250최저', 0)),
                'market_cap': int(data.get('시가총액', 0)) * 100000000,  # 억원 -> 원
                'shares_outstanding': int(data.get('유통주식', 0)) * 1000,  # 천주 -> 주
                'foreign_ratio': float(data.get('외인소진률', 0)),
                'updated_at': datetime.now().isoformat()
            }
            
            # 2. kw_financial_ratio 테이블용 데이터
            financial_ratio_data = {
                'stock_code': code,
                'per': float(data.get('PER', 0)),
                'pbr': float(data.get('PBR', 0)),
                'eps': int(data.get('EPS', 0)),
                'bps': int(data.get('BPS', 0)),
                'roe': float(data.get('ROE', 0)),
                'updated_at': datetime.now().isoformat()
            }
            
            # 3. kw_financial_snapshot 테이블용 데이터 (시계열 저장)
            snapshot_data = {
                'stock_code': code,
                'stock_name': name,
                'market': market,
                'snapshot_date': self.snapshot_date,
                'snapshot_time': self.snapshot_time,
                'market_cap': int(data.get('시가총액', 0)),  # 억원 단위로 저장
                'shares_outstanding': int(data.get('유통주식', 0)) * 1000,
                'per': float(data.get('PER', 0)),
                'pbr': float(data.get('PBR', 0)),
                'eps': int(data.get('EPS', 0)),
                'bps': int(data.get('BPS', 0)),
                'roe': float(data.get('ROE', 0)),
                'high_52w': int(data.get('250최고', 0)),
                'low_52w': int(data.get('250최저', 0)),
                'current_price': abs(int(data.get('현재가', 0))),
                'change_rate': float(data.get('등락율', 0)),
                'volume': int(data.get('거래량', 0)),
                'trading_value': int(data.get('거래대금', 0)),
                'foreign_ratio': float(data.get('외인소진률', 0)),
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'current_price': current_price_data,
                'financial_ratio': financial_ratio_data,
                'snapshot': snapshot_data
            }
            
        except Exception as e:
            print(f"❌ {code} 데이터 조회 실패: {e}")
            return None
    
    def get_financial_statements(self, code: str) -> Optional[Dict]:
        """
        재무제표 데이터 조회
        TR: opt10080 (주식분석)
        """
        try:
            df = self.kiwoom.block_request("opt10080",
                종목코드=code,
                조회구분=0,  # 연간
                output="주식분석",
                next=0
            )
            
            if df is None or df.empty:
                return None
                
            # 최신 데이터 추출
            latest = df.iloc[0].to_dict()
            
            financial = {
                'stock_code': code,
                'snapshot_date': self.snapshot_date,
                'fiscal_year': latest.get('일자', ''),
                
                # 손익계산서 (억원 단위)
                'revenue': int(latest.get('매출액', 0)),
                'operating_profit': int(latest.get('영업이익', 0)),
                'net_profit': int(latest.get('당기순이익', 0)),
                
                # 이익률
                'operating_margin': float(latest.get('영업이익률', 0)),
                'net_margin': float(latest.get('순이익률', 0)),
                
                # 재무상태표 (억원 단위)
                'total_assets': int(latest.get('자산총계', 0)),
                'total_liabilities': int(latest.get('부채총계', 0)),
                'total_equity': int(latest.get('자본총계', 0)),
                
                # 안정성 지표
                'debt_ratio': float(latest.get('부채비율', 0)),
                'current_ratio': float(latest.get('유동비율', 0)),
                'quick_ratio': float(latest.get('당좌비율', 0)),
                
                # 추가 지표
                'roa': float(latest.get('ROA', 0)),
                'dividend_yield': float(latest.get('시가배당률', 0)),
                
                'created_at': datetime.now().isoformat()
            }
            
            return financial
            
        except Exception as e:
            print(f"❌ {code} 재무제표 조회 실패: {e}")
            return None
    
    def save_to_supabase(self, data: Dict, table_name: str):
        """Supabase에 데이터 저장"""
        try:
            self.supabase.table(table_name).insert(data).execute()
            return True
        except Exception as e:
            print(f"❌ 저장 실패 ({table_name}): {e}")
            return False
    
    def collect_all_data(self, limit: Optional[int] = None):
        """전체 종목 데이터 수집"""
        print("\n🔄 전체 종목 데이터 수집 시작...")
        
        # 전체 종목 조회
        all_codes = self.get_all_stocks()
        
        if limit:
            all_codes = all_codes[:limit]
            print(f"📌 테스트 모드: {limit}개 종목만 처리")
        
        success_count = 0
        fail_count = 0
        
        # 진행상황 저장
        progress_file = f"collection_progress_{self.snapshot_date}.json"
        
        for i, code in enumerate(all_codes, 1):
            print(f"\n[{i}/{len(all_codes)}] {code} 처리 중...")
            
            # 기본 재무지표 수집
            fundamental = self.get_fundamental_data(code)
            if fundamental:
                # kw_financial_snapshot 테이블에 저장 (시계열 데이터)
                if self.save_to_supabase(fundamental, 'kw_financial_snapshot'):
                    
                    # 현재 데이터도 kw_financial_ratio에 업데이트
                    current_data = {
                        'stock_code': fundamental['stock_code'],
                        'per': fundamental['per'],
                        'pbr': fundamental['pbr'],
                        'eps': fundamental['eps'],
                        'bps': fundamental['bps'],
                        'roe': fundamental['roe'],
                        'updated_at': fundamental['created_at']
                    }
                    
                    self.supabase.table('kw_financial_ratio').upsert(current_data).execute()
                    
                    # 재무제표 데이터 수집
                    financial = self.get_financial_statements(code)
                    if financial:
                        self.save_to_supabase(financial, 'kw_financial_statements_history')
                        
                        # 현재 데이터 업데이트
                        ratio_update = {
                            'stock_code': code,
                            'roa': financial['roa'],
                            'debt_ratio': financial['debt_ratio'],
                            'current_ratio': financial['current_ratio'],
                            'quick_ratio': financial['quick_ratio'],
                            'dividend_yield': financial['dividend_yield'],
                            'updated_at': financial['created_at']
                        }
                        self.supabase.table('kw_financial_ratio').upsert(ratio_update).execute()
                    
                    success_count += 1
                    print(f"✅ {fundamental['stock_name']} 저장 완료")
                else:
                    fail_count += 1
            else:
                fail_count += 1
            
            # 진행상황 저장
            progress = {
                'processed': i,
                'total': len(all_codes),
                'success': success_count,
                'fail': fail_count,
                'last_code': code,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(progress_file, 'w') as f:
                json.dump(progress, f)
            
            # API 제한 대기
            time.sleep(0.5)
        
        # 수집 완료 로그 저장
        summary = {
            'snapshot_date': self.snapshot_date,
            'snapshot_time': self.snapshot_time,
            'total_stocks': len(all_codes),
            'success_count': success_count,
            'fail_count': fail_count,
            'completed_at': datetime.now().isoformat()
        }
        
        self.save_to_supabase(summary, 'kw_collection_log')
        
        print("\n" + "="*50)
        print(f"📊 데이터 수집 완료")
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {fail_count}개")
        print(f"📅 수집 시점: {self.snapshot_date} {self.snapshot_time}")
        print("="*50)
    
    def collect_selected_stocks(self, stock_codes: List[str]):
        """선택된 종목만 데이터 수집"""
        print(f"\n{'='*50}")
        print(f"🔄 {len(stock_codes)}개 종목 데이터 수집 시작...")
        print(f"{'='*50}")
        
        success_count = 0
        fail_count = 0
        
        for i, code in enumerate(stock_codes, 1):
            print(f"\n[{i}/{len(stock_codes)}] 진행률: {i/len(stock_codes)*100:.1f}%")
            print(f"종목코드: {code}")
            
            # 종목명 먼저 조회
            name = self.kiwoom.GetMasterCodeName(code)
            print(f"종목명: {name}")
            print("수집 중: ", end="", flush=True)
            
            # 기본 재무지표 수집
            print("재무지표...", end="", flush=True)
            fundamental = self.get_fundamental_data(code)
            
            if fundamental:
                # kw_financial_snapshot 테이블에 저장 (시계열 데이터)
                print("저장...", end="", flush=True)
                if self.save_to_supabase(fundamental['snapshot'], 'kw_financial_snapshot'):
                    
                    # 현재 데이터도 kw_financial_ratio에 업데이트
                    self.supabase.table('kw_financial_ratio').upsert(
                        fundamental['financial_ratio']
                    ).execute()
                    
                    # kw_price_current에 현재가 정보 업데이트
                    self.supabase.table('kw_price_current').upsert(
                        fundamental['current_price']
                    ).execute()
                    
                    # 재무제표 데이터 수집
                    print("재무제표...", end="", flush=True)
                    financial = self.get_financial_statements(code)
                    if financial:
                        self.save_to_supabase(financial, 'kw_financial_statements_history')
                    
                    success_count += 1
                    print(f" ✅ 완료!")
                    print(f"  - 시가총액: {fundamental['snapshot']['market_cap']:,}억원")
                    print(f"  - PER: {fundamental['snapshot']['per']}")
                    print(f"  - PBR: {fundamental['snapshot']['pbr']}")
                    print(f"  - ROE: {fundamental['snapshot']['roe']}%")
                else:
                    fail_count += 1
                    print(f" ❌ 저장 실패")
            else:
                fail_count += 1
                print(f" ❌ 데이터 조회 실패")
            
            print(f"누적: 성공 {success_count}개 / 실패 {fail_count}개")
            
            # API 제한 대기
            if i < len(stock_codes):
                print("API 대기 중...", end="", flush=True)
                time.sleep(0.5)
                print(" 다음 종목 진행")
        
        print("\n" + "="*50)
        print(f"📊 주요 종목 데이터 수집 완료")
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {fail_count}개")
        print(f"📅 수집 시점: {self.snapshot_date} {self.snapshot_time}")
        print("="*50)
    
    def get_latest_snapshot_info(self):
        """최신 스냅샷 정보 조회"""
        result = self.supabase.table('kw_collection_log')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            latest = result.data[0]
            print("\n📊 최신 데이터 정보:")
            print(f"  수집일: {latest['snapshot_date']} {latest['snapshot_time']}")
            print(f"  종목수: {latest['total_stocks']}")
            print(f"  성공: {latest['success_count']}")
            print(f"  실패: {latest['fail_count']}")
            return latest
        else:
            print("❌ 수집된 데이터가 없습니다.")
            return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='키움 투자설정 데이터 수집')
    parser.add_argument('--all', action='store_true', help='전체 종목 수집')
    parser.add_argument('--limit', type=int, help='수집할 종목 수 제한')
    parser.add_argument('--info', action='store_true', help='최신 스냅샷 정보 조회')
    parser.add_argument('--major', action='store_true', help='주요 종목만 수집')
    
    args = parser.parse_args()
    
    collector = InvestmentDataCollector()
    
    if args.info:
        collector.get_latest_snapshot_info()
    elif args.major:
        # 주요 종목만 수집
        major_codes = ['005930', '000660', '035720', '035420', '005380', 
                      '051910', '006400', '003550', '105560', '055550']
        print(f"\n🎯 주요 {len(major_codes)}개 종목만 수집합니다...")
        collector.collect_selected_stocks(major_codes)
    elif args.all:
        collector.collect_all_data(limit=args.limit)
    else:
        print("\n사용법:")
        print("  python collect_investment_data.py --all          # 전체 종목 수집")
        print("  python collect_investment_data.py --all --limit 10  # 10개만 테스트")
        print("  python collect_investment_data.py --major        # 주요 종목만")
        print("  python collect_investment_data.py --info         # 최신 데이터 정보")