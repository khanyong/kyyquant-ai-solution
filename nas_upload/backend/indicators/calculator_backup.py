"""
기술적 지표 계산기
"""

import pandas as pd
import numpy as np
from typing import Dict, Any

class IndicatorCalculator:
    """지표 계산기"""

    async def calculate(self, df: pd.DataFrame, indicator_config: Dict[str, Any]) -> pd.DataFrame:
        """지표 계산"""
        name = indicator_config.get('name')
        params = indicator_config.get('params', {})
        column_name = indicator_config.get('column_name', name)

        if name == 'ma':
            return self._calculate_ma(df, params, column_name)
        elif name == 'ema':
            return self._calculate_ema(df, params, column_name)
        elif name == 'rsi':
            return self._calculate_rsi(df, params, column_name)
        elif name == 'macd':
            return self._calculate_macd(df, params, column_name)
        elif name == 'bollinger':
            return self._calculate_bollinger(df, params, column_name)
        elif name == 'stochastic':
            return self._calculate_stochastic(df, params, column_name)
        elif name == 'volume_ma':
            return self._calculate_volume_ma(df, params, column_name)
        else:
            print(f"Unknown indicator: {name}")
            return df

    def _calculate_ma(self, df: pd.DataFrame, params: Dict, column_name: str) -> pd.DataFrame:
        """이동평균 계산"""
        period = params.get('period', 20)
        df[column_name] = df['close'].rolling(window=period).mean()
        return df

    def _calculate_ema(self, df: pd.DataFrame, params: Dict, column_name: str) -> pd.DataFrame:
        """지수이동평균 계산"""
        period = params.get('period', 20)
        df[column_name] = df['close'].ewm(span=period, adjust=False).mean()
        return df

    def _calculate_rsi(self, df: pd.DataFrame, params: Dict, column_name: str) -> pd.DataFrame:
        """RSI 계산"""
        period = params.get('period', 14)

        # 가격 변화량 계산
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # RS 계산
        rs = gain / loss

        # RSI 계산
        df[column_name] = 100 - (100 / (1 + rs))
        return df

    def _calculate_macd(self, df: pd.DataFrame, params: Dict, column_name: str) -> pd.DataFrame:
        """MACD 계산"""
        fast = params.get('fast', 12)
        slow = params.get('slow', 26)
        signal = params.get('signal', 9)

        # MACD 라인
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        df[f'{column_name}_line'] = exp1 - exp2

        # Signal 라인
        df[f'{column_name}_signal'] = df[f'{column_name}_line'].ewm(span=signal, adjust=False).mean()

        # MACD 히스토그램
        df[f'{column_name}_hist'] = df[f'{column_name}_line'] - df[f'{column_name}_signal']

        return df

    def _calculate_bollinger(self, df: pd.DataFrame, params: Dict, column_name: str) -> pd.DataFrame:
        """볼린저 밴드 계산"""
        period = params.get('period', 20)
        std = params.get('std', 2)

        # 중심선 (이동평균)
        df[f'{column_name}_middle'] = df['close'].rolling(window=period).mean()

        # 표준편차
        rolling_std = df['close'].rolling(window=period).std()

        # 상단/하단 밴드
        df[f'{column_name}_upper'] = df[f'{column_name}_middle'] + (rolling_std * std)
        df[f'{column_name}_lower'] = df[f'{column_name}_middle'] - (rolling_std * std)

        # 밴드폭
        df[f'{column_name}_width'] = df[f'{column_name}_upper'] - df[f'{column_name}_lower']

        # %B (현재 가격의 밴드 내 위치)
        df[f'{column_name}_percent'] = (df['close'] - df[f'{column_name}_lower']) / df[f'{column_name}_width']

        return df

    def _calculate_stochastic(self, df: pd.DataFrame, params: Dict, column_name: str) -> pd.DataFrame:
        """스토캐스틱 계산"""
        k_period = params.get('k_period', 14)
        d_period = params.get('d_period', 3)
        smooth_k = params.get('smooth_k', 3)

        # %K 계산
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()

        df[f'{column_name}_K'] = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))

        # Smooth %K
        if smooth_k > 1:
            df[f'{column_name}_K'] = df[f'{column_name}_K'].rolling(window=smooth_k).mean()

        # %D 계산 (Signal Line)
        df[f'{column_name}_D'] = df[f'{column_name}_K'].rolling(window=d_period).mean()

        return df

    def _calculate_volume_ma(self, df: pd.DataFrame, params: Dict, column_name: str) -> pd.DataFrame:
        """거래량 이동평균 계산"""
        period = params.get('period', 20)
        df[column_name] = df['volume'].rolling(window=period).mean()
        return df

    def calculate_all_basic(self, df: pd.DataFrame) -> pd.DataFrame:
        """기본 지표 모두 계산"""
        # 기본 이동평균
        for period in [5, 10, 20, 60, 120]:
            df = self._calculate_ma(df, {'period': period}, f'MA_{period}')

        # RSI
        df = self._calculate_rsi(df, {'period': 14}, 'RSI')

        # MACD
        df = self._calculate_macd(df, {}, 'MACD')

        # 볼린저 밴드
        df = self._calculate_bollinger(df, {}, 'BB')

        # 거래량 이동평균
        df = self._calculate_volume_ma(df, {'period': 20}, 'volume_ma_20')

        return df