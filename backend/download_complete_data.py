"""
전체 종목의 주가 + 재무지표 통합 다운로드
모든 상장 종목의 완전한 데이터셋 구축
"""
import sys
import os
from datetime import datetime, timedelta
import time
import pandas as pd
from typing import Dict, List
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.kiwoom_openapi import KiwoomOpenAPI
from api.kiwoom_fundamental import KiwoomFundamental
from core.supabase_client import get_supabase_client
from pykiwoom import Kiwoom

class CompleteDataDownloader:
    """주가 + 재무지표 통합 다운로더"""
    
    def __init__(self):
        self.kiwoom_price = KiwoomOpenAPI()  # 주가 데이터용
        self.kiwoom_fund = KiwoomFundamental()  # 재무지표용
        self.supabase = get_supabase_client()
        self.kiwoom = Kiwoom()
        
    def connect(self):
        """키움 API 연결"""
        print("키움증권 OpenAPI+ 접속 중...")
        
        # 주가 API 연결
        if not self.kiwoom_price.connect():
            print("주가 API 연결 실패")
            return False
            
        # 재무 API 연결
        if not self.kiwoom_fund.connect():
            print("재무 API 연결 실패")
            return False
            
        print("✅ 키움 API 연결 성공")
        return True
    
    def get_all_stocks(self) -> List[Dict]:
        """전체 종목 리스트 조회"""
        print("\n전체 종목 리스트 조회 중...")
        
        # 코스피 종목
        kospi_codes = self.kiwoom.GetCodeListByMarket('0')
        kospi_list = kospi_codes.split(';')[:-1]
        
        # 코스닥 종목
        kosdaq_codes = self.kiwoom.GetCodeListByMarket('10')
        kosdaq_list = kosdaq_codes.split(';')[:-1]
        
        all_stocks = []
        
        # 종목 정보 수집
        for code in kospi_list:
            if code:
                name = self.kiwoom.GetMasterCodeName(code)
                # ETF, 스팩 등 제외
                if name and not any(x in name for x in ['ETF', 'ETN', '스팩', '리츠']):
                    all_stocks.append({
                        'code': code,
                        'name': name,
                        'market': 'KOSPI'
                    })
        
        for code in kosdaq_list:
            if code:
                name = self.kiwoom.GetMasterCodeName(code)
                if name and not any(x in name for x in ['ETF', 'ETN', '스팩', '리츠']):
                    all_stocks.append({
                        'code': code,
                        'name': name,
                        'market': 'KOSDAQ'
                    })
        
        print(f"✅ 총 {len(all_stocks)}개 종목 발견")
        print(f"   - 코스피: {len([s for s in all_stocks if s['market'] == 'KOSPI'])}개")
        print(f"   - 코스닥: {len([s for s in all_stocks if s['market'] == 'KOSDAQ'])}개")
        
        return all_stocks
    
    def download_stock_complete_data(self, stock: Dict, years: int = 10) -> Dict:
        """
        한 종목의 모든 데이터 다운로드
        
        Returns:
            {
                'price_data': DataFrame,  # 주가 데이터
                'fundamental': Dict,      # 재무지표
                'success': bool
            }
        """
        code = stock['code']
        name = stock['name']
        
        result = {
            'code': code,
            'name': name,
            'market': stock['market'],
            'price_data': None,
            'fundamental': None,
            'success': False
        }
        
        try:
            # 1. 주가 데이터 다운로드
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * years)
            
            price_df = self.kiwoom_price.get_ohlcv(
                code,
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
            
            if price_df is not None and not price_df.empty:
                result['price_data'] = price_df
                print(f"  ✅ 주가: {len(price_df)}일")
            else:
                print(f"  ❌ 주가 데이터 없음")
            
            # 2. 재무지표 다운로드
            fundamental = self.kiwoom_fund.get_fundamental_data(code)
            
            if fundamental:
                result['fundamental'] = fundamental
                print(f"  ✅ 재무: PER={fundamental.get('per', 'N/A')}, ROE={fundamental.get('roe', 'N/A')}%")
            else:
                print(f"  ❌ 재무지표 없음")
            
            # 성공 여부
            result['success'] = (result['price_data'] is not None or 
                               result['fundamental'] is not None)
            
        except Exception as e:
            print(f"  ❌ 오류: {e}")
            
        return result
    
    def save_complete_data(self, data: Dict) -> bool:
        """통합 데이터 저장"""
        try:
            code = data['code']
            
            # 1. 종목 메타데이터 저장
            stock_meta = {
                'stock_code': code,
                'stock_name': data['name'],
                'market': data['market'],
                'last_updated': datetime.now().isoformat()
            }
            self.supabase.table('stock_metadata').upsert(stock_meta).execute()
            
            # 2. 주가 데이터 저장
            if data['price_data'] is not None and not data['price_data'].empty:
                saved_count = self.kiwoom_price.save_to_supabase(
                    data['price_data'], 
                    code
                )
                print(f"    💾 주가: {saved_count}개 저장")
            
            # 3. 재무지표 저장
            if data['fundamental']:
                self.kiwoom_fund.save_to_database(data['fundamental'])
                print(f"    💾 재무지표 저장")
            
            return True
            
        except Exception as e:
            print(f"    ❌ 저장 실패: {e}")
            return False
    
    def download_all(self, years: int = 10, resume_from: str = None):
        """
        전체 종목 데이터 다운로드
        
        Args:
            years: 주가 데이터 연수
            resume_from: 재시작할 종목코드
        """
        print("\n" + "=" * 70)
        print(f"전체 종목 통합 데이터 다운로드 ({years}년)")
        print("=" * 70)
        
        # API 연결
        if not self.connect():
            return
        
        # 전체 종목 리스트
        all_stocks = self.get_all_stocks()
        
        # 진행 상황 파일
        progress_file = 'download_progress_complete.txt'
        
        # 재시작 위치 찾기
        start_idx = 0
        if resume_from:
            for i, stock in enumerate(all_stocks):
                if stock['code'] == resume_from:
                    start_idx = i
                    print(f"\n{resume_from}부터 재시작 ({start_idx}/{len(all_stocks)})")
                    break
        elif os.path.exists(progress_file):
            with open(progress_file, 'r') as f:
                last_code = f.read().strip()
                for i, stock in enumerate(all_stocks):
                    if stock['code'] == last_code:
                        start_idx = i + 1
                        print(f"\n이전 진행: {last_code} 완료 ({start_idx}/{len(all_stocks)})")
                        break
        
        # 통계
        total = len(all_stocks)
        success_price = 0
        success_fund = 0
        fail = 0
        
        print(f"\n다운로드 시작 (총 {total}개 종목)...")
        print("-" * 70)
        
        # 각 종목 처리
        for i in range(start_idx, total):
            stock = all_stocks[i]
            progress = ((i + 1) / total) * 100
            
            print(f"\n[{i+1}/{total}] ({progress:.1f}%) {stock['market']} | {stock['name']} ({stock['code']})")
            
            try:
                # 기존 데이터 확인
                existing_price = self.supabase.table('price_data')\
                    .select('count', count='exact')\
                    .eq('stock_code', stock['code'])\
                    .execute()
                
                existing_fund = self.supabase.table('fundamental_data')\
                    .select('count', count='exact')\
                    .eq('stock_code', stock['code'])\
                    .execute()
                
                # 이미 충분한 데이터가 있으면 스킵
                if (existing_price.count and existing_price.count > years * 200 and
                    existing_fund.count and existing_fund.count > 0):
                    print("  ⏭ 이미 완전한 데이터 존재 - 스킵")
                    continue
                
                # 데이터 다운로드
                data = self.download_stock_complete_data(stock, years)
                
                # 저장
                if data['success']:
                    if self.save_complete_data(data):
                        if data['price_data'] is not None:
                            success_price += 1
                        if data['fundamental']:
                            success_fund += 1
                else:
                    fail += 1
                
                # 진행 상황 저장
                with open(progress_file, 'w') as f:
                    f.write(stock['code'])
                
                # API 제한 대기
                time.sleep(0.3)
                
                # 100개마다 휴식
                if (i + 1) % 100 == 0:
                    print("\n" + "=" * 70)
                    print(f"중간 결과 ({i+1}/{total})")
                    print(f"주가 성공: {success_price} | 재무 성공: {success_fund} | 실패: {fail}")
                    print("=" * 70)
                    print("API 제한 회피를 위해 30초 대기...")
                    time.sleep(30)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  중단됨! 다시 실행하면 이어서 다운로드합니다.")
                break
                
            except Exception as e:
                print(f"  ❌ 오류: {e}")
                fail += 1
                continue
        
        # 완료 시 진행 파일 삭제
        if i >= total - 1 and os.path.exists(progress_file):
            os.remove(progress_file)
        
        # 최종 결과
        self.print_summary(success_price, success_fund, fail)
    
    def print_summary(self, success_price: int, success_fund: int, fail: int):
        """최종 요약 출력"""
        print("\n" + "=" * 70)
        print("📊 다운로드 완료!")
        print("=" * 70)
        print(f"✅ 주가 데이터: {success_price}개 종목")
        print(f"✅ 재무지표: {success_fund}개 종목")
        print(f"❌ 실패: {fail}개 종목")
        
        # DB 통계
        try:
            # 주가 데이터
            price_count = self.supabase.table('price_data')\
                .select('count', count='exact').execute()
            
            # 재무 데이터
            fund_count = self.supabase.table('fundamental_data')\
                .select('count', count='exact').execute()
            
            # 종목 수
            stock_count = self.supabase.table('stock_metadata')\
                .select('count', count='exact').execute()
            
            print("\n📈 데이터베이스 현황")
            print("-" * 40)
            print(f"종목 정보: {stock_count.count:,}개")
            print(f"주가 레코드: {price_count.count:,}개")
            print(f"재무지표: {fund_count.count:,}개")
            
        except Exception as e:
            print(f"통계 조회 실패: {e}")
    
    def verify_data_completeness(self):
        """데이터 완전성 검증"""
        print("\n" + "=" * 70)
        print("데이터 완전성 검증")
        print("=" * 70)
        
        # 종목별 데이터 현황
        query = """
        SELECT 
            s.stock_code,
            s.stock_name,
            s.market,
            COUNT(DISTINCT p.date) as price_days,
            CASE WHEN f.stock_code IS NOT NULL THEN '✓' ELSE '✗' END as has_fundamental
        FROM stock_metadata s
        LEFT JOIN price_data p ON s.stock_code = p.stock_code
        LEFT JOIN fundamental_data f ON s.stock_code = f.stock_code
        GROUP BY s.stock_code, s.stock_name, s.market, f.stock_code
        ORDER BY s.market, s.stock_code
        """
        
        # TODO: Supabase에서 직접 쿼리 실행
        print("데이터 완전성 검증 기능은 Supabase 대시보드에서 확인하세요.")
        print("위 SQL 쿼리를 실행하면 종목별 데이터 현황을 확인할 수 있습니다.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='전체 종목 통합 데이터 다운로드')
    parser.add_argument('--years', type=int, default=10, 
                       help='주가 데이터 연수 (기본: 10년)')
    parser.add_argument('--resume', type=str, 
                       help='재시작할 종목코드')
    parser.add_argument('--verify', action='store_true',
                       help='데이터 완전성 검증')
    
    args = parser.parse_args()
    
    downloader = CompleteDataDownloader()
    
    if args.verify:
        downloader.verify_data_completeness()
    else:
        print("\n⚠️  전체 종목 통합 다운로드")
        print("- 주가 데이터 (일봉)")
        print("- 재무지표 (PER, PBR, ROE 등)")
        print("- 예상 시간: 2-3시간")
        print("- 중단 시 자동 재시작 가능")
        
        response = input("\n시작하시겠습니까? (y/n): ")
        if response.lower() == 'y':
            downloader.download_all(args.years, args.resume)