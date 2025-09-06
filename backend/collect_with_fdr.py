"""
FinanceDataReader를 사용한 재무 지표 수집
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import time
from datetime import datetime
import json
import FinanceDataReader as fdr
import pandas as pd

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

class FDRCollector:
    def __init__(self):
        # 진행상황 추적
        self.progress_file = 'fdr_progress.json'
        self.progress = self.load_progress()
        
        # 한국 상장 종목 리스트
        self.krx_list = fdr.StockListing('KRX')
    
    def load_progress(self):
        """진행상황 로드"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'completed': [], 'last_index': 0}
    
    def save_progress(self):
        """진행상황 저장"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False)
    
    def get_financial_data(self, code: str) -> dict:
        """FDR로 재무 데이터 가져오기"""
        data = {}
        
        try:
            # 종목 정보 가져오기
            stock_info = self.krx_list[self.krx_list['Code'] == code]
            
            if not stock_info.empty:
                # 업종명
                if 'Sector' in stock_info.columns:
                    data['sector_name'] = stock_info.iloc[0]['Sector']
                
                # 시가총액 (백만원 단위)
                if 'Marcap' in stock_info.columns:
                    marcap = stock_info.iloc[0]['Marcap']
                    if pd.notna(marcap):
                        data['market_cap'] = int(marcap * 1000000)  # 백만원 -> 원
                
                # 주식수
                if 'Stocks' in stock_info.columns:
                    stocks = stock_info.iloc[0]['Stocks']
                    if pd.notna(stocks):
                        data['shares_outstanding'] = int(stocks)
            
            # 재무비율 데이터 (krx에서 제공하는 경우)
            # FDR은 주로 가격 데이터 위주라 재무비율은 제한적
            
        except Exception as e:
            print(f"  FDR 오류: {str(e)[:30]}")
        
        return data
    
    def collect_all(self, limit=None, resume=False):
        """모든 종목 수집"""
        print("="*50)
        print("📊 FinanceDataReader로 데이터 수집")
        print("="*50)
        
        # 전체 종목 조회
        print("\n전체 종목 조회 중...")
        all_stocks = []
        page_size = 1000
        offset = 0
        
        while True:
            result = supabase.table('kw_financial_snapshot')\
                .select('stock_code, stock_name')\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            all_stocks.extend(result.data)
            
            if len(result.data) < page_size:
                break
            
            offset += page_size
        
        print(f"총 {len(all_stocks)}개 종목 발견")
        
        # 이어하기 설정
        start_index = 0
        if resume and self.progress['last_index'] > 0:
            start_index = self.progress['last_index']
            print(f"이어하기: {start_index}번째부터 시작")
        
        # 제한 설정
        if limit:
            end_index = min(start_index + limit, len(all_stocks))
        else:
            end_index = len(all_stocks)
        
        # 수집 시작
        print(f"\n수집 시작 ({start_index+1} ~ {end_index})...")
        print("-"*40)
        
        success = 0
        fail = 0
        skip = 0
        
        for i in range(start_index, end_index):
            stock = all_stocks[i]
            code = stock['stock_code']
            name = stock['stock_name']
            
            # 이미 처리된 종목 건너뛰기
            if code in self.progress['completed']:
                skip += 1
                continue
            
            # 진행 상황
            if (i + 1) % 10 == 0:
                print(f"\n진행: {i+1}/{end_index} ({(i+1)*100//end_index}%)")
                print(f"  성공: {success}, 실패: {fail}, 건너뜀: {skip}")
            
            print(f"[{i+1}] {code} {name[:10] if name else ''}", end=" ")
            
            # 데이터 수집
            data = self.get_financial_data(code)
            
            if data:
                try:
                    # 시간 추가
                    data['updated_at'] = datetime.now().isoformat()
                    
                    # Supabase 업데이트
                    supabase.table('kw_financial_snapshot')\
                        .update(data)\
                        .eq('stock_code', code)\
                        .execute()
                    
                    success += 1
                    self.progress['completed'].append(code)
                    print("✅")
                    
                except Exception as e:
                    fail += 1
                    print(f"❌ {str(e)[:20]}")
            else:
                skip += 1
                print("⏭️")
            
            # 진행상황 저장
            self.progress['last_index'] = i + 1
            if (i + 1) % 10 == 0:
                self.save_progress()
            
            # API 제한 방지
            time.sleep(0.1)
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*50)
        print(f"✅ 완료: 성공 {success}개 / 실패 {fail}개 / 건너뜀 {skip}개")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='FDR 데이터 수집')
    parser.add_argument('--limit', type=int, help='수집할 종목 수')
    parser.add_argument('--resume', action='store_true', help='이어하기')
    
    args = parser.parse_args()
    
    # FinanceDataReader 설치 확인
    try:
        import FinanceDataReader
    except ImportError:
        print("FinanceDataReader를 설치해주세요:")
        print("pip install finance-datareader")
        sys.exit(1)
    
    collector = FDRCollector()
    collector.collect_all(limit=args.limit, resume=args.resume)