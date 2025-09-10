"""
키움증권 API를 통한 과거 주가 데이터 조회
"""
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_client import get_supabase_client

class KiwoomDataAPI:
    """키움증권 데이터 API 클래스"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.kiwoom_api = None
        self.connected = False
        
        # 키움 OpenAPI+ 사용 가능 여부 확인
        try:
            from .kiwoom_openapi import KiwoomOpenAPI
            self.kiwoom_api = KiwoomOpenAPI()
            self.connected = self.kiwoom_api.connect()
            if self.connected:
                print("키움 OpenAPI+ 연결 성공")
            else:
                print("키움 OpenAPI+ 연결 실패 - 모의 데이터 사용")
        except Exception as e:
            print(f"키움 OpenAPI+ 초기화 실패: {e}")
            print("모의 데이터를 사용합니다.")
        
    def authenticate(self, app_key: str = None, app_secret: str = None):
        """키움증권 API 인증 (OpenAPI+는 자동 인증)"""
        # OpenAPI+가 연결되어 있으면 이미 인증됨
        if self.connected and self.kiwoom_api:
            return True
        
        # OpenAPI+ 연결 재시도
        try:
            if not self.kiwoom_api:
                from .kiwoom_openapi import KiwoomOpenAPI
                self.kiwoom_api = KiwoomOpenAPI()
            
            self.connected = self.kiwoom_api.connect()
            return self.connected
            
        except Exception as e:
            print(f"키움 OpenAPI+ 인증 실패: {e}")
            return False
    
    def get_daily_price(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        키움증권 API로 일별 주가 데이터 조회
        
        Args:
            stock_code: 종목코드 (예: "005930")
            start_date: 시작일 (YYYYMMDD)
            end_date: 종료일 (YYYYMMDD)
        """
        # 키움 OpenAPI+ 사용
        if self.connected and self.kiwoom_api:
            try:
                return self.kiwoom_api.get_ohlcv(stock_code, start_date, end_date)
            except Exception as e:
                print(f"키움 API 조회 실패: {e}")
                return pd.DataFrame()
        
        # OpenAPI+ 연결 실패 시 모의 데이터 반환
        print(f"키움 OpenAPI+ 미연결 - 모의 데이터 사용: {stock_code}")
        
        # 모의 데이터 생성
        from .mock_kiwoom_api import generate_mock_stock_data
        
        # 날짜 형식 변환 (YYYYMMDD -> YYYY-MM-DD)
        if len(start_date) == 8 and '-' not in start_date:
            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]}"
        if len(end_date) == 8 and '-' not in end_date:
            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:]}"
            
        return generate_mock_stock_data(stock_code, start_date, end_date)
    
    def get_minute_price(self, stock_code: str, interval: str = '1') -> pd.DataFrame:
        """
        키움증권 API로 분봉 데이터 조회
        
        Args:
            stock_code: 종목코드
            interval: 분봉 간격 (1, 5, 10, 15, 30, 60)
        """
        # 키움 OpenAPI+ 사용
        if self.connected and self.kiwoom_api:
            try:
                return self.kiwoom_api.get_minute_data(stock_code, int(interval))
            except Exception as e:
                print(f"키움 API 분봉 조회 실패: {e}")
                return pd.DataFrame()
        
        # OpenAPI+ 미연결 시 빈 데이터프레임 반환
        print(f"키움 OpenAPI+ 미연결 - 분봉 데이터 없음")
        return pd.DataFrame()
    
    def save_to_supabase(self, df: pd.DataFrame, stock_code: str):
        """
        조회한 주가 데이터를 Supabase에 저장
        """
        try:
            records = []
            for index, row in df.iterrows():
                record = {
                    'stock_code': stock_code,
                    'date': index.isoformat(),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume']),
                    'trading_value': int(row.get('amount', 0))
                }
                records.append(record)
            
            # Supabase에 bulk insert
            result = self.supabase.table('price_data').upsert(records).execute()
            return len(records)
            
        except Exception as e:
            print(f"데이터 저장 실패: {e}")
            return 0
    
    def get_from_supabase(self, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Supabase에서 저장된 주가 데이터 조회
        """
        try:
            result = self.supabase.table('price_data').select('*')\
                .eq('stock_code', stock_code)\
                .gte('date', start_date)\
                .lte('date', end_date)\
                .order('date', desc=False)\
                .execute()
            
            if result.data:
                df = pd.DataFrame(result.data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Supabase 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def get_historical_data(self, stock_code: str, start_date: str, end_date: str, 
                          use_cache: bool = True) -> pd.DataFrame:
        """
        과거 주가 데이터 조회 (캐시 우선, 없으면 API 호출)
        
        Args:
            stock_code: 종목코드
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            use_cache: Supabase 캐시 사용 여부
        """
        # 1. 캐시(Supabase) 확인
        if use_cache:
            cached_data = self.get_from_supabase(stock_code, start_date, end_date)
            if not cached_data.empty:
                print(f"캐시에서 데이터 로드: {stock_code}")
                return cached_data
        
        # 2. 키움 API로 조회
        print(f"키움 API에서 데이터 조회: {stock_code}")
        
        # 날짜 형식 변환 (YYYY-MM-DD -> YYYYMMDD)
        start = start_date.replace('-', '')
        end = end_date.replace('-', '')
        
        df = self.get_daily_price(stock_code, start, end)
        
        # 3. API 실패 시 모의 데이터 사용 (개발/테스트용)
        if df.empty:
            print(f"API 데이터 조회 실패 - 모의 데이터 사용: {stock_code}")
            from .mock_kiwoom_api import generate_mock_stock_data
            df = generate_mock_stock_data(stock_code, start_date, end_date)
        
        # 4. 데이터 저장
        if not df.empty and use_cache:
            saved_count = self.save_to_supabase(df, stock_code)
            print(f"{saved_count}개 레코드 저장 완료")
        
        return df


# 백테스트용 헬퍼 함수
def get_backtest_data(stock_codes: List[str], start_date: str, end_date: str, 
                      config: Dict) -> Dict[str, pd.DataFrame]:
    """
    백테스트용 주가 데이터 일괄 조회
    """
    kiwoom_api = KiwoomDataAPI()
    
    # 키움 API 인증
    kiwoom_api.authenticate(
        config.get('kiwoom_app_key'),
        config.get('kiwoom_app_secret')
    )
    
    all_data = {}
    for code in stock_codes:
        data = kiwoom_api.get_historical_data(code, start_date, end_date)
        if not data.empty:
            all_data[code] = data
        else:
            print(f"Warning: {code} 데이터를 가져올 수 없습니다")
    
    return all_data