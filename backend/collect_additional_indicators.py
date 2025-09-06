"""
추가 재무 지표 수집 (ROA, 부채비율, 유동비율 등)
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
    print(r"C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe collect_additional_indicators.py")
    sys.exit(1)

class AdditionalIndicatorCollector:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])
        self.kiwoom = Kiwoom()
        
        if self.kiwoom.GetConnectState() == 0:
            print("키움 연결 중...")
            self.kiwoom.CommConnect()
            time.sleep(2)
        
        # 진행상황 추적
        self.progress_file = 'additional_indicator_progress.json'
        self.progress = self.load_progress()
    
    def load_progress(self):
        """진행상황 로드"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'completed': [], 'last_index': 0, 'failures': {}}
    
    def save_progress(self):
        """진행상황 저장"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False)
    
    def get_financial_ratios(self, code: str) -> dict:
        """재무비율 가져오기 (opt10081)"""
        data = {}
        
        try:
            # opt10081: 주식일봉차트조회 (재무비율 포함)
            self.kiwoom.SetInputValue("종목코드", code)
            self.kiwoom.SetInputValue("기준일자", "20241231")  # 최신 데이터
            self.kiwoom.SetInputValue("수정주가구분", "1")
            
            self.kiwoom.CommRqData("재무비율", "opt10081", 0, "0101")
            time.sleep(0.3)
            
            # 데이터 파싱
            try:
                # 부채비율 (GetCommData의 인덱스 확인 필요)
                debt_ratio = self.kiwoom.GetCommData("재무비율", "opt10081", 0, "부채비율")
                if debt_ratio:
                    data['debt_ratio'] = float(debt_ratio.strip())
            except:
                pass
            
            try:
                # 유동비율
                current_ratio = self.kiwoom.GetCommData("재무비율", "opt10081", 0, "유동비율")
                if current_ratio:
                    data['current_ratio'] = float(current_ratio.strip())
            except:
                pass
            
            try:
                # ROA
                roa = self.kiwoom.GetCommData("재무비율", "opt10081", 0, "ROA")
                if roa:
                    data['roa'] = float(roa.strip())
            except:
                pass
            
            try:
                # 영업이익률
                operating_margin = self.kiwoom.GetCommData("재무비율", "opt10081", 0, "영업이익률")
                if operating_margin:
                    data['operating_margin'] = float(operating_margin.strip())
            except:
                pass
            
            try:
                # 순이익률
                net_margin = self.kiwoom.GetCommData("재무비율", "opt10081", 0, "순이익률")
                if net_margin:
                    data['net_margin'] = float(net_margin.strip())
            except:
                pass
            
        except Exception as e:
            # opt10081이 안되면 다른 방법 시도
            pass
        
        # 대체 방법: opt10001에서 추가 정보 시도
        if not data:
            try:
                self.kiwoom.SetInputValue("종목코드", code)
                self.kiwoom.CommRqData("추가정보", "opt10001", 0, "0101")
                time.sleep(0.3)
                
                # 배당수익률
                try:
                    dividend = self.kiwoom.GetCommData("추가정보", "opt10001", 0, "배당수익률")
                    if dividend:
                        data['dividend_yield'] = float(dividend.strip())
                except:
                    pass
                
            except:
                pass
        
        return data
    
    def collect_all(self, limit=None, resume=False):
        """모든 종목의 추가 지표 수집"""
        print("="*50)
        print("📊 추가 재무 지표 수집")
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
            
            # 재무비율 수집
            data = self.get_financial_ratios(code)
            
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
                    self.progress['failures'][code] = str(e)
                    print(f"❌ {str(e)[:20]}")
            else:
                # 데이터가 없어도 처리된 것으로 표시 (재무제표가 없는 종목일 수 있음)
                self.progress['completed'].append(code)
                skip += 1
                print("⏭️")
            
            # 진행상황 저장
            self.progress['last_index'] = i + 1
            if (i + 1) % 10 == 0:
                self.save_progress()
            
            # API 제한
            time.sleep(0.3)
            
            # 50개마다 대기
            if (i + 1) % 50 == 0:
                print("잠시 대기...")
                time.sleep(2)
        
        # 최종 저장
        self.save_progress()
        
        print("\n" + "="*50)
        print(f"✅ 완료: 성공 {success}개 / 실패 {fail}개 / 건너뜀 {skip}개")
        
        # 샘플 확인
        print("\n📊 샘플 확인")
        print("-"*40)
        
        test_codes = ['005930', '000660', '035720']
        for code in test_codes:
            result = supabase.table('kw_financial_snapshot')\
                .select('stock_code, stock_name, roa, debt_ratio, current_ratio, operating_margin, net_margin, dividend_yield')\
                .eq('stock_code', code)\
                .execute()
            
            if result.data:
                data = result.data[0]
                print(f"\n{data['stock_code']} - {data['stock_name']}")
                print(f"  ROA: {data.get('roa', 'N/A')}%")
                print(f"  부채비율: {data.get('debt_ratio', 'N/A')}%")
                print(f"  유동비율: {data.get('current_ratio', 'N/A')}%")
                print(f"  영업이익률: {data.get('operating_margin', 'N/A')}%")
                print(f"  순이익률: {data.get('net_margin', 'N/A')}%")
                print(f"  배당수익률: {data.get('dividend_yield', 'N/A')}%")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='추가 재무 지표 수집')
    parser.add_argument('--limit', type=int, help='수집할 종목 수')
    parser.add_argument('--resume', action='store_true', help='이어하기')
    
    args = parser.parse_args()
    
    collector = AdditionalIndicatorCollector()
    collector.collect_all(limit=args.limit, resume=args.resume)