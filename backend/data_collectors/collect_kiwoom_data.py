"""
Kiwoom OpenAPI+ 데이터 수집 및 Supabase 저장
"""
import sys
import os
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any
import json

# PyQt5 imports
from PyQt5.QWidgets import QApplication
from PyQt5.QtCore import QEventLoop

# pykiwoom imports
from pykiwoom.kiwoom import Kiwoom

# Supabase imports
from supabase import create_client, Client
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class KiwoomDataCollector:
    def __init__(self):
        """키움 데이터 수집기 초기화"""
        # Supabase 연결
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_KEY')
        )
        
        # PyQt 앱 생성
        self.app = QApplication(sys.argv) if not QApplication.instance() else QApplication.instance()
        
        # 키움 API 연결
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect()
        
        print("✅ 키움 OpenAPI+ 연결 완료")
        print(f"✅ Supabase 연결 완료: {os.getenv('SUPABASE_URL')}")
        
    def get_stock_list(self, market: str = "0") -> List[Dict]:
        """
        종목 리스트 조회
        market: "0"=코스피, "10"=코스닥
        """
        print(f"\n📊 {market} 종목 리스트 조회 중...")
        
        code_list = self.kiwoom.GetCodeListByMarket(market)
        stock_list = []
        
        for code in code_list[:50]:  # 테스트로 50개만
            name = self.kiwoom.GetMasterCodeName(code)
            if name and not name.startswith("KODEX"):  # ETF 제외
                stock_info = {
                    'stock_code': code,
                    'stock_name': name,
                    'market': 'KOSPI' if market == "0" else 'KOSDAQ',
                    'sector_name': self.kiwoom.GetMasterStockInfo(code)
                }
                stock_list.append(stock_info)
                
        print(f"✅ {len(stock_list)}개 종목 조회 완료")
        return stock_list
    
    def save_stock_master(self, stock_list: List[Dict]):
        """종목 마스터 정보 저장"""
        print("\n💾 종목 마스터 정보 저장 중...")
        
        for stock in stock_list:
            try:
                self.supabase.table('kw_stock_master').upsert(stock).execute()
            except Exception as e:
                print(f"❌ {stock['stock_name']} 저장 실패: {e}")
                
        print(f"✅ {len(stock_list)}개 종목 마스터 저장 완료")
    
    def get_daily_prices(self, code: str, days: int = 365) -> pd.DataFrame:
        """일봉 데이터 조회"""
        print(f"📈 {code} 일봉 데이터 조회 중...")
        
        # TR: opt10081 (주식일봉차트조회)
        df = self.kiwoom.block_request("opt10081",
            종목코드=code,
            기준일자=datetime.now().strftime("%Y%m%d"),
            수정주가구분=1,
            output="주식일봉차트",
            next=0
        )
        
        if df is not None and not df.empty:
            # 컬럼명 변경
            df = df.rename(columns={
                '현재가': 'close',
                '시가': 'open',
                '고가': 'high',
                '저가': 'low',
                '거래량': 'volume'
            })
            
            # 날짜 형식 변환
            df['trade_date'] = pd.to_datetime(df.index).strftime('%Y-%m-%d')
            df['stock_code'] = code
            
            # 필요한 컬럼만 선택
            return df[['stock_code', 'trade_date', 'open', 'high', 'low', 'close', 'volume']]
        
        return pd.DataFrame()
    
    def save_daily_prices(self, df: pd.DataFrame):
        """일봉 데이터 저장"""
        if df.empty:
            return
            
        stock_code = df['stock_code'].iloc[0]
        print(f"💾 {stock_code} 일봉 데이터 저장 중... ({len(df)}개)")
        
        # 데이터 저장
        records = df.to_dict('records')
        for record in records:
            # 숫자 값 정리
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in record:
                    record[col] = abs(float(record[col])) if record[col] else 0
                    
            try:
                self.supabase.table('kw_price_daily').upsert(record).execute()
            except Exception as e:
                print(f"❌ 저장 실패: {e}")
                break
                
        print(f"✅ {stock_code} 일봉 저장 완료")
    
    def get_current_price(self, code: str) -> Dict:
        """현재가 조회"""
        # TR: opt10001 (주식기본정보)
        df = self.kiwoom.block_request("opt10001",
            종목코드=code,
            output="주식기본정보",
            next=0
        )
        
        if df is not None and not df.empty:
            return {
                'stock_code': code,
                'current_price': abs(float(df.iloc[0].get('현재가', 0))),
                'change_price': float(df.iloc[0].get('전일대비', 0)),
                'change_rate': float(df.iloc[0].get('등락율', 0)),
                'volume': int(df.iloc[0].get('거래량', 0)),
                'high_52w': abs(float(df.iloc[0].get('52주최고', 0))),
                'low_52w': abs(float(df.iloc[0].get('52주최저', 0))),
                'market_cap': int(df.iloc[0].get('시가총액', 0)) * 100000000  # 억원 → 원
            }
        return None
    
    def save_current_price(self, price_data: Dict):
        """현재가 저장"""
        if not price_data:
            return
            
        try:
            self.supabase.table('kw_price_current').upsert(price_data).execute()
            print(f"✅ {price_data['stock_code']} 현재가 저장 완료")
        except Exception as e:
            print(f"❌ 현재가 저장 실패: {e}")
    
    def get_financial_info(self, code: str) -> Dict:
        """재무 정보 조회"""
        # TR: opt10001에서 기본 재무비율 추출
        df = self.kiwoom.block_request("opt10001",
            종목코드=code,
            output="주식기본정보",
            next=0
        )
        
        if df is not None and not df.empty:
            row = df.iloc[0]
            return {
                'stock_code': code,
                'per': float(row.get('PER', 0)),
                'pbr': float(row.get('PBR', 0)),
                'roe': float(row.get('ROE', 0)),
                'eps': int(row.get('EPS', 0)),
                'bps': int(row.get('BPS', 0)),
                'dividend_yield': float(row.get('배당수익률', 0))
            }
        return None
    
    def save_financial_info(self, financial_data: Dict):
        """재무 정보 저장"""
        if not financial_data:
            return
            
        try:
            self.supabase.table('kw_financial_ratio').upsert(financial_data).execute()
            print(f"✅ {financial_data['stock_code']} 재무비율 저장 완료")
        except Exception as e:
            print(f"❌ 재무비율 저장 실패: {e}")
    
    def collect_all_data(self):
        """전체 데이터 수집 실행"""
        print("\n" + "="*50)
        print("🚀 키움 OpenAPI+ 데이터 수집 시작")
        print("="*50)
        
        # 1. 종목 리스트 수집
        kospi_stocks = self.get_stock_list("0")  # 코스피
        kosdaq_stocks = self.get_stock_list("10")  # 코스닥
        all_stocks = kospi_stocks + kosdaq_stocks
        
        # 2. 종목 마스터 저장
        self.save_stock_master(all_stocks)
        
        # 3. 주요 종목 상세 데이터 수집
        major_codes = ['005930', '000660', '035720', '035420', '005380']  # 주요 5종목
        
        for code in major_codes:
            print(f"\n{'='*30}")
            print(f"📊 {code} 데이터 수집 중...")
            print(f"{'='*30}")
            
            # 일봉 데이터
            daily_df = self.get_daily_prices(code)
            self.save_daily_prices(daily_df)
            time.sleep(0.5)  # API 호출 제한 방지
            
            # 현재가
            current = self.get_current_price(code)
            self.save_current_price(current)
            time.sleep(0.5)
            
            # 재무비율
            financial = self.get_financial_info(code)
            self.save_financial_info(financial)
            time.sleep(0.5)
        
        print("\n" + "="*50)
        print("✅ 데이터 수집 완료!")
        print("="*50)
        
        # 통계 출력
        self.print_statistics()
    
    def print_statistics(self):
        """수집 데이터 통계 출력"""
        print("\n📊 수집 데이터 통계:")
        
        # 종목 수
        result = self.supabase.table('kw_stock_master').select("count", count='exact').execute()
        print(f"- 종목 마스터: {result.count}개")
        
        # 일봉 데이터
        result = self.supabase.table('kw_price_daily').select("count", count='exact').execute()
        print(f"- 일봉 데이터: {result.count}개")
        
        # 현재가
        result = self.supabase.table('kw_price_current').select("count", count='exact').execute()
        print(f"- 현재가: {result.count}개")
        
        # 재무비율
        result = self.supabase.table('kw_financial_ratio').select("count", count='exact').execute()
        print(f"- 재무비율: {result.count}개")

def main():
    """메인 실행 함수"""
    collector = KiwoomDataCollector()
    
    try:
        collector.collect_all_data()
    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
    finally:
        print("\n프로그램 종료")
        sys.exit(0)

if __name__ == "__main__":
    main()