"""
전체 종목 데이터 수집 (KOSPI + KOSDAQ)
"""
import sys
import os
from pathlib import Path
from datetime import datetime
import time
import json

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

class AllStockCollector:
    def __init__(self):
        print("\n" + "="*50)
        print("🚀 전체 종목 데이터 수집")
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
        
        # 연결 확인
        if self.kiwoom.GetConnectState() == 0:
            print("⚠️ 연결 중...")
            self.kiwoom.CommConnect()
            time.sleep(2)
        else:
            print("✅ 이미 연결됨")
        
        self.snapshot_date = datetime.now().strftime("%Y-%m-%d")
        self.snapshot_time = datetime.now().strftime("%H:%M:%S")
        
        # 진행 상황 파일
        self.progress_file = f"collection_progress_{self.snapshot_date}.json"
        
    def get_all_stock_codes(self):
        """전체 종목 코드 조회"""
        print("\n📊 전체 종목 리스트 조회 중...")
        
        # KOSPI
        kospi_codes = self.kiwoom.GetCodeListByMarket("0")
        print(f"  KOSPI: {len(kospi_codes)}개")
        
        # KOSDAQ
        kosdaq_codes = self.kiwoom.GetCodeListByMarket("10")
        print(f"  KOSDAQ: {len(kosdaq_codes)}개")
        
        all_codes = []
        
        # KOSPI 종목 필터링 (ETF, 스팩 제외)
        for code in kospi_codes:
            name = self.kiwoom.GetMasterCodeName(code)
            if name and not any(exc in name.upper() for exc in ['KODEX', 'TIGER', 'KBSTAR', 'ARIRANG', '스팩', 'ETF', 'ETN']):
                all_codes.append((code, name, 'KOSPI'))
        
        # KOSDAQ 종목 필터링
        for code in kosdaq_codes:
            name = self.kiwoom.GetMasterCodeName(code)
            if name and not any(exc in name.upper() for exc in ['KODEX', 'TIGER', 'KBSTAR', 'ARIRANG', '스팩', 'ETF', 'ETN']):
                all_codes.append((code, name, 'KOSDAQ'))
        
        print(f"\n✅ 총 {len(all_codes)}개 종목 (ETF/스팩 제외)")
        return all_codes
    
    def load_progress(self):
        """이전 진행 상황 불러오기"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {'completed': [], 'failed': [], 'last_index': 0}
    
    def save_progress(self, progress):
        """진행 상황 저장"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f)
    
    def collect_stock_data(self, code, name, market):
        """개별 종목 데이터 수집"""
        try:
            # opt10001 - 주식기본정보
            df = self.kiwoom.block_request("opt10001",
                종목코드=code,
                output="주식기본정보",
                next=0
            )
            
            if df is not None and not df.empty:
                data = df.iloc[0]
                
                # 데이터 추출 (빈 문자열 처리)
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
                    'market_cap': safe_int(data.get('시가총액', 0)),  # 억원
                    'shares_outstanding': safe_int(data.get('상장주식', 0)) * 1000,  # 천주->주
                    'per': safe_float(data.get('PER', 0)),
                    'pbr': safe_float(data.get('PBR', 0)),
                    'eps': safe_int(data.get('EPS', 0)),
                    'bps': safe_int(data.get('BPS', 0)),
                    'roe': safe_float(data.get('ROE', 0)),
                    'current_price': safe_int(data.get('현재가', 0)),
                    'change_rate': safe_float(data.get('등락율', 0)),
                    'high_52w': safe_int(data.get('250최고', 0)),
                    'low_52w': safe_int(data.get('250최저', 0)),
                    'volume': safe_int(data.get('거래량', 0)),
                    'foreign_ratio': safe_float(data.get('외인소진률', 0)),
                    'created_at': datetime.now().isoformat()
                }
                
                # Supabase 저장
                self.supabase.table('kw_financial_snapshot').insert(result).execute()
                return True
                
        except Exception as e:
            print(f"    ❌ 오류: {str(e)[:50]}")
            return False
    
    def collect_all(self, limit=None, resume=False):
        """전체 종목 수집"""
        # 종목 리스트
        all_stocks = self.get_all_stock_codes()
        
        if limit:
            all_stocks = all_stocks[:limit]
            print(f"📌 테스트 모드: {limit}개만 수집")
        
        # 진행 상황
        progress = self.load_progress() if resume else {'completed': [], 'failed': [], 'last_index': 0}
        start_index = progress['last_index'] if resume else 0
        
        print(f"\n{'='*50}")
        print(f"📊 데이터 수집 시작")
        if resume:
            print(f"📌 이어서 진행 (완료: {len(progress['completed'])}개)")
        print(f"{'='*50}\n")
        
        success_count = len(progress['completed'])
        fail_count = len(progress['failed'])
        
        # 수집 시작
        for i in range(start_index, len(all_stocks)):
            code, name, market = all_stocks[i]
            
            # 이미 처리된 종목 스킵
            if code in progress['completed'] or code in progress['failed']:
                continue
            
            # 진행률 표시
            percent = (i + 1) / len(all_stocks) * 100
            print(f"[{i+1}/{len(all_stocks)}] {percent:.1f}% - {code} {name[:10]}", end="")
            
            # 데이터 수집
            if self.collect_stock_data(code, name, market):
                success_count += 1
                progress['completed'].append(code)
                print(f" ✅ (총 {success_count}개 완료)")
            else:
                fail_count += 1
                progress['failed'].append(code)
                print(f" ❌ (총 {fail_count}개 실패)")
            
            # 진행 상황 저장
            progress['last_index'] = i + 1
            if (i + 1) % 10 == 0:  # 10개마다 저장
                self.save_progress(progress)
            
            # API 제한 대기 (초당 5회)
            time.sleep(0.2)
            
            # 100개마다 휴식
            if (i + 1) % 100 == 0:
                print(f"\n⏸️ 100개 완료. 3초 대기...")
                time.sleep(3)
                print()
        
        # 최종 저장
        self.save_progress(progress)
        
        # 결과 출력
        print(f"\n{'='*50}")
        print(f"📊 수집 완료!")
        print(f"✅ 성공: {success_count}개")
        print(f"❌ 실패: {fail_count}개")
        print(f"📅 수집 시점: {self.snapshot_date} {self.snapshot_time}")
        print(f"💾 진행 파일: {self.progress_file}")
        print(f"{'='*50}")
        
        # Supabase 로그 저장
        log_data = {
            'snapshot_date': self.snapshot_date,
            'snapshot_time': self.snapshot_time,
            'total_stocks': len(all_stocks),
            'success_count': success_count,
            'fail_count': fail_count,
            'completed_at': datetime.now().isoformat()
        }
        
        try:
            # kw_collection_log 테이블이 있다면 저장
            self.supabase.table('kw_collection_log').insert(log_data).execute()
        except:
            pass

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='전체 종목 데이터 수집')
    parser.add_argument('--limit', type=int, help='수집할 종목 수 제한')
    parser.add_argument('--resume', action='store_true', help='이전 작업 이어서 진행')
    
    args = parser.parse_args()
    
    try:
        collector = AllStockCollector()
        collector.collect_all(limit=args.limit, resume=args.resume)
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자 중단. 진행 상황이 저장되었습니다.")
        print("--resume 옵션으로 이어서 진행할 수 있습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
    finally:
        sys.exit(0)