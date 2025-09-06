"""
키움 OpenAPI+ 모든 데이터 수집 및 Supabase 저장
실행 가능한 최종 통합 스크립트
"""
import sys
import os
from datetime import datetime, timedelta
import time
import json
from PyQt5.QWidgets import QApplication
from pykiwoom.kiwoom import Kiwoom
import pandas as pd
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.kiwoom_openapi import KiwoomOpenAPI
from core.supabase_client import get_supabase_client

class CompleteDataCollector:
    """모든 키움 데이터 수집 및 저장"""
    
    def __init__(self):
        # PyQt5 앱 생성
        self.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        self.kiwoom = Kiwoom()
        self.kiwoom_api = KiwoomOpenAPI()
        self.supabase = get_supabase_client()
        self.connected = False
        
    def connect(self):
        """키움 API 연결"""
        try:
            print("키움증권 OpenAPI+ 연결 중...")
            self.kiwoom.CommConnect()
            
            # 연결 확인
            for i in range(30):
                if self.kiwoom.GetConnectState() == 1:
                    self.connected = True
                    print("✅ 키움 API 연결 성공!")
                    
                    # KiwoomOpenAPI도 연결
                    self.kiwoom_api.connect()
                    return True
                time.sleep(1)
                
            print("❌ 키움 API 연결 실패")
            return False
            
        except Exception as e:
            print(f"❌ 연결 오류: {e}")
            return False
    
    def collect_all_for_stock(self, stock_code: str):
        """
        한 종목의 모든 데이터 수집 및 저장
        """
        stock_name = self.kiwoom.GetMasterCodeName(stock_code)
        print(f"\n{'='*60}")
        print(f"{stock_name} ({stock_code}) 데이터 수집")
        print(f"{'='*60}")
        
        success_count = 0
        fail_count = 0
        
        # 1. 종목 마스터 정보 저장
        try:
            print("1. 종목 기본정보...")
            master_data = {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'market': self._get_market(stock_code),
                'updated_at': datetime.now().isoformat()
            }
            self.supabase.table('stock_master').upsert(master_data).execute()
            print("   ✅ 저장 완료")
            success_count += 1
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            fail_count += 1
        
        # 2. 일봉 데이터 (10년)
        try:
            print("2. 일봉 데이터 (10년)...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3650)
            
            df = self.kiwoom_api.get_ohlcv(
                stock_code,
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
            
            if df is not None and not df.empty:
                # 데이터 저장
                records = []
                for date, row in df.iterrows():
                    record = {
                        'stock_code': stock_code,
                        'date': date.strftime('%Y-%m-%d'),
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': int(row['volume']),
                        'trading_value': int(row.get('trading_value', 0))
                    }
                    records.append(record)
                
                # 배치로 저장 (100개씩)
                for i in range(0, len(records), 100):
                    batch = records[i:i+100]
                    self.supabase.table('price_data').upsert(batch).execute()
                
                print(f"   ✅ {len(df)}개 레코드 저장")
                success_count += 1
            else:
                print("   ⚠️  데이터 없음")
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            fail_count += 1
        
        # 3. 주봉 데이터
        try:
            print("3. 주봉 데이터...")
            df = self.kiwoom.block_request("opt10082",
                종목코드=stock_code,
                기준일자=end_date.strftime('%Y%m%d'),
                수정주가구분=1,
                output="주식주봉차트조회",
                next=0)
            
            if df is not None and not df.empty:
                records = []
                for _, row in df.iterrows():
                    record = {
                        'stock_code': stock_code,
                        'week_date': row['일자'],
                        'open': abs(int(row.get('시가', 0))),
                        'high': abs(int(row.get('고가', 0))),
                        'low': abs(int(row.get('저가', 0))),
                        'close': abs(int(row.get('현재가', 0))),
                        'volume': int(row.get('거래량', 0))
                    }
                    records.append(record)
                
                # 저장
                for i in range(0, len(records), 100):
                    batch = records[i:i+100]
                    self.supabase.table('price_data_weekly').upsert(batch).execute()
                
                print(f"   ✅ {len(df)}개 주봉 저장")
                success_count += 1
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            fail_count += 1
        
        # 4. 재무제표 및 재무비율
        try:
            print("4. 재무제표...")
            df = self.kiwoom.block_request("opt10001",
                종목코드=stock_code,
                output="주식기본정보",
                next=0)
            
            if df is not None and not df.empty:
                ratios = {
                    'stock_code': stock_code,
                    'per': float(df.get('PER', [0])[0]) if df.get('PER', [0])[0] else None,
                    'pbr': float(df.get('PBR', [0])[0]) if df.get('PBR', [0])[0] else None,
                    'eps': int(df.get('EPS', [0])[0]) if df.get('EPS', [0])[0] else None,
                    'bps': int(df.get('BPS', [0])[0]) if df.get('BPS', [0])[0] else None,
                    'roe': float(df.get('ROE', [0])[0]) if df.get('ROE', [0])[0] else None,
                    'dividend_yield': float(df.get('시가배당률', [0])[0]) if df.get('시가배당률', [0])[0] else None,
                    'updated_at': datetime.now().isoformat()
                }
                
                self.supabase.table('financial_ratios').upsert(ratios).execute()
                print("   ✅ 재무비율 저장")
                success_count += 1
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            fail_count += 1
        
        # 5. 투자자별 매매동향 (최근 60일)
        try:
            print("5. 투자자별 매매...")
            df = self.kiwoom.block_request("opt10059",
                일자="",
                종목코드=stock_code,
                금액수량구분=2,  # 수량
                매매구분=0,  # 순매수
                단위구분=1000,  # 천주
                output="투자자별매매",
                next=0)
            
            if df is not None and not df.empty:
                records = []
                for _, row in df.head(60).iterrows():
                    record = {
                        'stock_code': stock_code,
                        'trading_date': row.get('일자', ''),
                        'individual_net': int(row.get('개인', 0)) * 1000,
                        'foreign_net': int(row.get('외국인', 0)) * 1000,
                        'institution_net': int(row.get('기관', 0)) * 1000
                    }
                    records.append(record)
                
                # 저장
                for record in records:
                    self.supabase.table('investor_trading').upsert(record).execute()
                
                print(f"   ✅ {len(records)}일 매매동향 저장")
                success_count += 1
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            fail_count += 1
        
        # 6. 실시간 현재가
        try:
            print("6. 현재가 정보...")
            current = self.kiwoom_api.get_current_price(stock_code)
            
            if current:
                realtime = {
                    'stock_code': stock_code,
                    'current_price': current.get('current_price'),
                    'change_price': current.get('change'),
                    'change_rate': current.get('change_rate'),
                    'volume': current.get('volume'),
                    'updated_at': datetime.now().isoformat()
                }
                
                self.supabase.table('realtime_price').upsert(realtime).execute()
                print("   ✅ 현재가 저장")
                success_count += 1
        except Exception as e:
            print(f"   ❌ 실패: {e}")
            fail_count += 1
        
        # 결과 요약
        print(f"\n종목 수집 완료: 성공 {success_count}, 실패 {fail_count}")
        
        return success_count > 0
    
    def _get_market(self, stock_code: str) -> str:
        """종목이 속한 시장 구분"""
        kospi = self.kiwoom.GetCodeListByMarket('0')
        if stock_code in kospi:
            return 'KOSPI'
        return 'KOSDAQ'
    
    def collect_all_stocks(self):
        """
        모든 종목 데이터 수집
        """
        print("\n" + "="*70)
        print("전체 종목 데이터 수집 시작")
        print("="*70)
        
        # 전체 종목 리스트
        kospi = self.kiwoom.GetCodeListByMarket('0').split(';')[:-1]
        kosdaq = self.kiwoom.GetCodeListByMarket('10').split(';')[:-1]
        
        all_codes = []
        
        # ETF, 스팩 제외
        for code in kospi + kosdaq:
            if code:
                name = self.kiwoom.GetMasterCodeName(code)
                if name and not any(x in name for x in ['ETF', 'ETN', '스팩', '리츠']):
                    all_codes.append(code)
        
        total = len(all_codes)
        print(f"\n총 {total}개 종목 수집 예정")
        
        # 진행상황 파일
        progress_file = 'collection_progress.txt'
        
        # 이전 진행상황 확인
        start_idx = 0
        if os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                last_code = f.read().strip()
                try:
                    start_idx = all_codes.index(last_code) + 1
                    print(f"이전 진행: {last_code} 완료 ({start_idx}/{total})")
                except:
                    pass
        
        # 수집 시작
        success = 0
        fail = 0
        
        for i in range(start_idx, total):
            code = all_codes[i]
            progress = ((i+1) / total) * 100
            
            print(f"\n[{i+1}/{total}] ({progress:.1f}%)")
            
            try:
                if self.collect_all_for_stock(code):
                    success += 1
                else:
                    fail += 1
                
                # 진행상황 저장
                with open(progress_file, 'w') as f:
                    f.write(code)
                
                # API 제한 대기
                time.sleep(1)
                
                # 50개마다 휴식
                if (i+1) % 50 == 0:
                    print("\n30초 휴식 (API 제한)...")
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                print("\n\n중단됨! 다시 실행하면 이어서 진행됩니다.")
                break
            except Exception as e:
                print(f"오류: {e}")
                fail += 1
        
        # 완료
        if i >= total - 1:
            if os.path.exists(progress_file):
                os.remove(progress_file)
        
        # 최종 결과
        print("\n" + "="*70)
        print("수집 완료!")
        print("="*70)
        print(f"성공: {success}개 종목")
        print(f"실패: {fail}개 종목")
        
        # DB 통계
        self.show_statistics()
    
    def show_statistics(self):
        """데이터베이스 통계"""
        print("\n" + "="*70)
        print("데이터베이스 현황")
        print("="*70)
        
        tables = [
            'stock_master',
            'price_data',
            'price_data_weekly',
            'financial_ratios',
            'investor_trading',
            'realtime_price'
        ]
        
        for table in tables:
            try:
                result = self.supabase.table(table).select('count', count='exact').execute()
                count = result.count if result else 0
                print(f"{table:20s}: {count:,}개")
            except:
                print(f"{table:20s}: 테이블 없음")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='키움 전체 데이터 수집')
    parser.add_argument('--stock', type=str, help='특정 종목만')
    parser.add_argument('--all', action='store_true', help='전체 종목')
    parser.add_argument('--stats', action='store_true', help='통계만')
    
    args = parser.parse_args()
    
    collector = CompleteDataCollector()
    
    if args.stats:
        collector.show_statistics()
    elif args.stock:
        if collector.connect():
            collector.collect_all_for_stock(args.stock)
            collector.show_statistics()
    elif args.all:
        print("\n⚠️  전체 종목 수집 (약 2000개)")
        print("예상 시간: 3-4시간")
        print("중단 시 자동으로 이어서 진행됩니다.")
        
        response = input("\n시작하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            if collector.connect():
                collector.collect_all_stocks()
    else:
        print("\n사용법:")
        print("  특정 종목: python collect_all_data.py --stock 005930")
        print("  전체 종목: python collect_all_data.py --all")
        print("  통계 확인: python collect_all_data.py --stats")