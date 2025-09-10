"""
통합 지표 처리 모듈
모든 지표 ID 형식을 표준화하고 처리
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class IndicatorProcessor:
    """지표 처리 클래스"""
    
    @staticmethod
    def normalize_indicator_id(indicator_id: str) -> str:
        """지표 ID를 표준화"""
        if not indicator_id:
            return ""
        
        indicator_id = indicator_id.lower()
        
        # RSI 변형들
        if any(x in indicator_id for x in ['rsi', 'relative']):
            return 'rsi'
        
        # MACD 변형들
        if any(x in indicator_id for x in ['macd', 'convergence']):
            return 'macd'
        
        # Bollinger Bands 변형들
        if any(x in indicator_id for x in ['bb', 'bollinger', 'price']):
            return 'bb'
        
        # SMA 변형들
        if 'sma' in indicator_id or 'simple' in indicator_id:
            return 'sma'
        
        # EMA 변형들
        if 'ema' in indicator_id or 'exponential' in indicator_id:
            return 'ema'
        
        # Ichimoku 변형들
        if 'ichimoku' in indicator_id or 'cloud' in indicator_id:
            return 'ichimoku'
        
        # Stochastic 변형들
        if 'stoch' in indicator_id:
            return 'stochastic'
        
        # ADX 변형들
        if 'adx' in indicator_id:
            return 'adx'
        
        # CCI 변형들
        if 'cci' in indicator_id:
            return 'cci'
        
        # Williams %R 변형들
        if 'williams' in indicator_id:
            return 'williams_r'
        
        # OBV 변형들
        if 'obv' in indicator_id:
            return 'obv'
        
        # VWAP 변형들
        if 'vwap' in indicator_id:
            return 'vwap'
        
        # Volume 변형들
        if 'volume' in indicator_id or 'vol' in indicator_id:
            return 'volume'
        
        return indicator_id
    
    @staticmethod
    def extract_period(indicator_id: str) -> int:
        """지표 ID에서 기간 추출 (예: rsi_14 -> 14)"""
        import re
        match = re.search(r'_(\d+)', indicator_id)
        if match:
            return int(match.group(1))
        
        # 기본값
        defaults = {
            'rsi': 14,
            'sma': 20,
            'ema': 20,
            'bb': 20,
            'stochastic': 14,
            'cci': 20,
            'williams_r': 14,
            'adx': 14
        }
        
        normalized = IndicatorProcessor.normalize_indicator_id(indicator_id)
        return defaults.get(normalized, 20)
    
    @staticmethod
    def get_required_indicators(conditions: List[Dict]) -> List[Dict]:
        """조건에서 필요한 지표 추출"""
        indicators = {}
        
        for cond in conditions:
            indicator_id = cond.get('indicator') or cond.get('indicatorId')
            if not indicator_id:
                continue
            
            normalized = IndicatorProcessor.normalize_indicator_id(indicator_id)
            period = IndicatorProcessor.extract_period(indicator_id)
            
            # 중복 제거를 위해 딕셔너리 사용
            key = f"{normalized}_{period}"
            if key not in indicators:
                indicators[key] = {
                    'indicator': normalized,
                    'params': {'period': period}
                }
        
        return list(indicators.values())
    
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame, indicators: List[Dict]) -> pd.DataFrame:
        """모든 지표 계산"""
        for indicator in indicators:
            ind_type = indicator.get('indicator')
            params = indicator.get('params', {})
            
            if ind_type == 'rsi':
                period = params.get('period', 14)
                df['rsi'] = IndicatorProcessor.calculate_rsi(df['close'], period)
                
            elif ind_type == 'macd':
                df['macd'], df['macd_signal'], df['macd_hist'] = IndicatorProcessor.calculate_macd(df['close'])
                
            elif ind_type == 'bb':
                period = params.get('period', 20)
                std = params.get('std', 2)
                df['bb_upper'], df['bb_middle'], df['bb_lower'] = IndicatorProcessor.calculate_bollinger(df['close'], period, std)
                
            elif ind_type == 'sma':
                period = params.get('period', 20)
                df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
                
            elif ind_type == 'ema':
                period = params.get('period', 20)
                df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
                
            elif ind_type == 'ichimoku':
                df = IndicatorProcessor.calculate_ichimoku(df)
                
            elif ind_type == 'stochastic':
                period = params.get('period', 14)
                df['stoch_k'], df['stoch_d'] = IndicatorProcessor.calculate_stochastic(df, period)
                
            elif ind_type == 'adx':
                period = params.get('period', 14)
                df['adx'] = IndicatorProcessor.calculate_adx(df, period)
                
            elif ind_type == 'cci':
                period = params.get('period', 20)
                df['cci'] = IndicatorProcessor.calculate_cci(df, period)
                
            elif ind_type == 'williams_r':
                period = params.get('period', 14)
                df['williams_r'] = IndicatorProcessor.calculate_williams_r(df, period)
                
            elif ind_type == 'obv':
                df['obv'] = IndicatorProcessor.calculate_obv(df)
                
            elif ind_type == 'vwap':
                df['vwap'] = IndicatorProcessor.calculate_vwap(df)
        
        return df
    
    # 개별 지표 계산 함수들
    @staticmethod
    def calculate_rsi(prices, period=14):
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        """MACD 계산"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist
    
    @staticmethod
    def calculate_bollinger(prices, period=20, std_dev=2):
        """볼린저밴드 계산"""
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        return upper, middle, lower
    
    @staticmethod
    def calculate_stochastic(df, period=14):
        """스토캐스틱 계산"""
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        k = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d = k.rolling(window=3).mean()
        return k, d
    
    @staticmethod
    def calculate_adx(df, period=14):
        """ADX 계산"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0
        
        tr = pd.concat([high - low, 
                       (high - close.shift()).abs(), 
                       (low - close.shift()).abs()], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.abs().rolling(window=period).mean() / atr)
        
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def calculate_cci(df, period=20):
        """CCI 계산"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        sma = tp.rolling(window=period).mean()
        mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
        cci = (tp - sma) / (0.015 * mad)
        return cci
    
    @staticmethod
    def calculate_williams_r(df, period=14):
        """Williams %R 계산"""
        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        wr = -100 * ((high_max - df['close']) / (high_max - low_min))
        return wr
    
    @staticmethod
    def calculate_obv(df):
        """OBV 계산"""
        obv = (df['volume'] * (~df['close'].diff().le(0) * 2 - 1)).cumsum()
        return obv
    
    @staticmethod
    def calculate_vwap(df):
        """VWAP 계산"""
        tp = (df['high'] + df['low'] + df['close']) / 3
        vwap = (tp * df['volume']).cumsum() / df['volume'].cumsum()
        return vwap
    
    @staticmethod
    def calculate_ichimoku(df):
        """일목균형표 계산"""
        # 전환선 (9일)
        high_9 = df['high'].rolling(window=9).max()
        low_9 = df['low'].rolling(window=9).min()
        df['ichimoku_tenkan'] = (high_9 + low_9) / 2
        
        # 기준선 (26일)
        high_26 = df['high'].rolling(window=26).max()
        low_26 = df['low'].rolling(window=26).min()
        df['ichimoku_kijun'] = (high_26 + low_26) / 2
        
        # 선행스팬 A (26일 전)
        senkou_a_base = (df['ichimoku_tenkan'].shift(26) + df['ichimoku_kijun'].shift(26)) / 2
        df['ichimoku_senkou_a'] = senkou_a_base
        
        # 선행스팬 B (26일 전)
        high_52_shifted = df['high'].shift(26).rolling(window=52).max()
        low_52_shifted = df['low'].shift(26).rolling(window=52).min()
        df['ichimoku_senkou_b'] = (high_52_shifted + low_52_shifted) / 2
        
        # 후행스팬
        df['ichimoku_chikou'] = df['close'].shift(-26)
        
        # NaN 값 처리 (pandas 2.0+ 호환)
        df['ichimoku_senkou_a'] = df['ichimoku_senkou_a'].ffill()
        df['ichimoku_senkou_b'] = df['ichimoku_senkou_b'].ffill()
        
        return df