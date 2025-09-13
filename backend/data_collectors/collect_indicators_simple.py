"""
키움 API에서 재무 지표 수집 (단순화 버전)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import time
from datetime import datetime
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
    from pykiwoom.kiwoom import Kiwoom
except ImportError:
    print("32비트 Python으로 실행해주세요:")
    print(r"C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe collect_indicators_simple.py")
    sys.exit(1)

class SimpleIndicatorCollector:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])
        self.kiwoom = Kiwoom()
        
        if self.kiwoom.GetConnectState() == 0:
            print("키움 연결 중...")
            self.kiwoom.CommConnect()
            time.sleep(2)
        
        # 진행상황 추적
        self.progress_file = 'simple_indicator_progress.json'
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
    
    def get_basic_info(self, code: str) -> dict:
        """기본 정보만 가져오기"""
        data = {}
        
        try:
            # 기본 정보 조회 (opt10001)
            self.kiwoom.SetInputValue("종목코드", code)
            self.kiwoom.CommRqData("주식기본정보", "opt10001", 0, "0101")
            time.sleep(0.3)
            
            # 시가총액
            try:
                market_cap = abs(int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "시가총액")))
                if market_cap > 0:
                    data['market_cap'] = market_cap * 100000000  # 억원 -> 원
            except:
                pass
            
            # 현재가
            try:
                current_price = abs(int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "현재가")))
                if current_price > 0:
                    data['current_price'] = current_price
            except:
                pass
            
            # PER
            try:
                per = float(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "PER"))
                if per != 0:
                    data['per'] = per
            except:
                pass
            
            # PBR
            try:
                pbr = float(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "PBR"))
                if pbr != 0:
                    data['pbr'] = pbr
            except:
                pass
            
            # ROE
            try:
                roe = float(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "ROE"))
                if roe != 0:
                    data['roe'] = roe
            except:
                pass
            
            # EPS
            try:
                eps = int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "EPS"))
                if eps != 0:
                    data['eps'] = eps
            except:
                pass
            
            # BPS
            try:
                bps = int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "BPS"))
                if bps != 0:
                    data['bps'] = bps
            except:
                pass
            
            # 52주 최고/최저
            try:
                high_52w = abs(int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "250최고")))
                if high_52w > 0:
                    data['high_52w'] = high_52w
                    
                low_52w = abs(int(self.kiwoom.GetCommData("주식기본정보", "opt10001", 0, "250최저")))
                if low_52w > 0:
                    data['low_52w'] = low_52w
            except:
                pass
            
        except Exception as e:
            print(f"기본정보 오류: {str(e)[:30]}")
        
        return data
    
    def collect_all(self, limit=None, resume=False):
        """모든 종목 수집"""
        print("="*50)
        print("📊 재무 지표 수집 (단순화 버전)")
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
        
        for i in range(start_index, end_index):
            stock = all_stocks[i]
            code = stock['stock_code']
            name = stock['stock_name']
            
            # 진행 상황
            if (i + 1) % 10 == 0:
                print(f"\n진행: {i+1}/{end_index} ({(i+1)*100//end_index}%)")
                print(f"  성공: {success}, 실패: {fail}")
            
            print(f"[{i+1}] {code} {name[:10] if name else ''}", end=" ")
            
            # 데이터 수집
            data = self.get_basic_info(code)
            
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
                    print("✅")
                    
                except Exception as e:
                    fail += 1
                    print(f"❌ {str(e)[:20]}")
            else:
                fail += 1
                print("❌")
            
            # 진행상황 저장
            self.progress['last_index'] = i + 1
            self.progress['completed'].append(code)
            if (i + 1) % 10 == 0:
                self.save_progress()
            
            # API 제한
            time.sleep(0.2)
            
            # 100개마다 대기
            if (i + 1) % 100 == 0:
                print("잠시 대기...")
                time.sleep(2)
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*50)
        print(f"✅ 완료: 성공 {success}개 / 실패 {fail}개")
        
        # 샘플 확인
        print("\n📊 샘플 확인")
        print("-"*40)
        
        test_codes = ['005930', '000660', '035720']
        for code in test_codes:
            result = supabase.table('kw_financial_snapshot')\
                .select('stock_code, stock_name, market_cap, current_price, per, pbr, roe')\
                .eq('stock_code', code)\
                .execute()
            
            if result.data:
                data = result.data[0]
                print(f"\n{data['stock_code']} - {data['stock_name']}")
                print(f"  시가총액: {data.get('market_cap', 0):,}원")
                print(f"  현재가: {data.get('current_price', 0):,}원")
                print(f"  PER: {data.get('per', 'N/A')}")
                print(f"  PBR: {data.get('pbr', 'N/A')}")
                print(f"  ROE: {data.get('roe', 'N/A')}%")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='재무 지표 수집 (단순화)')
    parser.add_argument('--limit', type=int, help='수집할 종목 수')
    parser.add_argument('--resume', action='store_true', help='이어하기')
    
    args = parser.parse_args()
    
    collector = SimpleIndicatorCollector()
    collector.collect_all(limit=args.limit, resume=args.resume)