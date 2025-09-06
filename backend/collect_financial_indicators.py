"""
키움 API에서 누락된 재무 지표 수집
- sector_name (업종)
- roa (총자산수익률) 
- debt_ratio (부채비율)
- current_ratio (유동비율)
- operating_margin (영업이익률)
- net_margin (순이익률)
- dividend_yield (배당수익률)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import time
from datetime import datetime
from typing import Dict, Optional
import json

# 환경변수 로드
env_path = Path('D:/Dev/auto_stock/.env')
load_dotenv(env_path)

# Supabase 연결
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_ANON_KEY')
)

# PyQt5 import
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QEventLoop
    from pykiwoom.kiwoom import Kiwoom
except ImportError:
    print("32비트 Python으로 실행해주세요:")
    print(r"C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe collect_financial_indicators.py")
    sys.exit(1)

class FinancialIndicatorCollector:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])
        self.kiwoom = Kiwoom()
        self.event_loop = QEventLoop()
        
        if self.kiwoom.GetConnectState() == 0:
            print("키움 연결 중...")
            self.kiwoom.CommConnect()
            time.sleep(2)
        
        # 진행상황 추적
        self.progress_file = 'indicator_progress.json'
        self.progress = self.load_progress()
    
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
    
    def get_financial_data(self, code: str) -> Optional[Dict]:
        """재무 데이터 조회"""
        try:
            data = {}
            
            # 1. 업종 정보 - pykiwoom의 get_master_stock_state 사용
            try:
                stock_state = self.kiwoom.get_master_stock_state(code)
                if stock_state:
                    # 업종 정보가 포함되어 있을 수 있음
                    data['sector_name'] = stock_state
            except:
                # 메소드가 없거나 오류 시 None
                data['sector_name'] = None
            
            # 2. 기본 정보 조회 (opt10001)
            self.kiwoom.SetInputValue("종목코드", code)
            self.kiwoom.CommRqData("주식기본정보", "opt10001", 0, "0101")
            time.sleep(0.3)
            
            try:
                # PER, PBR, ROE는 이미 있으므로 다른 지표 수집
                
                # 시가총액 (억원 단위)
                market_cap = abs(int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "시가총액")))
                if market_cap > 0:
                    data['market_cap'] = market_cap * 100000000  # 억원 -> 원
                
                # 현재가
                current_price = abs(int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "현재가")))
                if current_price > 0:
                    data['current_price'] = current_price
                
                # PER
                per = float(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "PER"))
                if per != 0:
                    data['per'] = per
                
                # PBR  
                pbr = float(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "PBR"))
                if pbr != 0:
                    data['pbr'] = pbr
                
                # ROE
                roe = float(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "ROE"))
                if roe != 0:
                    data['roe'] = roe
                    
            except Exception as e:
                print(f"  기본정보 파싱 오류: {str(e)[:30]}")
            
            # 3. 재무비율 조회 (opt10081)
            self.kiwoom.SetInputValue("종목코드", code)
            self.kiwoom.CommRqData("주식재무비율", "opt10081", 0, "0101")
            time.sleep(0.3)
            
            try:
                # 부채비율
                debt_ratio = float(self.kiwoom.GetCommData("주식재무비율", "opt10081", 0, "부채비율"))
                if debt_ratio != 0:
                    data['debt_ratio'] = debt_ratio
                
                # 유동비율
                current_ratio = float(self.kiwoom.GetCommData("주식재무비율", "opt10081", 0, "유동비율"))
                if current_ratio != 0:
                    data['current_ratio'] = current_ratio
                
                # ROA
                roa = float(self.kiwoom.GetCommData("주식재무비율", "opt10081", 0, "ROA"))
                if roa != 0:
                    data['roa'] = roa
                
                # 영업이익률
                operating_margin = float(self.kiwoom.GetCommData("주식재무비율", "opt10081", 0, "영업이익률"))
                if operating_margin != 0:
                    data['operating_margin'] = operating_margin
                
                # 순이익률
                net_margin = float(self.kiwoom.GetCommData("주식재무비율", "opt10081", 0, "순이익률"))
                if net_margin != 0:
                    data['net_margin'] = net_margin
                    
            except Exception as e:
                print(f"  재무비율 파싱 오류: {str(e)[:30]}")
            
            # 4. 배당정보 조회 (opt10012)
            self.kiwoom.SetInputValue("종목코드", code)
            self.kiwoom.CommRqData("주식배당정보", "opt10012", 0, "0101")
            time.sleep(0.3)
            
            try:
                # 배당수익률
                dividend_yield = float(self.kiwoom.GetCommData("주식배당정보", "opt10012", 0, "배당수익률"))
                if dividend_yield != 0:
                    data['dividend_yield'] = dividend_yield
                    
            except Exception as e:
                print(f"  배당정보 파싱 오류: {str(e)[:30]}")
            
            return data if data else None
            
        except Exception as e:
            print(f"  전체 오류 {code}: {str(e)[:50]}")
            return None
    
    def update_all_indicators(self, limit=None, resume=False):
        """모든 종목의 재무 지표 업데이트"""
        print("="*50)
        print("📊 재무 지표 수집 및 업데이트")
        print("="*50)
        
        # 전체 종목 조회
        print("\n전체 종목 조회 중...")
        all_stocks = []
        page_size = 1000
        offset = 0
        
        while True:
            result = supabase.table('kw_financial_snapshot')\
                .select('id, stock_code, stock_name')\
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
        
        # 업데이트 시작
        print(f"\n재무 지표 수집 시작 ({start_index+1} ~ {end_index})...")
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
            
            # 진행 상황 표시
            if (i + 1) % 10 == 0:
                print(f"\n진행: {i+1}/{end_index} ({(i+1)*100//end_index}%)")
                print(f"  성공: {success}, 실패: {fail}, 건너뜀: {skip}")
            
            print(f"[{i+1}/{end_index}] {code} {name[:10] if name else 'N/A'}", end=" ")
            
            # 재무 데이터 가져오기
            financial_data = self.get_financial_data(code)
            
            if financial_data:
                try:
                    # 업데이트 시간 추가
                    financial_data['updated_at'] = datetime.now().isoformat()
                    
                    # Supabase 업데이트
                    supabase.table('kw_financial_snapshot')\
                        .update(financial_data)\
                        .eq('stock_code', code)\
                        .execute()
                    
                    success += 1
                    self.progress['completed'].append(code)
                    print("✅")
                    
                except Exception as e:
                    fail += 1
                    print(f"❌ 업데이트 실패: {str(e)[:30]}")
            else:
                fail += 1
                print("❌ 데이터 없음")
            
            # 진행상황 저장
            self.progress['last_index'] = i + 1
            if (i + 1) % 10 == 0:
                self.save_progress()
            
            # API 제한 대기
            time.sleep(0.5)  # 초당 2회 제한
            
            # 100개마다 긴 대기
            if (i + 1) % 100 == 0:
                print(f"\n잠시 대기 중 (API 제한)...")
                time.sleep(3)
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*50)
        print(f"✅ 완료: 성공 {success}개 / 실패 {fail}개 / 건너뜀 {skip}개")
        
        # 결과 확인
        self.verify_updates()
    
    def verify_updates(self):
        """업데이트 결과 확인"""
        print("\n📊 업데이트 결과 확인")
        print("-"*40)
        
        # 샘플 확인
        test_codes = ['005930', '000660', '035720', '051910', '207940']
        
        for code in test_codes:
            result = supabase.table('kw_financial_snapshot')\
                .select('stock_code, stock_name, sector_name, market_cap, per, pbr, roe, roa, debt_ratio, current_ratio, operating_margin, net_margin, dividend_yield')\
                .eq('stock_code', code)\
                .execute()
            
            if result.data and len(result.data) > 0:
                data = result.data[0]
                print(f"\n{data['stock_code']} - {data['stock_name']}")
                print(f"  업종: {data.get('sector_name', 'N/A')}")
                print(f"  시가총액: {data.get('market_cap', 0):,}원")
                print(f"  PER: {data.get('per', 'N/A')}")
                print(f"  PBR: {data.get('pbr', 'N/A')}")
                print(f"  ROE: {data.get('roe', 'N/A')}%")
                print(f"  ROA: {data.get('roa', 'N/A')}%")
                print(f"  부채비율: {data.get('debt_ratio', 'N/A')}%")
                print(f"  유동비율: {data.get('current_ratio', 'N/A')}%")
                print(f"  영업이익률: {data.get('operating_margin', 'N/A')}%")
                print(f"  순이익률: {data.get('net_margin', 'N/A')}%")
                print(f"  배당수익률: {data.get('dividend_yield', 'N/A')}%")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='재무 지표 수집')
    parser.add_argument('--limit', type=int, help='수집할 종목 수 제한')
    parser.add_argument('--resume', action='store_true', help='이어하기')
    
    args = parser.parse_args()
    
    collector = FinancialIndicatorCollector()
    collector.update_all_indicators(limit=args.limit, resume=args.resume)