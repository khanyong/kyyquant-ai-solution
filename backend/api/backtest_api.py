"""
백테스트 API 엔드포인트
FastAPI를 사용한 백테스트 실행 서버
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import uuid

# 부모 디렉토리를 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd
import numpy as np

# .env 파일 경로를 명시적으로 지정 (프로젝트 루트에서 찾기)
# backend/api/backtest_api.py -> D:\Dev\auto_stock\.env
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')

# .env 파일 존재 확인
if os.path.exists(env_path):
    print(f"Found .env at: {env_path}")
    load_dotenv(env_path)
else:
    # backend 폴더에서도 시도
    backend_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(backend_env_path):
        print(f"Found .env at: {backend_env_path}")
        load_dotenv(backend_env_path)
    else:
        print(f"WARNING: .env file not found at {env_path} or {backend_env_path}")
        load_dotenv()  # 시스템 환경변수에서 시도

# 환경 변수 확인
print(f"SUPABASE_URL exists: {'SUPABASE_URL' in os.environ}")
print(f"SUPABASE_ANON_KEY exists: {'SUPABASE_ANON_KEY' in os.environ}")

app = FastAPI(title="KyyQuant Backtest API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase 클라이언트
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Supabase configuration missing!")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'Set' if SUPABASE_KEY else 'Not set'}")
    raise ValueError("Please set SUPABASE_URL and SUPABASE_KEY (or SUPABASE_ANON_KEY) in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 요청 모델
class BacktestRequest(BaseModel):
    strategy_id: str
    start_date: str
    end_date: str
    initial_capital: float = 10000000
    commission: float = 0.00015
    slippage: float = 0.001
    data_interval: str = "1d"
    stock_codes: Optional[List[str]] = None
    filter_id: Optional[str] = None  # 저장된 필터 ID
    filter_rules: Optional[Dict[str, Any]] = None  # 필터 규칙
    filtering_mode: Optional[str] = None  # 필터링 모드 (filtering/staged)

class QuickBacktestRequest(BaseModel):
    strategy: Dict[str, Any]
    stock_codes: Optional[List[str]] = None
    
# 백테스트 엔진
class BacktestEngine:
    def __init__(self):
        self.supabase = supabase
        
    async def load_strategy(self, strategy_id: str):
        """전략 로드"""
        response = self.supabase.table('strategies').select('*').eq('id', strategy_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="전략을 찾을 수 없습니다")
        return response.data
    
    async def load_price_data(self, stock_codes: List[str], start_date: str, end_date: str, interval: str = '1d'):
        """가격 데이터 로드 및 리샘플링"""
        price_data = {}
        
        for code in stock_codes:
            response = self.supabase.table('kw_price_daily').select('*').eq(
                'stock_code', code
            ).gte(
                'trade_date', start_date
            ).lte(
                'trade_date', end_date
            ).order('trade_date').execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                # trade_date를 date로 변환
                df['date'] = pd.to_datetime(df['trade_date'])
                df.set_index('date', inplace=True)
                
                # 데이터 간격에 따라 리샘플링
                if interval == '1w':  # 주봉
                    df = self.resample_to_weekly(df)
                elif interval == '1M':  # 월봉
                    df = self.resample_to_monthly(df)
                # 1d는 그대로 사용
                
                price_data[code] = df
                
        return price_data
    
    def resample_to_weekly(self, df: pd.DataFrame):
        """일봉 데이터를 주봉으로 변환"""
        weekly_df = df.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'market_cap': 'last',
            'per': 'last',
            'pbr': 'last',
            'roe': 'last',
            'debt_ratio': 'last'
        }).dropna()
        return weekly_df
    
    def resample_to_monthly(self, df: pd.DataFrame):
        """일봉 데이터를 월봉으로 변환"""
        monthly_df = df.resample('M').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'market_cap': 'last',
            'per': 'last',
            'pbr': 'last',
            'roe': 'last',
            'debt_ratio': 'last'
        }).dropna()
        return monthly_df
    
    def calculate_indicators(self, df: pd.DataFrame, indicators: List[Dict]):
        """지표 계산"""
        print(f"Calculating indicators: {indicators}")
        print(f"DataFrame shape before indicators: {df.shape}")
        print(f"DataFrame columns before indicators: {df.columns.tolist()}")
        
        # 중복 제거를 위한 집합
        calculated_indicators = set()
        
        for indicator in indicators:
            # 프론트엔드에서 보내는 형식 처리
            indicator_id = indicator.get('indicator') or indicator.get('indicatorId')
            
            if indicator_id == 'rsi' and 'rsi' not in calculated_indicators:
                period = indicator.get('params', {}).get('period', 14)
                df['rsi'] = self.calculate_rsi(df['close'], period)
                calculated_indicators.add('rsi')
                print(f"Calculated RSI with period {period}")
                
            elif indicator_id == 'sma':
                period = indicator.get('params', {}).get('period', 20)
                col_name = f'sma_{period}'
                if col_name not in df.columns:
                    df[col_name] = df['close'].rolling(window=period).mean()
                    print(f"Calculated SMA with period {period}")
                    
            elif indicator_id == 'ema':
                period = indicator.get('params', {}).get('period', 20)
                col_name = f'ema_{period}'
                if col_name not in df.columns:
                    df[col_name] = df['close'].ewm(span=period, adjust=False).mean()
                    print(f"Calculated EMA with period {period}")
                    
            elif indicator_id == 'macd' and 'macd' not in calculated_indicators:
                df['macd'], df['macd_signal'], df['macd_hist'] = self.calculate_macd(df['close'])
                calculated_indicators.add('macd')
                print(f"Calculated MACD")
                
            elif indicator_id == 'bb' and 'bb' not in calculated_indicators:
                period = indicator.get('params', {}).get('period', 20)
                std = indicator.get('params', {}).get('std', 2)
                df['bb_upper'], df['bb_middle'], df['bb_lower'] = self.calculate_bollinger(df['close'], period, std)
                calculated_indicators.add('bb')
                print(f"Calculated Bollinger Bands with period {period}, std {std}")
                
            elif indicator_id == 'ichimoku' and 'ichimoku' not in calculated_indicators:
                df = self.calculate_ichimoku(df)
                calculated_indicators.add('ichimoku')
                print(f"Calculated Ichimoku")
        
        print(f"DataFrame columns after indicators: {df.columns.tolist()}")
        return df
    
    def calculate_rsi(self, prices, period=14):
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """MACD 계산"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    def calculate_bollinger(self, prices, period=20, std_dev=2):
        """볼린저밴드 계산"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    def calculate_ichimoku(self, df):
        """일목균형표 계산"""
        # 전환선 (Tenkan-sen) - 9일
        high_9 = df['high'].rolling(window=9).max()
        low_9 = df['low'].rolling(window=9).min()
        df['ichimoku_tenkan'] = (high_9 + low_9) / 2
        
        # 기준선 (Kijun-sen) - 26일
        high_26 = df['high'].rolling(window=26).max()
        low_26 = df['low'].rolling(window=26).min()
        df['ichimoku_kijun'] = (high_26 + low_26) / 2
        
        # 선행스팬 A (Senkou Span A)
        # 백테스트에서는 26일 전에 계산된 값을 현재 사용하므로 shift(26) 사용
        df['ichimoku_senkou_a'] = ((df['ichimoku_tenkan'] + df['ichimoku_kijun']) / 2).shift(26)
        
        # 선행스팬 B (Senkou Span B) 
        # 백테스트에서는 26일 전에 계산된 값을 현재 사용하므로 shift(26) 사용
        high_52 = df['high'].rolling(window=52).max()
        low_52 = df['low'].rolling(window=52).min()
        df['ichimoku_senkou_b'] = ((high_52 + low_52) / 2).shift(26)
        
        # 후행스팬 (Chikou Span) - 26일 과거 종가
        df['ichimoku_chikou'] = df['close'].shift(26)
        
        # NaN 값을 forward fill로 채우기 (옵션)
        df['ichimoku_senkou_a'].fillna(method='ffill', inplace=True)
        df['ichimoku_senkou_b'].fillna(method='ffill', inplace=True)
        
        print(f"Ichimoku calculation complete.")
        print(f"  Total rows: {len(df)}")
        print(f"  Senkou A - NaN count: {df['ichimoku_senkou_a'].isna().sum()}, Valid count: {df['ichimoku_senkou_a'].notna().sum()}")
        print(f"  Senkou B - NaN count: {df['ichimoku_senkou_b'].isna().sum()}, Valid count: {df['ichimoku_senkou_b'].notna().sum()}")
        if df['ichimoku_senkou_a'].notna().any():
            print(f"  Sample senkou_a values: {df['ichimoku_senkou_a'].dropna().head().tolist()}")
        if df['ichimoku_senkou_b'].notna().any():
            print(f"  Sample senkou_b values: {df['ichimoku_senkou_b'].dropna().head().tolist()}")
        
        return df
    
    def evaluate_condition(self, row, condition):
        """조건 평가"""
        # 프론트엔드에서 보내는 조건 형식 처리
        indicator_id = condition.get('indicator') or condition.get('indicatorId')
        operator = condition.get('operator')
        value = condition.get('value', 0)
        
        print(f"Evaluating condition: indicator={indicator_id}, operator={operator}, value={value}")
        print(f"Row columns: {row.index.tolist()}")
        print(f"Row values sample - close: {row.get('close', 'N/A')}, rsi: {row.get('rsi', 'N/A')}")
        
        # 조건이 잘못된 경우
        if not indicator_id or not operator:
            print(f"Invalid condition: {condition}")
            return False
        
        # RSI 조건
        if indicator_id == 'rsi':
            if 'rsi' not in row:
                print(f"RSI not in row, available columns: {row.index.tolist()}")
                return False
            
            rsi_value = row['rsi']
            print(f"RSI value: {rsi_value}, operator: {operator}, compare value: {value}")
            
            # 연산자별 평가
            if operator == '<':
                return rsi_value < value
            elif operator == '>':
                return rsi_value > value
            elif operator == '<=':
                return rsi_value <= value
            elif operator == '>=':
                return rsi_value >= value
            elif operator == '==':
                return abs(rsi_value - value) < 0.01
            # 프리셋 조건들
            elif operator == 'rsi_oversold_30':
                return rsi_value < 30
            elif operator == 'rsi_overbought_70':
                return rsi_value > 70
            elif operator == 'rsi_oversold_20':
                return rsi_value < 20
            elif operator == 'rsi_overbought_80':
                return rsi_value > 80
            elif operator == 'rsi_neutral_40_60':  # RSI 중립 구간
                return 40 <= rsi_value <= 60
            elif operator == 'rsi_bullish_50_70':  # RSI 상승 모멘텀
                return 50 <= rsi_value <= 70
            elif operator == 'rsi_bearish_30_50':  # RSI 하락 모멘텀
                return 30 <= rsi_value <= 50
            elif operator == 'rsi_range':  # 사용자 정의 범위
                min_val = value
                max_val = condition.get('value2', value + 20)
                return min_val <= rsi_value <= max_val
                
        # MACD 조건
        if indicator_id == 'macd' and 'macd' in row:
            if operator == 'macd_above_signal':
                return row['macd'] > row['macd_signal']
            elif operator == 'macd_below_signal':
                return row['macd'] < row['macd_signal']
            elif operator == 'macd_above_zero':
                return row['macd'] > 0
            elif operator == 'macd_below_zero':
                return row['macd'] < 0
            elif operator == 'macd_bullish_divergence':  # 상승 다이버전스
                # 가격은 하락하지만 MACD는 상승
                return row['macd'] > row['macd_signal'] and row['macd'] > 0
            elif operator == 'macd_bearish_divergence':  # 하락 다이버전스
                # 가격은 상승하지만 MACD는 하락
                return row['macd'] < row['macd_signal'] and row['macd'] < 0
                
        # SMA 조건
        if indicator_id == 'sma':
            # SMA 컬럼 찾기 (sma_20, sma_50, sma_200 등)
            sma_columns = [col for col in row.index if col.startswith('sma_')]
            if sma_columns:
                sma_col = sma_columns[0]  # 첫 번째 SMA 사용
                sma_value = row[sma_col]
                close_price = row['close']
                
                print(f"SMA condition - close: {close_price}, {sma_col}: {sma_value}, operator: {operator}")
                
                if operator == 'price_above':
                    return close_price > sma_value
                elif operator == 'price_below':
                    return close_price < sma_value
                elif operator == 'price_above_pct':  # 이평선 위 특정 % 이상
                    pct = value / 100.0
                    return close_price > sma_value * (1 + pct)
                elif operator == 'price_below_pct':  # 이평선 아래 특정 % 이상
                    pct = value / 100.0
                    return close_price < sma_value * (1 - pct)
                elif operator == 'price_near':  # 이평선 근처 (±2%)
                    return abs(close_price - sma_value) / sma_value < 0.02
                elif operator == 'sma_cross_above':
                    # 이전 값과 비교 필요 (추후 구현)
                    return False
                elif operator == 'sma_cross_below':
                    # 이전 값과 비교 필요 (추후 구현)
                    return False
        
        # EMA 조건 (SMA와 동일한 로직)
        if indicator_id == 'ema':
            ema_columns = [col for col in row.index if col.startswith('ema_')]
            if ema_columns:
                ema_col = ema_columns[0]
                ema_value = row[ema_col]
                close_price = row['close']
                
                if operator == 'price_above':
                    return close_price > ema_value
                elif operator == 'price_below':
                    return close_price < ema_value
                elif operator == 'price_above_pct':
                    pct = value / 100.0
                    return close_price > ema_value * (1 + pct)
                elif operator == 'price_below_pct':
                    pct = value / 100.0
                    return close_price < ema_value * (1 - pct)
                elif operator == 'price_near':
                    return abs(close_price - ema_value) / ema_value < 0.02
        
        # Ichimoku 조건
        if indicator_id == 'ichimoku':
            if 'ichimoku_tenkan' in row and 'ichimoku_kijun' in row:
                tenkan = row['ichimoku_tenkan']
                kijun = row['ichimoku_kijun']
                close_price = row['close']
                senkou_a = row.get('ichimoku_senkou_a', float('nan'))
                senkou_b = row.get('ichimoku_senkou_b', float('nan'))
                
                print(f"Ichimoku - tenkan: {tenkan}, kijun: {kijun}, close: {close_price}, operator: {operator}")
                print(f"  Cloud values - senkou_a: {senkou_a}, senkou_b: {senkou_b}")
                if pd.notna(senkou_a) and pd.notna(senkou_b):
                    print(f"  Cloud - senkou_a: {senkou_a}, senkou_b: {senkou_b}, cloud_top: {max(senkou_a, senkou_b)}, cloud_bottom: {min(senkou_a, senkou_b)}")
                else:
                    print(f"  WARNING: Cloud values are NaN - senkou_a: {senkou_a}, senkou_b: {senkou_b}")
                
                if operator == 'tenkan_above_kijun':
                    return tenkan > kijun
                elif operator == 'tenkan_below_kijun':
                    return tenkan < kijun
                elif operator == 'price_above_cloud':
                    if pd.notna(senkou_a) and pd.notna(senkou_b):
                        return close_price > max(senkou_a, senkou_b)
                elif operator == 'price_below_cloud':
                    if pd.notna(senkou_a) and pd.notna(senkou_b):
                        return close_price < min(senkou_a, senkou_b)
                elif operator == 'cloud_breakout_up':
                    # 구름대 상향 돌파: 가격이 구름대 위에 있어야 함
                    if pd.notna(senkou_a) and pd.notna(senkou_b):
                        cloud_top = max(senkou_a, senkou_b)
                        result = close_price > cloud_top
                        print(f"  Cloud breakout up check: close({close_price}) > cloud_top({cloud_top}) = {result}")
                        return result
                    return False
                elif operator == 'cloud_breakout_down':
                    # 구름대 하향 돌파: 가격이 구름대 아래에 있어야 함
                    if pd.notna(senkou_a) and pd.notna(senkou_b):
                        cloud_bottom = min(senkou_a, senkou_b)
                        result = close_price < cloud_bottom
                        print(f"  Cloud breakout down check: close({close_price}) < cloud_bottom({cloud_bottom}) = {result}")
                        return result
                    return False
                elif operator == 'price_in_cloud':
                    # 가격이 구름대 내부에 있는지
                    if pd.notna(senkou_a) and pd.notna(senkou_b):
                        cloud_top = max(senkou_a, senkou_b)
                        cloud_bottom = min(senkou_a, senkou_b)
                        return cloud_bottom <= close_price <= cloud_top
                    return False
                elif operator == 'bullish_cloud':
                    # 상승 구름: senkou_a가 senkou_b 위에 있음
                    if pd.notna(senkou_a) and pd.notna(senkou_b):
                        return senkou_a > senkou_b
                    return False
                elif operator == 'bearish_cloud':
                    # 하락 구름: senkou_b가 senkou_a 위에 있음
                    if pd.notna(senkou_a) and pd.notna(senkou_b):
                        return senkou_b > senkou_a
                    return False
                elif operator == 'tenkan_cross_kijun_up':
                    # 크로스 판단은 이전 값과 비교 필요 (추후 구현)
                    return False
                elif operator == 'tenkan_cross_kijun_down':
                    # 크로스 판단은 이전 값과 비교 필요 (추후 구현)
                    return False
        
        # 볼린저밴드 조건
        if indicator_id == 'bb' and 'bb_upper' in row:
            close_price = row['close']
            if operator == 'price_above_upper':
                return close_price > row['bb_upper']
            elif operator == 'price_below_lower':
                return close_price < row['bb_lower']
            elif operator == 'price_above_middle':
                return close_price > row['bb_middle']
            elif operator == 'price_below_middle':
                return close_price < row['bb_middle']
            elif operator == 'price_in_band':  # 밴드 내부
                return row['bb_lower'] <= close_price <= row['bb_upper']
            elif operator == 'band_squeeze':  # 밴드 수축 (변동성 감소)
                band_width = (row['bb_upper'] - row['bb_lower']) / row['bb_middle']
                return band_width < 0.1  # 10% 미만
            elif operator == 'band_expansion':  # 밴드 확장 (변동성 증가)
                band_width = (row['bb_upper'] - row['bb_lower']) / row['bb_middle']
                return band_width > 0.2  # 20% 이상
        
        # Stochastic 조건
        if indicator_id == 'stochastic':
            if 'stoch_k' in row and 'stoch_d' in row:
                stoch_k = row['stoch_k']
                stoch_d = row['stoch_d']
                
                if operator == 'k_above_d':
                    return stoch_k > stoch_d
                elif operator == 'k_below_d':
                    return stoch_k < stoch_d
                elif operator == 'oversold':
                    return stoch_k < 20 and stoch_d < 20
                elif operator == 'overbought':
                    return stoch_k > 80 and stoch_d > 80
                elif operator == 'oversold_20':
                    return stoch_k < 20
                elif operator == 'overbought_80':
                    return stoch_k > 80
                elif operator == 'neutral_zone':
                    return 20 <= stoch_k <= 80
        
        # ADX 조건 (추세 강도)
        if indicator_id == 'adx' and 'adx' in row:
            adx_value = row['adx']
            if operator == 'strong_trend':
                return adx_value > 25
            elif operator == 'weak_trend':
                return adx_value < 25
            elif operator == 'very_strong_trend':
                return adx_value > 50
            elif operator == 'no_trend':
                return adx_value < 20
            elif operator == 'trend_developing':
                return 20 <= adx_value <= 40
        
        # CCI 조건
        if indicator_id == 'cci' and 'cci' in row:
            cci_value = row['cci']
            if operator == 'oversold':
                return cci_value < -100
            elif operator == 'overbought':
                return cci_value > 100
            elif operator == 'oversold_200':
                return cci_value < -200
            elif operator == 'overbought_200':
                return cci_value > 200
            elif operator == 'neutral':
                return -100 <= cci_value <= 100
        
        # Williams %R 조건
        if indicator_id == 'williams_r' and 'williams_r' in row:
            wr_value = row['williams_r']
            if operator == 'oversold':
                return wr_value < -80
            elif operator == 'overbought':
                return wr_value > -20
            elif operator == 'oversold_90':
                return wr_value < -90
            elif operator == 'overbought_10':
                return wr_value > -10
        
        # OBV 조건
        if indicator_id == 'obv' and 'obv' in row:
            obv_value = row['obv']
            if operator == 'increasing':
                # 이전 값과 비교 필요 (간단히 양수 체크)
                return obv_value > 0
            elif operator == 'decreasing':
                return obv_value < 0
        
        # VWAP 조건
        if indicator_id == 'vwap' and 'vwap' in row:
            vwap_value = row['vwap']
            close_price = row['close']
            if operator == 'price_above':
                return close_price > vwap_value
            elif operator == 'price_below':
                return close_price < vwap_value
            elif operator == 'price_near':
                return abs(close_price - vwap_value) / vwap_value < 0.01
        
        # Volume 조건 (거래량)
        if indicator_id == 'volume' and 'volume' in row:
            volume = row['volume']
            # 평균 거래량 계산이 필요하지만, 간단히 임계값 사용
            if operator == 'high_volume':
                return volume > value if value else volume > 1000000
            elif operator == 'low_volume':
                return volume < value if value else volume < 100000
            elif operator == 'volume_spike':
                # 평균 대비 2배 이상 (추후 구현)
                return volume > value * 2 if value else False
                
        return False
    
    def evaluate_stage_conditions(self, row, stages):
        """3단계 조건 평가"""
        print(f"  Evaluating {len(stages)} stages")
        
        for stage_idx, stage in enumerate(stages):
            if not stage.get('enabled', True):
                print(f"  Stage {stage_idx} is disabled, skipping")
                continue
            
            indicators = stage.get('indicators', [])
            if not indicators:
                print(f"  Stage {stage_idx} has no indicators, skipping")
                continue
                
            stage_result = False
            pass_all = stage.get('passAllRequired', True)
            print(f"  Stage {stage_idx}: {len(indicators)} indicators, pass_all={pass_all}")
            
            for ind_idx, indicator in enumerate(indicators):
                condition_met = self.evaluate_condition(row, indicator)
                indicator_id = indicator.get('indicator') or indicator.get('indicatorId')
                operator = indicator.get('operator')
                print(f"    Indicator {ind_idx}: {indicator_id} {operator} = {condition_met}")
                
                if pass_all:
                    # AND 조건
                    if not condition_met:
                        print(f"  Stage {stage_idx} failed (AND condition not met)")
                        return False
                    stage_result = True
                else:
                    # OR 조건
                    if condition_met:
                        stage_result = True
                        print(f"  Stage {stage_idx} passed (OR condition met)")
                        break
            
            if not stage_result:
                print(f"  Stage {stage_idx} failed (no conditions met)")
                return False
        
        print(f"  All stages passed!")
        return True
    
    async def run_backtest(self, strategy, price_data, initial_capital, commission, slippage, data_interval='1d'):
        """백테스트 실행"""
        print(f"Running backtest with data interval: {data_interval}")
        results = {
            'trades': [],
            'daily_returns': [],
            'positions': [],
            'final_capital': initial_capital,
            'total_return': 0,
            'max_drawdown': 0,
            'win_rate': 0,
            'total_trades': 0,
            'data_interval': data_interval
        }
        
        capital = initial_capital
        position = None
        max_capital = capital
        trades = []
        
        # 전략 설정 파싱
        config = strategy.get('config', {})
        print(f"Strategy config: {config}")
        use_stage_based = config.get('useStageBasedStrategy', False)
        print(f"Using stage-based strategy: {use_stage_based}")
        
        if use_stage_based:
            buy_stages = config.get('buyStageStrategy', {}).get('stages', [])
            sell_stages = config.get('sellStageStrategy', {}).get('stages', [])
            print(f"Buy stages count: {len(buy_stages)}")
            print(f"Sell stages count: {len(sell_stages)}")
            
            # 스테이지 전략이 비어있는지 확인
            if not buy_stages or not sell_stages:
                error_msg = "전략에 매수/매도 조건이 설정되지 않았습니다. 전략 빌더에서 조건을 설정한 후 다시 시도해주세요."
                print(f"ERROR: {error_msg}")
                results['error'] = error_msg
                results['total_trades'] = 0
                results['total_return'] = 0
                results['win_rate'] = 0
                return results
        else:
            buy_conditions = config.get('buyConditions', [])
            sell_conditions = config.get('sellConditions', [])
            print(f"Buy conditions: {buy_conditions}")
            print(f"Sell conditions: {sell_conditions}")
            
            # 조건이 없는 경우 에러 반환
            if not buy_conditions or not sell_conditions:
                error_msg = "전략에 매수/매도 조건이 설정되지 않았습니다. 전략 빌더에서 조건을 설정한 후 다시 시도해주세요."
                print(f"ERROR: {error_msg}")
                results['error'] = error_msg
                results['total_trades'] = 0
                results['total_return'] = 0
                results['win_rate'] = 0
                return results
        
        # 각 종목별 백테스트
        last_df = None  # 마지막 데이터프레임 저장용
        for stock_code, df in price_data.items():
            last_df = df  # 현재 처리 중인 데이터프레임 저장
            # 지표 계산
            indicators = []
            if use_stage_based:
                print(f"Processing stage-based strategy for {stock_code}")
                for stage_type, stages in [('buy', buy_stages), ('sell', sell_stages)]:
                    for stage_idx, stage in enumerate(stages):
                        for ind in stage.get('indicators', []):
                            # 지표 정보 로깅
                            indicator_id = ind.get('indicator') or ind.get('indicatorId')
                            print(f"Processing {stage_type} stage {stage_idx} indicator: {indicator_id}")
                            
                            # params가 없을 경우 기본값 추가
                            if 'params' not in ind:
                                ind['params'] = {}
                                # SMA/EMA의 경우 기본 period 설정
                                if indicator_id in ['sma', 'ema']:
                                    ind['params']['period'] = 20  # 기본값 20
                                    print(f"Added default period 20 for {indicator_id}")
                            indicators.append(ind)
            else:
                # 조건에서 지표 추출
                for cond in buy_conditions + sell_conditions:
                    # 프론트엔드에서 보내는 형식에 맞게 처리
                    indicator_name = cond.get('indicator') or cond.get('indicatorId') or 'rsi'
                    indicators.append({
                        'indicator': indicator_name,
                        'indicatorId': indicator_name,  # 두 형식 모두 지원
                        'params': cond.get('params', {})
                    })
                print(f"Extracted indicators from conditions: {indicators}")
            
            df = self.calculate_indicators(df, indicators)
            
            # 백테스트 실행
            print(f"Processing {len(df)} days for stock {stock_code}")
            print(f"DataFrame columns available: {df.columns.tolist()}")
            
            # 첫 번째 행의 값 확인
            if len(df) > 0:
                first_row = df.iloc[0]
                print(f"First row sample values:")
                for col in df.columns:
                    if col in ['close', 'rsi', 'sma_20', 'ichimoku_tenkan', 'ichimoku_kijun']:
                        val = first_row[col]
                        print(f"  {col}: {val}")
            
            for i, (date, row) in enumerate(df.iterrows()):
                # 매수 신호 체크
                if position is None:
                    buy_signal = False
                    
                    if use_stage_based:
                        if i < 3:  # 처음 3개 행에서 로그
                            print(f"\n=== Evaluating buy conditions for {stock_code} on {date} ===")
                            print(f"Row data - close: {row['close']}")
                            for col in row.index:
                                if 'ichimoku' in col or 'rsi' in col or 'sma' in col:
                                    print(f"  {col}: {row[col]}")
                        
                        buy_signal = self.evaluate_stage_conditions(row, buy_stages)
                        
                        if i < 3:
                            print(f"Buy signal result: {buy_signal}")
                    else:
                        # 단순 조건 평가
                        for condition in buy_conditions:
                            condition_result = self.evaluate_condition(row, condition)
                            if i == 0:  # 첫 번째 행에서만 로그
                                print(f"Condition {condition} evaluated to: {condition_result}")
                            if condition_result:
                                buy_signal = True
                                break
                    
                    if buy_signal:
                        print(f"BUY SIGNAL TRIGGERED for {stock_code} on {date}")
                        # 매수 실행
                        shares = int(capital * 0.95 / row['close'])  # 95% 자금 사용
                        if shares > 0:
                            cost = shares * row['close'] * (1 + commission + slippage)
                            if cost <= capital:
                                position = {
                                    'stock_code': stock_code,
                                    'entry_date': date,
                                    'entry_price': row['close'],
                                    'shares': shares,
                                    'cost': cost
                                }
                                capital -= cost
                                trades.append({
                                    'date': date.isoformat(),
                                    'stock_code': stock_code,
                                    'action': 'BUY',
                                    'price': row['close'],
                                    'quantity': shares,
                                    'amount': cost
                                })
                
                # 매도 신호 체크
                elif position is not None:
                    sell_signal = False
                    
                    if use_stage_based:
                        sell_signal = self.evaluate_stage_conditions(row, sell_stages)
                    else:
                        for condition in sell_conditions:
                            if self.evaluate_condition(row, condition):
                                sell_signal = True
                                break
                    
                    # 손절/익절 체크
                    if position:
                        pnl_pct = (row['close'] - position['entry_price']) / position['entry_price'] * 100
                        risk_mgmt = config.get('riskManagement', {})
                        
                        if risk_mgmt.get('stopLoss') and pnl_pct <= -abs(risk_mgmt['stopLoss']):
                            sell_signal = True
                        elif risk_mgmt.get('takeProfit') and pnl_pct >= risk_mgmt['takeProfit']:
                            sell_signal = True
                    
                    if sell_signal and position:
                        # 매도 실행
                        proceeds = position['shares'] * row['close'] * (1 - commission - slippage)
                        capital += proceeds
                        
                        profit = proceeds - position['cost']
                        trades.append({
                            'date': date.isoformat(),
                            'stock_code': stock_code,
                            'action': 'SELL',
                            'price': row['close'],
                            'quantity': position['shares'],
                            'amount': proceeds,
                            'profit': profit
                        })
                        
                        position = None
                
                # 최대 자본 및 드로다운 계산
                current_value = capital
                if position:
                    current_value += position['shares'] * row['close']
                
                if current_value > max_capital:
                    max_capital = current_value
                
                drawdown = (current_value - max_capital) / max_capital * 100
                if drawdown < results['max_drawdown']:
                    results['max_drawdown'] = drawdown
        
        # 최종 결과 계산
        final_value = capital
        if position and last_df is not None:
            # 포지션 청산 - 해당 종목의 마지막 가격 사용
            # position이 있다면 해당 종목의 마지막 데이터를 찾아야 함
            if position['stock_code'] in price_data:
                stock_df = price_data[position['stock_code']]
                last_price = stock_df.iloc[-1]['close'] if len(stock_df) > 0 else 0
            else:
                last_price = last_df.iloc[-1]['close'] if len(last_df) > 0 else 0
            
            position_value = position['shares'] * last_price
            final_value += position_value
            print(f"Open position at end: {position['stock_code']} - {position['shares']} shares @ {last_price} = {position_value}")
        
        print(f"=== Final Calculation ===")
        print(f"Initial capital: {initial_capital}")
        print(f"Current cash: {capital}")
        print(f"Final value (cash + positions): {final_value}")
        print(f"Return calculation: ({final_value} - {initial_capital}) / {initial_capital} * 100")
        
        results['trades'] = trades
        results['final_capital'] = final_value
        results['total_return'] = ((final_value - initial_capital) / initial_capital) * 100
        results['total_trades'] = len([t for t in trades if t['action'] == 'BUY'])
        
        # 승률 및 거래 통계 계산
        wins = len([t for t in trades if t.get('profit', 0) > 0])
        losses = len([t for t in trades if t.get('profit', 0) < 0])
        total_closed = len([t for t in trades if t['action'] == 'SELL'])
        
        results['win_rate'] = (wins / total_closed * 100) if total_closed > 0 else 0
        results['profitable_trades'] = wins
        results['losing_trades'] = losses
        
        print(f"Backtest completed - Total trades: {len(trades)}, Buy trades: {results['total_trades']}, Sell trades: {total_closed}")
        print(f"Final return: {results['total_return']:.2f}%, Win rate: {results['win_rate']:.2f}%")
        print(f"=======================")
        
        return results

# 백테스트 엔진 인스턴스
engine = BacktestEngine()

@app.get("/")
async def root():
    return {"message": "KyyQuant Backtest API", "status": "online"}

@app.post("/api/backtest/run")
async def run_backtest(request: BacktestRequest):
    """백테스트 실행"""
    try:
        print(f"Received backtest request: {request.dict()}")
        print(f"Strategy ID: {request.strategy_id}")
        print(f"Stock codes: {request.stock_codes[:5] if request.stock_codes else 'None'}")  # 처음 5개만 출력
        # 전략 로드 및 사용자 확인
        strategy = await engine.load_strategy(request.strategy_id)
        
        # 전략 내용 상세 로그
        print(f"Loaded strategy: {strategy.get('name')}")
        print(f"Strategy config type: {type(strategy.get('config'))}")
        strategy_config = strategy.get('config', {})
        if isinstance(strategy_config, str):
            import json
            try:
                strategy_config = json.loads(strategy_config)
                strategy['config'] = strategy_config
                print("Strategy config was JSON string, parsed successfully")
            except:
                print("Failed to parse strategy config JSON string")
        
        print(f"Strategy config: {strategy_config}")
        
        # 조건 확인
        if isinstance(strategy_config, dict):
            use_stage = strategy_config.get('useStageBasedStrategy', False)
            if use_stage:
                buy_stages = strategy_config.get('buyStageStrategy', {}).get('stages', [])
                sell_stages = strategy_config.get('sellStageStrategy', {}).get('stages', [])
                print(f"Stage-based strategy - Buy stages: {len(buy_stages)}, Sell stages: {len(sell_stages)}")
                if buy_stages:
                    print(f"First buy stage: {buy_stages[0]}")
                if sell_stages:
                    print(f"First sell stage: {sell_stages[0]}")
            else:
                buy_conds = strategy_config.get('buyConditions', [])
                sell_conds = strategy_config.get('sellConditions', [])
                print(f"Simple strategy - Buy conditions: {len(buy_conds)}, Sell conditions: {len(sell_conds)}")
                if buy_conds:
                    print(f"Buy conditions: {buy_conds}")
                if sell_conds:
                    print(f"Sell conditions: {sell_conds}")
        
        # 전략의 user_id 추출
        strategy_user_id = strategy.get('user_id')
        
        # 종목 코드 설정
        stock_codes = request.stock_codes
        filter_id = request.filter_id
        
        print(f"Filter ID from request: {filter_id}")
        print(f"Stock codes from request: {stock_codes[:5] if stock_codes else 'None'}")
        
        if not stock_codes:
            if filter_id:
                # kw_investment_filters 테이블에서 필터링된 종목 가져오기
                print(f"Loading stocks from filter ID: {filter_id}")
                try:
                    filter_response = supabase.table('kw_investment_filters').select('filtered_stocks').eq('id', filter_id).single().execute()
                    print(f"Filter response: {filter_response}")
                    
                    if filter_response.data and filter_response.data.get('filtered_stocks'):
                        filtered_stocks = filter_response.data['filtered_stocks']
                        print(f"Filtered stocks type: {type(filtered_stocks)}")
                        print(f"Filtered stocks content (first 3): {filtered_stocks[:3] if isinstance(filtered_stocks, list) else filtered_stocks}")
                        
                        # filtered_stocks는 JSON 배열로 저장되어 있음
                        if isinstance(filtered_stocks, list):
                            # 종목 코드 추출 (다양한 형식 지원)
                            stock_codes = []
                            for stock in filtered_stocks:
                                if isinstance(stock, str):
                                    stock_codes.append(stock)
                                elif isinstance(stock, dict):
                                    code = stock.get('code') or stock.get('stock_code') or stock.get('symbol')
                                    if code:
                                        stock_codes.append(code)
                                else:
                                    print(f"Unknown stock format: {type(stock)} - {stock}")
                            print(f"Successfully loaded {len(stock_codes)} stocks from filter")
                            if stock_codes:
                                print(f"Sample stock codes: {stock_codes[:5]}")
                        else:
                            print(f"Invalid filtered_stocks format: {type(filtered_stocks)}")
                            stock_codes = []
                    else:
                        print(f"No stocks found in filter {filter_id} - Response data: {filter_response.data}")
                        stock_codes = []
                except Exception as e:
                    print(f"Error loading filter {filter_id}: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    stock_codes = []
            else:
                # 최근 사용한 필터에서 종목 가져오기 (사용자가 있는 경우)
                if strategy_user_id:
                    print(f"Loading most recent filter for user {strategy_user_id}")
                    recent_filter = supabase.table('kw_investment_filters').select('filtered_stocks').eq('user_id', strategy_user_id).eq('is_active', True).order('created_at', desc=False).limit(1).execute()
                    
                    if recent_filter.data and recent_filter.data[0].get('filtered_stocks'):
                        filtered_stocks = recent_filter.data[0]['filtered_stocks']
                        if isinstance(filtered_stocks, list):
                            stock_codes = []
                            for stock in filtered_stocks:
                                if isinstance(stock, str):
                                    stock_codes.append(stock)
                                elif isinstance(stock, dict):
                                    code = stock.get('code') or stock.get('stock_code') or stock.get('symbol')
                                    if code:
                                        stock_codes.append(code)
                            print(f"Loaded {len(stock_codes)} stocks from recent filter")
                        else:
                            stock_codes = []
                    else:
                        print("No recent filters found for user")
                        stock_codes = []
                else:
                    print("No user ID available, cannot load filters")
                    stock_codes = []
        
        if not stock_codes:
            raise HTTPException(status_code=400, detail="종목 코드가 제공되지 않았습니다. 투자설정에서 필터를 적용하고 저장한 후 다시 시도하세요.")
        
        # 가격 데이터 로드 (데이터 간격 포함)
        price_data = await engine.load_price_data(
            stock_codes, 
            request.start_date, 
            request.end_date,
            request.data_interval
        )
        
        if not price_data:
            raise HTTPException(status_code=404, detail="가격 데이터를 찾을 수 없습니다")
        
        # 백테스트 실행
        results = await engine.run_backtest(
            strategy,
            price_data,
            request.initial_capital,
            request.commission,
            request.slippage,
            request.data_interval
        )
        
        # 전략 조건 에러 체크
        if 'error' in results:
            raise HTTPException(status_code=400, detail=results['error'])
        
        # 결과 저장
        backtest_id = str(uuid.uuid4())
        
        # 백테스트 설정 정보 포함
        # 전략의 매수/매도 조건 추출
        strategy_config = strategy.get('config', {})
        buy_conditions = []
        sell_conditions = []
        
        if isinstance(strategy_config, dict):
            # 매수 조건 추출
            if 'buyConditions' in strategy_config:
                buy_conditions = strategy_config['buyConditions']
            elif 'buy_conditions' in strategy_config:
                buy_conditions = strategy_config['buy_conditions']
            
            # 매도 조건 추출
            if 'sellConditions' in strategy_config:
                sell_conditions = strategy_config['sellConditions']
            elif 'sell_conditions' in strategy_config:
                sell_conditions = strategy_config['sell_conditions']
        
        backtest_config = {
            'data_interval': request.data_interval,
            'commission': request.commission,
            'slippage': request.slippage,
            'filter_rules': getattr(request, 'filter_rules', None),
            'filter_id': getattr(request, 'filter_id', None),
            'stock_codes': stock_codes[:20] if stock_codes else [],  # 처음 20개만 저장 (공간 절약)
            'total_stocks': len(stock_codes) if stock_codes else 0,
            'strategy_config': {
                'buyConditions': buy_conditions,
                'sellConditions': sell_conditions,
                **strategy_config  # 나머지 설정도 포함
            },
            'strategy_type': strategy.get('type', 'Unknown'),
            'strategy_description': strategy.get('description', ''),
            'filtering_mode': getattr(request, 'filtering_mode', None)  # 필터링 모드 추가
        }
        
        # backtest_results 테이블에 저장
        result_data = {
            'id': backtest_id,
            'strategy_id': request.strategy_id,
            'strategy_name': strategy.get('name', 'Unknown'),
            'user_id': strategy_user_id,  # 전략 소유자의 ID 저장
            'start_date': request.start_date,
            'end_date': request.end_date,
            'initial_capital': request.initial_capital,
            'final_capital': results['final_capital'],
            'total_return': results['total_return'],
            'max_drawdown': results['max_drawdown'],
            'win_rate': results['win_rate'],
            'total_trades': results['total_trades'],
            'profitable_trades': results.get('profitable_trades', 0),
            'losing_trades': results.get('losing_trades', 0),
            'results_data': {
                **results,
                'backtest_config': backtest_config  # 백테스트 설정 포함
            },
            'trade_details': results.get('trades', []),  # JSONB 형식으로 거래 내역 저장
            'daily_returns': results.get('daily_returns', [])  # JSONB 형식으로 일간 수익률 저장
        }
        
        supabase.table('backtest_results').insert(result_data).execute()
        
        # 거래 내역 저장
        if results['trades']:
            trade_records = [
                {
                    'backtest_id': backtest_id,
                    'trade_date': trade['date'],
                    'stock_code': trade['stock_code'],
                    'action': trade['action'],
                    'price': trade['price'],
                    'quantity': trade['quantity'],
                    'amount': trade['amount'],
                    'profit_loss': trade.get('profit', 0)
                }
                for trade in results['trades']
            ]
            supabase.table('backtest_trades').insert(trade_records).execute()
        
        return {
            'backtest_id': backtest_id,
            'status': 'completed',
            'results': {
                'total_return': round(results['total_return'], 2),
                'win_rate': round(results['win_rate'], 2),
                'max_drawdown': round(results['max_drawdown'], 2),
                'total_trades': results['total_trades'],
                'final_capital': round(results['final_capital'], 0)
            }
        }
        
    except Exception as e:
        import traceback
        print(f"ERROR in run_backtest: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backtest/quick")
async def run_quick_backtest(request: QuickBacktestRequest):
    """퀵 백테스트 (1년)"""
    try:
        # 날짜 설정 (최근 1년)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # 종목 설정
        stock_codes = request.stock_codes or ['005930']  # 기본: 삼성전자
        
        # 가격 데이터 로드 (일봉 기본)
        price_data = await engine.load_price_data(
            stock_codes,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            '1d'  # 퀵 백테스트는 일봉 기본
        )
        
        # 백테스트 실행
        results = await engine.run_backtest(
            request.strategy,
            price_data,
            10000000,  # 1천만원
            0.00015,   # 수수료 0.015%
            0.001      # 슬리피지 0.1%
        )
        
        return {
            'returns': round(results['total_return'], 1),
            'winRate': round(results['win_rate'], 1),
            'maxDrawdown': round(results['max_drawdown'], 1),
            'trades': results['total_trades']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest/results/user/{user_id}")
async def get_user_backtest_results(user_id: str):
    """사용자별 백테스트 결과 목록 조회"""
    try:
        response = supabase.table('backtest_results').select('*').eq('user_id', user_id).order('created_at', desc=False).execute()
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest/results/{backtest_id}")
async def get_backtest_result(backtest_id: str):
    """백테스트 결과 조회"""
    try:
        response = supabase.table('backtest_results').select('*').eq('id', backtest_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="백테스트 결과를 찾을 수 없습니다")
        
        return response.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/backtest/trades/{backtest_id}")
async def get_backtest_trades(backtest_id: str):
    """백테스트 거래 내역 조회"""
    try:
        response = supabase.table('backtest_trades').select('*').eq('backtest_id', backtest_id).order('trade_date').execute()
        return response.data or []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class StockHistoricalRequest(BaseModel):
    start_date: str
    end_date: str
    interval: str = "1d"

@app.post("/api/stock/historical/{stock_code}")
async def get_stock_historical_data(stock_code: str, request: StockHistoricalRequest):
    """
    종목의 과거 가격 데이터 조회
    3-tier 데이터 소싱 전략의 최종 API 엔드포인트
    """
    try:
        print(f"Fetching historical data for {stock_code} from {request.start_date} to {request.end_date}")
        
        # 1. Supabase에서 데이터 조회 시도 (kw_price_daily 테이블 사용)
        response = supabase.table('kw_price_daily').select('*').eq(
            'stock_code', stock_code
        ).gte(
            'trade_date', request.start_date
        ).lte(
            'trade_date', request.end_date
        ).order('trade_date').execute()
        
        if response.data and len(response.data) > 0:
            print(f"Found {len(response.data)} records in database for {stock_code}")
            return {
                "status": "success",
                "source": "database",
                "data": response.data
            }
        
        # 2. 외부 API에서 데이터 가져오기 (예: yfinance, KIS API 등)
        # 여기서는 시뮬레이션용 더미 데이터 생성
        print(f"No data in database for {stock_code}, generating sample data...")
        
        # 날짜 범위 생성
        start = pd.to_datetime(request.start_date)
        end = pd.to_datetime(request.end_date)
        dates = pd.date_range(start=start, end=end, freq='B')  # Business days only
        
        # 더미 데이터 생성 (실제로는 외부 API 호출)
        sample_data = []
        base_price = 50000  # 기준 가격
        
        for date in dates:
            # 랜덤 변동성 추가
            change = np.random.randn() * 0.02  # 2% 변동성
            close_price = base_price * (1 + change)
            
            daily_data = {
                "stock_code": stock_code,
                "stock_name": f"종목_{stock_code}",
                "trade_date": date.strftime('%Y-%m-%d'),  # trade_date 컬럼명 사용
                "open": int(close_price * (1 + np.random.uniform(-0.01, 0.01))),
                "high": int(close_price * (1 + np.random.uniform(0, 0.02))),
                "low": int(close_price * (1 + np.random.uniform(-0.02, 0))),
                "close": int(close_price),
                "volume": int(np.random.uniform(100000, 1000000)),
                "change_rate": change,
                "market_cap": int(close_price * 10000000),
                "per": round(np.random.uniform(5, 30), 2),
                "pbr": round(np.random.uniform(0.5, 3), 2),
                "roe": round(np.random.uniform(5, 20), 2),
                "debt_ratio": round(np.random.uniform(30, 150), 2)
            }
            sample_data.append(daily_data)
            base_price = close_price  # 다음 날 기준 가격 업데이트
        
        # 3. 가져온 데이터를 Supabase에 저장 (캐싱)
        if sample_data:
            try:
                # upsert를 사용하여 중복 방지 (kw_price_daily 테이블 사용)
                supabase.table('kw_price_daily').upsert(
                    sample_data,
                    on_conflict='stock_code,trade_date'  # 복합 유니크 키
                ).execute()
                print(f"Saved {len(sample_data)} records to database for {stock_code}")
            except Exception as save_error:
                print(f"Error saving to database: {save_error}")
                # 저장 실패해도 데이터는 반환
        
        return {
            "status": "success",
            "source": "api",
            "data": sample_data
        }
        
    except Exception as e:
        print(f"Error fetching historical data for {stock_code}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)