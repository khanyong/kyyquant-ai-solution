"""
키움증권 API로 재무지표 데이터 수집
"""
from pykiwoom import Kiwoom
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import get_supabase_client

class KiwoomFundamental:
    """재무지표 데이터 수집"""
    
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.supabase = get_supabase_client()
        
    def connect(self):
        """키움 접속"""
        self.kiwoom.CommConnect()
        return self.kiwoom.GetConnectState() == 1
    
    def get_fundamental_data(self, stock_code: str) -> dict:
        """
        종목의 재무지표 조회
        
        키움 API TR:
        - opt10001: 주식기본정보 (PER, PBR, ROE 등)
        - opt10080: 주식분석 (매출액, 영업이익, 순이익)
        """
        
        try:
            # 1. 기본 재무지표 (opt10001)
            df = self.kiwoom.block_request("opt10001",
                                          종목코드=stock_code,
                                          output="주식기본정보",
                                          next=0)
            
            if df is not None and not df.empty:
                # 키움 API 필드명 → 재무지표
                fundamental = {
                    'stock_code': stock_code,
                    'stock_name': self.kiwoom.GetMasterCodeName(stock_code),
                    
                    # 가치평가 지표
                    'per': float(df.get('PER', [0])[0]),           # 주가수익비율
                    'pbr': float(df.get('PBR', [0])[0]),           # 주가순자산비율
                    'eps': int(df.get('EPS', [0])[0]),             # 주당순이익
                    'bps': int(df.get('BPS', [0])[0]),             # 주당순자산
                    
                    # 수익성 지표
                    'roe': float(df.get('ROE', [0])[0]),           # 자기자본이익률
                    'roa': float(df.get('ROA', [0])[0]),           # 총자산이익률
                    
                    # 시가총액/주식수
                    'market_cap': int(df.get('시가총액', [0])[0]) * 100000000,  # 억원→원
                    'shares_outstanding': int(df.get('유통주식', [0])[0]) * 1000,  # 천주→주
                    
                    # 배당
                    'dividend_yield': float(df.get('시가배당률', [0])[0]),
                    
                    'updated_at': datetime.now().isoformat()
                }
                
                # 2. 재무제표 데이터 (opt10080)
                financial = self.get_financial_statements(stock_code)
                if financial:
                    fundamental.update(financial)
                
                return fundamental
            
        except Exception as e:
            print(f"재무지표 조회 실패: {e}")
            return {}
    
    def get_financial_statements(self, stock_code: str) -> dict:
        """재무제표 데이터 조회"""
        try:
            # 연간 재무제표 조회
            df = self.kiwoom.block_request("opt10080",
                                          종목코드=stock_code,
                                          조회구분=0,  # 연간
                                          output="주식분석",
                                          next=0)
            
            if df is not None and not df.empty:
                latest = df.iloc[0]  # 최신 연도
                
                return {
                    # 손익계산서
                    'revenue': int(latest.get('매출액', 0)) * 100000000,        # 억원→원
                    'operating_profit': int(latest.get('영업이익', 0)) * 100000000,
                    'net_profit': int(latest.get('당기순이익', 0)) * 100000000,
                    
                    # 이익률
                    'operating_margin': float(latest.get('영업이익률', 0)),     # %
                    'net_margin': float(latest.get('순이익률', 0)),            # %
                    
                    # 재무상태표
                    'total_assets': int(latest.get('자산총계', 0)) * 100000000,
                    'total_liabilities': int(latest.get('부채총계', 0)) * 100000000,
                    'total_equity': int(latest.get('자본총계', 0)) * 100000000,
                    
                    # 안정성 지표
                    'debt_ratio': float(latest.get('부채비율', 0)),            # %
                    'current_ratio': float(latest.get('유동비율', 0)),         # %
                    
                    'fiscal_year': latest.get('일자', '')  # 회계연도
                }
            
        except Exception as e:
            print(f"재무제표 조회 실패: {e}")
            return {}
    
    def save_to_database(self, fundamental: dict):
        """재무지표를 데이터베이스에 저장"""
        if not fundamental:
            return False
        
        try:
            # fundamental_data 테이블에 저장
            result = self.supabase.table('fundamental_data').upsert(fundamental).execute()
            print(f"저장 완료: {fundamental['stock_name']} ({fundamental['stock_code']})")
            return True
            
        except Exception as e:
            print(f"저장 실패: {e}")
            return False
    
    def download_all_fundamentals(self):
        """전체 종목 재무지표 다운로드"""
        
        # 종목 리스트 가져오기
        stocks = self.supabase.table('stock_metadata')\
            .select('stock_code, stock_name')\
            .execute()
        
        if not stocks.data:
            print("종목 정보가 없습니다.")
            return
        
        success = 0
        fail = 0
        
        for stock in stocks.data:
            code = stock['stock_code']
            name = stock['stock_name']
            
            print(f"\n{name} ({code}) 재무지표 조회...")
            
            # 재무지표 조회
            fundamental = self.get_fundamental_data(code)
            
            if fundamental:
                # 저장
                if self.save_to_database(fundamental):
                    success += 1
                else:
                    fail += 1
            else:
                fail += 1
                print(f"  조회 실패")
            
            # API 제한 대기
            import time
            time.sleep(0.5)
        
        print(f"\n완료: 성공 {success}, 실패 {fail}")


# 재무지표 테이블 SQL
def create_fundamental_table():
    return """
    CREATE TABLE IF NOT EXISTS fundamental_data (
        stock_code VARCHAR(10) PRIMARY KEY,
        stock_name VARCHAR(100),
        
        -- 가치평가 지표
        per DECIMAL(10, 2),        -- 주가수익비율
        pbr DECIMAL(10, 2),        -- 주가순자산비율  
        eps INTEGER,               -- 주당순이익
        bps INTEGER,               -- 주당순자산
        
        -- 수익성 지표
        roe DECIMAL(10, 2),        -- 자기자본이익률 %
        roa DECIMAL(10, 2),        -- 총자산이익률 %
        
        -- 규모
        market_cap BIGINT,         -- 시가총액
        shares_outstanding BIGINT,  -- 발행주식수
        
        -- 손익계산서
        revenue BIGINT,            -- 매출액
        operating_profit BIGINT,   -- 영업이익
        net_profit BIGINT,         -- 순이익
        operating_margin DECIMAL(10, 2),  -- 영업이익률 %
        net_margin DECIMAL(10, 2),        -- 순이익률 %
        
        -- 재무상태표
        total_assets BIGINT,       -- 총자산
        total_liabilities BIGINT,  -- 총부채
        total_equity BIGINT,       -- 자기자본
        
        -- 안정성 지표
        debt_ratio DECIMAL(10, 2),    -- 부채비율 %
        current_ratio DECIMAL(10, 2), -- 유동비율 %
        
        -- 배당
        dividend_yield DECIMAL(10, 2), -- 배당수익률 %
        
        -- 기타
        fiscal_year VARCHAR(10),   -- 회계연도
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_fundamental_per ON fundamental_data(per);
    CREATE INDEX IF NOT EXISTS idx_fundamental_pbr ON fundamental_data(pbr);
    CREATE INDEX IF NOT EXISTS idx_fundamental_roe ON fundamental_data(roe);
    """

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='재무지표 다운로드')
    parser.add_argument('--stock', type=str, help='특정 종목')
    parser.add_argument('--all', action='store_true', help='전체 종목')
    parser.add_argument('--create-table', action='store_true', help='테이블 SQL')
    
    args = parser.parse_args()
    
    if args.create_table:
        print(create_fundamental_table())
    else:
        kf = KiwoomFundamental()
        
        if kf.connect():
            if args.stock:
                # 특정 종목
                data = kf.get_fundamental_data(args.stock)
                if data:
                    print("\n재무지표:")
                    for key, value in data.items():
                        print(f"  {key}: {value}")
                    kf.save_to_database(data)
            elif args.all:
                # 전체 종목
                kf.download_all_fundamentals()
            else:
                # 테스트 (삼성전자)
                data = kf.get_fundamental_data('005930')
                if data:
                    print("\n삼성전자 재무지표:")
                    print(f"  PER: {data.get('per')}")
                    print(f"  PBR: {data.get('pbr')}")
                    print(f"  ROE: {data.get('roe')}%")
                    print(f"  부채비율: {data.get('debt_ratio')}%")