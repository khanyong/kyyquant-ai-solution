"""
데이터 제공자
주가 데이터를 Supabase 또는 외부 API에서 가져오기
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import os
from supabase import create_client

class DataProvider:
    """데이터 제공자"""

    def __init__(self):
        self._init_database()

    def _init_database(self):
        """데이터베이스 연결 초기화"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

            if url and key:
                self.supabase = create_client(url, key)
                print("DataProvider: Supabase connected")
            else:
                self.supabase = None
                print("DataProvider: Running with mock data")
        except Exception as e:
            print(f"DataProvider: Database connection failed: {e}")
            self.supabase = None

    async def get_historical_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
        interval: str = '1d'
    ) -> Optional[pd.DataFrame]:
        """
        과거 주가 데이터 가져오기

        Args:
            stock_code: 종목 코드
            start_date: 시작일 (YYYY-MM-DD)
            end_date: 종료일 (YYYY-MM-DD)
            interval: 데이터 간격 (1d, 1h, etc)

        Returns:
            주가 데이터 DataFrame
        """

        # Supabase에서 데이터 가져오기 시도
        if self.supabase:
            try:
                print(f"[DataProvider] Fetching data for {stock_code} from {start_date} to {end_date}")

                # kw_price_daily 테이블 사용 - 올바른 컬럼명 사용
                response = self.supabase.table('kw_price_daily').select('*').eq(
                    'stock_code', stock_code  # 올바른 컬럼명
                ).gte('trade_date', start_date).lte('trade_date', end_date).order('trade_date').execute()

                if response.data and len(response.data) > 0:
                    print(f"[DataProvider] Found {len(response.data)} rows for {stock_code}")
                    df = pd.DataFrame(response.data)

                    # 컬럼명 확인
                    print(f"[DataProvider] Available columns: {df.columns.tolist()}")

                    # trade_date를 date로 변경하고 인덱스로 설정
                    if 'trade_date' in df.columns:
                        df['date'] = pd.to_datetime(df['trade_date'])
                        df.set_index('date', inplace=True)
                    elif 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'])
                        df.set_index('date', inplace=True)

                    # 숫자형 컬럼 변환 (numeric 타입을 float로)
                    numeric_columns = ['open', 'high', 'low', 'close']
                    for col in numeric_columns:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                    # volume은 bigint이므로 int로 변환
                    if 'volume' in df.columns:
                        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype('int64')

                    # 필수 컬럼 확인
                    required_columns = ['open', 'high', 'low', 'close', 'volume']
                    if all(col in df.columns for col in required_columns):
                        print(f"[DataProvider] Successfully loaded real data for {stock_code}")
                        return df[required_columns]
                    else:
                        missing = [col for col in required_columns if col not in df.columns]
                        print(f"[DataProvider] Missing columns: {missing}")
                        print(f"[DataProvider] Available columns after mapping: {df.columns.tolist()}")
                else:
                    print(f"[DataProvider] No data found for {stock_code} in the given date range")

            except Exception as e:
                print(f"[DataProvider] Failed to fetch data from Supabase: {e}")
                import traceback
                traceback.print_exc()

        # Mock 데이터 생성 (테스트용)
        print(f"[DataProvider] WARNING: Using mock data for {stock_code}")
        return self._generate_mock_data(stock_code, start_date, end_date)

    def _generate_mock_data(
        self,
        stock_code: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """테스트용 모의 데이터 생성"""

        # 날짜 범위 생성
        dates = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days only

        # 기본 가격 설정 (종목별로 다르게)
        base_prices = {
            '005930': 70000,  # 삼성전자
            '000660': 130000,  # SK하이닉스
            '035720': 400000,  # 카카오
            '035420': 270000,  # NAVER
        }
        base_price = base_prices.get(stock_code, 50000)

        # 랜덤 워크로 가격 생성
        np.random.seed(hash(stock_code) % 10000)  # 종목별 시드
        returns = np.random.normal(0.001, 0.02, len(dates))  # 일일 수익률
        prices = base_price * np.exp(np.cumsum(returns))

        # OHLCV 데이터 생성
        data = []
        for i, date in enumerate(dates):
            close = prices[i]
            open_price = close * (1 + np.random.uniform(-0.01, 0.01))
            high = max(open_price, close) * (1 + np.random.uniform(0, 0.02))
            low = min(open_price, close) * (1 - np.random.uniform(0, 0.02))
            volume = int(np.random.uniform(1000000, 5000000))

            data.append({
                'date': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })

        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)

        print(f"Generated mock data for {stock_code}: {len(df)} rows")
        return df

    async def get_stock_list(self, market: Optional[str] = None) -> list:
        """
        종목 목록 가져오기

        Args:
            market: 시장 구분 (KOSPI, KOSDAQ, None for all)

        Returns:
            종목 목록
        """

        if self.supabase:
            try:
                query = self.supabase.table('stocks').select('code, name, market')

                if market:
                    query = query.eq('market', market)

                response = query.execute()

                if response.data:
                    return response.data

            except Exception as e:
                print(f"Failed to fetch stock list: {e}")

        # 기본 종목 목록 반환
        return [
            {'code': '005930', 'name': '삼성전자', 'market': 'KOSPI'},
            {'code': '000660', 'name': 'SK하이닉스', 'market': 'KOSPI'},
            {'code': '035720', 'name': '카카오', 'market': 'KOSPI'},
            {'code': '035420', 'name': 'NAVER', 'market': 'KOSPI'},
        ]

    async def get_current_price(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        현재가 조회

        Args:
            stock_code: 종목 코드

        Returns:
            현재가 정보
        """

        if self.supabase:
            try:
                # 가장 최근 데이터 가져오기 - kw_price_daily 테이블 사용
                response = self.supabase.table('kw_price_daily').select('*').eq(
                    'stock_code', stock_code
                ).order('trade_date', desc=True).limit(1).execute()

                if response.data:
                    data = response.data[0]
                    # 필드명 맞춤
                    return {
                        'stock_code': stock_code,
                        'current_price': float(data.get('close', 0)),
                        'change': float(data.get('close', 0)) - float(data.get('open', 0)),
                        'change_rate': float(data.get('change_rate', 0)),
                        'volume': int(data.get('volume', 0))
                    }

            except Exception as e:
                print(f"Failed to fetch current price: {e}")

        # Mock 현재가
        return {
            'stock_code': stock_code,
            'current_price': 50000,
            'change': 500,
            'change_rate': 1.0,
            'volume': 1000000
        }