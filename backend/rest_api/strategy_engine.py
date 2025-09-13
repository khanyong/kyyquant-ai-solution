"""
전략 신호 생성 엔진
실제 매수/매도 조건을 평가하고 거래 신호를 생성
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import talib

class IndicatorCalculator:
    """기술적 지표 계산 클래스"""

    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int) -> pd.Series:
        """단순 이동평균"""
        return df['close'].rolling(window=period).mean()

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int) -> pd.Series:
        """지수 이동평균"""
        return df['close'].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """RSI (Relative Strength Index)"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """MACD"""
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """볼린저 밴드"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }

    @staticmethod
    def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """스토캐스틱"""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()

        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()

        return {
            'k': k_percent,
            'd': d_percent
        }

    @staticmethod
    def calculate_volume_ratio(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """거래량 비율"""
        return df['volume'] / df['volume'].rolling(window=period).mean()

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATR (Average True Range)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr


class StrategyEngine:
    """전략 실행 엔진"""

    def __init__(self):
        self.indicator_calc = IndicatorCalculator()
        self.indicators = {}

    def prepare_data(self, df: pd.DataFrame, strategy_params: Dict) -> pd.DataFrame:
        """데이터에 필요한 지표들을 계산하여 추가"""
        df = df.copy()

        # 전략에서 사용하는 지표들 추출
        indicators = strategy_params.get('indicators', [])
        buy_conditions = strategy_params.get('buyConditions', [])
        sell_conditions = strategy_params.get('sellConditions', [])

        # 모든 조건에서 사용되는 지표 수집
        used_indicators = set()

        for ind in indicators:
            ind_type = ind.get('type', '').lower()
            used_indicators.add(ind_type)

        for cond in buy_conditions + sell_conditions:
            indicator = cond.get('indicator', '').lower()
            if indicator:
                # RSI_14 -> RSI 형태로 파싱
                base_indicator = indicator.split('_')[0]
                used_indicators.add(base_indicator)

        # 각 지표 계산
        for indicator in used_indicators:
            if 'sma' in indicator or 'ma' in indicator:
                # 다양한 기간의 SMA 계산
                for period in [5, 10, 20, 50, 100, 200]:
                    df[f'sma_{period}'] = self.indicator_calc.calculate_sma(df, period)

            elif 'ema' in indicator:
                # 다양한 기간의 EMA 계산
                for period in [5, 10, 20, 50, 100, 200]:
                    df[f'ema_{period}'] = self.indicator_calc.calculate_ema(df, period)

            elif 'rsi' in indicator:
                df['rsi'] = self.indicator_calc.calculate_rsi(df)
                df['rsi_14'] = df['rsi']  # 별칭

            elif 'macd' in indicator:
                macd_data = self.indicator_calc.calculate_macd(df)
                df['macd'] = macd_data['macd']
                df['macd_signal'] = macd_data['signal']
                df['macd_histogram'] = macd_data['histogram']

            elif 'bb' in indicator or 'bollinger' in indicator:
                bb_data = self.indicator_calc.calculate_bollinger_bands(df)
                df['bb_upper'] = bb_data['upper']
                df['bb_middle'] = bb_data['middle']
                df['bb_lower'] = bb_data['lower']

            elif 'stoch' in indicator:
                stoch_data = self.indicator_calc.calculate_stochastic(df)
                df['stoch_k'] = stoch_data['k']
                df['stoch_d'] = stoch_data['d']

            elif 'volume' in indicator:
                df['volume_ratio'] = self.indicator_calc.calculate_volume_ratio(df)

            elif 'atr' in indicator:
                df['atr'] = self.indicator_calc.calculate_atr(df)

        return df

    def evaluate_condition(self, df: pd.DataFrame, idx: int, condition: Dict) -> bool:
        """단일 조건 평가"""
        try:
            indicator = condition.get('indicator', '').lower()
            operator = condition.get('operator', '')
            value = condition.get('value', 0)

            if idx < 0 or idx >= len(df):
                return False

            # 현재 값 가져오기
            current_value = None

            # 가격 관련
            if indicator == 'price' or indicator == 'close':
                current_value = df.iloc[idx]['close']
            elif indicator == 'volume':
                current_value = df.iloc[idx]['volume']

            # RSI
            elif 'rsi' in indicator:
                if 'rsi' in df.columns:
                    current_value = df.iloc[idx]['rsi']

            # 이동평균
            elif 'sma' in indicator or 'ma' in indicator:
                # sma_20 형태에서 기간 추출
                parts = indicator.split('_')
                if len(parts) > 1:
                    period = parts[1]
                    col_name = f'sma_{period}'
                    if col_name in df.columns:
                        current_value = df.iloc[idx][col_name]

            elif 'ema' in indicator:
                parts = indicator.split('_')
                if len(parts) > 1:
                    period = parts[1]
                    col_name = f'ema_{period}'
                    if col_name in df.columns:
                        current_value = df.iloc[idx][col_name]

            # MACD
            elif 'macd' in indicator:
                if 'signal' in indicator and 'macd_signal' in df.columns:
                    current_value = df.iloc[idx]['macd_signal']
                elif 'histogram' in indicator and 'macd_histogram' in df.columns:
                    current_value = df.iloc[idx]['macd_histogram']
                elif 'macd' in df.columns:
                    current_value = df.iloc[idx]['macd']

            # 볼린저 밴드
            elif 'bb' in indicator or 'bollinger' in indicator:
                if 'upper' in indicator and 'bb_upper' in df.columns:
                    current_value = df.iloc[idx]['bb_upper']
                elif 'lower' in indicator and 'bb_lower' in df.columns:
                    current_value = df.iloc[idx]['bb_lower']
                elif 'middle' in indicator and 'bb_middle' in df.columns:
                    current_value = df.iloc[idx]['bb_middle']

            # 스토캐스틱
            elif 'stoch' in indicator:
                if 'k' in indicator and 'stoch_k' in df.columns:
                    current_value = df.iloc[idx]['stoch_k']
                elif 'd' in indicator and 'stoch_d' in df.columns:
                    current_value = df.iloc[idx]['stoch_d']

            if current_value is None or pd.isna(current_value):
                return False

            # 연산자별 평가
            if operator == '>':
                return current_value > float(value)
            elif operator == '<':
                return current_value < float(value)
            elif operator == '=' or operator == '==':
                return abs(current_value - float(value)) < 0.0001
            elif operator == '>=' or operator == '≥':
                return current_value >= float(value)
            elif operator == '<=' or operator == '≤':
                return current_value <= float(value)

            # 크로스오버 조건 (이전 값과 비교)
            elif operator == 'cross_above' and idx > 0:
                # 두 지표 간 크로스
                target_col = f"{value}".lower()
                if target_col in df.columns:
                    prev_current = df.iloc[idx-1][indicator] if indicator in df.columns else None
                    prev_target = df.iloc[idx-1][target_col]
                    curr_current = current_value
                    curr_target = df.iloc[idx][target_col]

                    if all(v is not None for v in [prev_current, prev_target, curr_current, curr_target]):
                        return prev_current <= prev_target and curr_current > curr_target

            elif operator == 'cross_below' and idx > 0:
                target_col = f"{value}".lower()
                if target_col in df.columns:
                    prev_current = df.iloc[idx-1][indicator] if indicator in df.columns else None
                    prev_target = df.iloc[idx-1][target_col]
                    curr_current = current_value
                    curr_target = df.iloc[idx][target_col]

                    if all(v is not None for v in [prev_current, prev_target, curr_current, curr_target]):
                        return prev_current >= prev_target and curr_current < curr_target

            return False

        except Exception as e:
            print(f"조건 평가 오류: {e}, condition: {condition}")
            return False

    def generate_signal(self, df: pd.DataFrame, date, strategy_params: Dict) -> str:
        """거래 신호 생성"""
        try:
            # 날짜에 해당하는 인덱스 찾기
            if date not in df.index:
                return 'hold'

            idx = df.index.get_loc(date)

            # 디버깅: 현재 상태 출력 (처음 몇 번만)
            if hasattr(self, '_debug_count'):
                self._debug_count += 1
            else:
                self._debug_count = 1

            if self._debug_count <= 5:  # 처음 5번만 로그 출력
                row = df.iloc[idx]
                print(f"\n[DEBUG {self._debug_count}] Date: {date}")
                if 'rsi' in df.columns and not pd.isna(row.get('rsi')):
                    print(f"  RSI: {row['rsi']:.2f}")
                if 'sma_20' in df.columns and not pd.isna(row.get('sma_20')):
                    print(f"  SMA_20: {row['sma_20']:.0f}")
                print(f"  Close: {row['close']:.0f}")

            # 매수 조건 체크
            buy_conditions = strategy_params.get('buyConditions', [])
            if buy_conditions:
                buy_signals = []

                for i, condition in enumerate(buy_conditions):
                    signal = self.evaluate_condition(df, idx, condition)
                    buy_signals.append(signal)

                    # AND/OR 로직 처리
                    if i > 0:
                        combine = condition.get('combineWith', 'AND')
                        if combine == 'AND':
                            buy_signals[i] = buy_signals[i-1] and buy_signals[i]
                        elif combine == 'OR':
                            buy_signals[i] = buy_signals[i-1] or buy_signals[i]

                if buy_signals and buy_signals[-1]:
                    return 'buy'

            # 매도 조건 체크
            sell_conditions = strategy_params.get('sellConditions', [])
            if sell_conditions:
                sell_signals = []

                for i, condition in enumerate(sell_conditions):
                    signal = self.evaluate_condition(df, idx, condition)
                    sell_signals.append(signal)

                    # AND/OR 로직 처리
                    if i > 0:
                        combine = condition.get('combineWith', 'AND')
                        if combine == 'AND':
                            sell_signals[i] = sell_signals[i-1] and sell_signals[i]
                        elif combine == 'OR':
                            sell_signals[i] = sell_signals[i-1] or sell_signals[i]

                if sell_signals and sell_signals[-1]:
                    return 'sell'

            return 'hold'

        except Exception as e:
            print(f"신호 생성 오류: {e}")
            return 'hold'


# 싱글톤 인스턴스
strategy_engine = StrategyEngine()