"""
누락된 재무 지표 업데이트
- 업종 (sector)
- ROA
- 부채비율 (debt_ratio)
- 유동비율 (liquidity_ratio)
- 영업이익률 (operating_margin)
- 순이익률 (net_margin)
- 배당수익률 (dividend_yield)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import time
from datetime import datetime
from typing import Dict, Optional

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
    print(r"C:\Users\khanyong\AppData\Local\Programs\Python\Python310-32\python.exe update_missing_indicators.py")
    sys.exit(1)

class FinancialIndicatorUpdater:
    def __init__(self):
        self.app = QApplication.instance() or QApplication([])
        self.kiwoom = Kiwoom()
        
        if self.kiwoom.GetConnectState() == 0:
            print("키움 연결 중...")
            self.kiwoom.CommConnect()
            time.sleep(2)
    
    def get_financial_indicators(self, code: str) -> Optional[Dict]:
        """재무 지표 가져오기"""
        try:
            indicators = {}
            
            # 업종 정보
            indicators['sector'] = self.kiwoom.GetMasterStockInfo(code)
            
            # 재무비율 데이터 조회
            self.kiwoom.SetInputValue("종목코드", code)
            self.kiwoom.CommRqData("재무지표", "OPT10001", 0, "0101")
            time.sleep(0.2)
            
            # ROA (당기순이익 / 총자산 * 100)
            try:
                net_income = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "당기순이익"))
                total_assets = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "총자산"))
                if total_assets > 0:
                    indicators['roa'] = round((net_income / total_assets) * 100, 2)
            except:
                indicators['roa'] = None
            
            # 부채비율 (총부채 / 자기자본 * 100)
            try:
                total_debt = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "총부채"))
                equity = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "자기자본"))
                if equity > 0:
                    indicators['debt_ratio'] = round((total_debt / equity) * 100, 2)
            except:
                indicators['debt_ratio'] = None
            
            # 유동비율 (유동자산 / 유동부채 * 100)
            try:
                current_assets = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "유동자산"))
                current_liabilities = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "유동부채"))
                if current_liabilities > 0:
                    indicators['liquidity_ratio'] = round((current_assets / current_liabilities) * 100, 2)
            except:
                indicators['liquidity_ratio'] = None
            
            # 영업이익률 (영업이익 / 매출액 * 100)
            try:
                operating_income = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "영업이익"))
                revenue = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "매출액"))
                if revenue > 0:
                    indicators['operating_margin'] = round((operating_income / revenue) * 100, 2)
            except:
                indicators['operating_margin'] = None
            
            # 순이익률 (당기순이익 / 매출액 * 100)
            try:
                net_income = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "당기순이익"))
                revenue = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "매출액"))
                if revenue > 0:
                    indicators['net_margin'] = round((net_income / revenue) * 100, 2)
            except:
                indicators['net_margin'] = None
            
            # 배당수익률
            try:
                indicators['dividend_yield'] = float(self.kiwoom.GetCommData("재무지표", "OPT10001", 0, "배당수익률"))
            except:
                indicators['dividend_yield'] = None
            
            return indicators
            
        except Exception as e:
            print(f"오류 {code}: {str(e)[:50]}")
            return None
    
    def update_all_indicators(self):
        """모든 종목의 누락된 지표 업데이트"""
        print("="*50)
        print("📊 누락된 재무 지표 업데이트")
        print("="*50)
        
        # 전체 종목 조회 (페이지네이션)
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
        
        # 업데이트 시작
        print("\n재무 지표 업데이트 시작...")
        print("-"*40)
        
        success = 0
        fail = 0
        
        for i, stock in enumerate(all_stocks, 1):
            code = stock['stock_code']
            name = stock['stock_name']
            
            # 진행 상황 표시
            if i % 50 == 0:
                print(f"\n진행: {i}/{len(all_stocks)} ({i*100//len(all_stocks)}%)")
            
            # 지표 가져오기
            indicators = self.get_financial_indicators(code)
            
            if indicators:
                try:
                    # Supabase 업데이트
                    update_data = {
                        'updated_at': datetime.now().isoformat()
                    }
                    
                    # None이 아닌 값만 업데이트
                    for key, value in indicators.items():
                        if value is not None:
                            update_data[key] = value
                    
                    supabase.table('kw_financial_snapshot')\
                        .update(update_data)\
                        .eq('stock_code', code)\
                        .execute()
                    
                    success += 1
                    print(f"✅ {code} {name[:10]}", end=" ")
                    
                except Exception as e:
                    fail += 1
                    print(f"❌ {code} 업데이트 실패: {str(e)[:30]}")
            else:
                fail += 1
                print(f"❌ {code} 데이터 없음", end=" ")
            
            # API 제한 대기
            time.sleep(0.2)
            
            # 100개마다 잠시 대기
            if i % 100 == 0:
                print(f"\n잠시 대기 중...")
                time.sleep(2)
        
        print("\n" + "="*50)
        print(f"✅ 완료: 성공 {success}개 / 실패 {fail}개")
        
        # 결과 확인
        self.verify_updates()
    
    def verify_updates(self):
        """업데이트 결과 확인"""
        print("\n📊 업데이트 결과 확인")
        print("-"*40)
        
        # 샘플 확인
        test_codes = ['005930', '000660', '035720']
        
        for code in test_codes:
            result = supabase.table('kw_financial_snapshot')\
                .select('stock_code, stock_name, sector, roa, debt_ratio, liquidity_ratio, operating_margin, net_margin, dividend_yield')\
                .eq('stock_code', code)\
                .execute()
            
            if result.data:
                data = result.data[0]
                print(f"\n{data['stock_code']} - {data['stock_name']}")
                print(f"  업종: {data.get('sector', 'N/A')}")
                print(f"  ROA: {data.get('roa', 'N/A')}%")
                print(f"  부채비율: {data.get('debt_ratio', 'N/A')}%")
                print(f"  유동비율: {data.get('liquidity_ratio', 'N/A')}%")
                print(f"  영업이익률: {data.get('operating_margin', 'N/A')}%")
                print(f"  순이익률: {data.get('net_margin', 'N/A')}%")
                print(f"  배당수익률: {data.get('dividend_yield', 'N/A')}%")

if __name__ == "__main__":
    updater = FinancialIndicatorUpdater()
    updater.update_all_indicators()