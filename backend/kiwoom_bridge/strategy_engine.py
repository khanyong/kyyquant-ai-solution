"""
전략 신호 생성 엔진 (시놀로지 NAS 버전)
실제 매수/매도 조건을 평가하고 거래 신호를 생성
talib 의존성 없이 순수 Python으로 구현
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

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
        rs = gain / loss.replace(0, 1e-10)  # Avoid division by zero
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

        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
        d_percent = k_percent.rolling(window=d_period).mean()

        return {
            'k': k_percent,
            'd': d_percent
        }

    @staticmethod
    def calculate_volume_ratio(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """거래량 비율"""
        avg_volume = df['volume'].rolling(window=period).mean()
        return df['volume'] / avg_volume.replace(0, 1e-10)

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """ATR (Average True Range)"""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr

    @staticmethod
    def calculate_obv(df: pd.DataFrame) -> pd.Series:
        """OBV (On Balance Volume)"""
        return (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()


class StrategyEngine:
    """전략 실행 엔진"""

    def __init__(self):
        self.indicator_calc = IndicatorCalculator()
        self.indicators = {}
        self._debug_count = 0
        self._max_debug = 10  # 디버그 출력 제한

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """모든 기본 지표를 계산하는 메서드"""
        df = df.copy()

        # PRICE 컬럼 추가
        df['PRICE'] = df['close']
        df['price'] = df['close']

        # RSI 계산 (여러 기간)
        for period in [14, 9, 21]:
            rsi_data = self.indicator_calc.calculate_rsi(df, period)
            df[f'rsi_{period}'] = rsi_data
            df[f'RSI_{period}'] = rsi_data  # 대문자 버전

        # 볼린저 밴드
        bb_data = self.indicator_calc.calculate_bollinger_bands(df)
        df['bb_upper'] = bb_data['upper']
        df['bb_middle'] = bb_data['middle']
        df['bb_lower'] = bb_data['lower']
        df['BB_upper'] = bb_data['upper']
        df['BB_middle'] = bb_data['middle']
        df['BB_lower'] = bb_data['lower']
        df['BB_UPPER'] = bb_data['upper']
        df['BB_MIDDLE'] = bb_data['middle']
        df['BB_LOWER'] = bb_data['lower']

        # MACD
        macd_data = self.indicator_calc.calculate_macd(df)
        df['macd'] = macd_data['macd']
        df['macd_signal'] = macd_data['signal']
        df['macd_hist'] = macd_data['histogram']
        df['MACD'] = macd_data['macd']
        df['MACD_signal'] = macd_data['signal']
        df['MACD_hist'] = macd_data['histogram']
        df['MACD_SIGNAL'] = macd_data['signal']  # 전체 대문자 버전 추가

        # SMA (여러 기간)
        for period in [5, 10, 20, 50, 200]:
            sma_data = self.indicator_calc.calculate_sma(df, period)
            df[f'sma_{period}'] = sma_data
            df[f'SMA_{period}'] = sma_data

        # EMA (여러 기간)
        for period in [12, 26, 50]:
            ema_data = self.indicator_calc.calculate_ema(df, period)
            df[f'ema_{period}'] = ema_data
            df[f'EMA_{period}'] = ema_data

        # Stochastic
        stoch_data = self.indicator_calc.calculate_stochastic(df)
        df['stoch_k'] = stoch_data['k']
        df['stoch_d'] = stoch_data['d']
        df['Stoch_K'] = stoch_data['k']
        df['Stoch_D'] = stoch_data['d']

        # ATR
        atr_data = self.indicator_calc.calculate_atr(df)
        df['atr_14'] = atr_data
        df['ATR_14'] = atr_data

        # OBV
        obv_data = self.indicator_calc.calculate_obv(df)
        df['obv'] = obv_data
        df['OBV'] = obv_data

        # Volume Ratio
        vr_data = self.indicator_calc.calculate_volume_ratio(df)
        df['vr_20'] = vr_data
        df['VR_20'] = vr_data

        return df

    def prepare_data(self, df: pd.DataFrame, strategy_params: Dict) -> pd.DataFrame:
        """데이터에 필요한 지표들을 계산하여 추가"""
        df = df.copy()

        # PRICE 컬럼 추가 (전략 템플릿 호환성)
        df['PRICE'] = df['close']
        df['price'] = df['close']

        # 전략에서 사용하는 지표들 추출
        indicators = strategy_params.get('indicators', [])
        buy_conditions = strategy_params.get('buyConditions', [])
        sell_conditions = strategy_params.get('sellConditions', [])

        # 모든 조건에서 사용되는 지표 수집
        used_indicators = set()

        # indicators 배열에서 지표 수집
        for ind in indicators:
            ind_type = ind.get('type', '').upper()
            params = ind.get('params', {})

            # 파라미터에 따라 구체적인 지표명 생성
            if ind_type in ['SMA', 'MA', 'EMA']:
                period = params.get('period', 20)
                used_indicators.add(f"{ind_type.lower()}_{period}")
            elif ind_type == 'RSI':
                period = params.get('period', 14)
                used_indicators.add(f"rsi_{period}")
            else:
                used_indicators.add(ind_type.lower())

        # 조건에서 사용되는 지표 수집
        for cond in buy_conditions + sell_conditions:
            indicator = cond.get('indicator', '').lower()
            if indicator and indicator not in ['price', 'close', 'volume']:
                used_indicators.add(indicator)

            # value가 지표인 경우도 수집
            value = str(cond.get('value', '')).lower()
            if value and not value.replace('.', '').isdigit():
                used_indicators.add(value)

        print(f"[StrategyEngine] 사용 지표: {used_indicators}")

        # 각 지표 계산
        for indicator_str in used_indicators:
            try:
                if 'sma' in indicator_str or 'ma_' in indicator_str or 'ma' == indicator_str:
                    # sma_20 형태에서 기간 추출
                    parts = indicator_str.split('_')
                    if len(parts) > 1 and parts[1].isdigit():
                        period = int(parts[1])
                        df[f'sma_{period}'] = self.indicator_calc.calculate_sma(df, period)
                        df[f'ma_{period}'] = df[f'sma_{period}']  # 별칭
                        # 대문자 버전도 추가 (전략 템플릿 호환성)
                        df[f'SMA_{period}'] = df[f'sma_{period}']
                        df[f'MA_{period}'] = df[f'sma_{period}']

                elif 'ema' in indicator_str:
                    parts = indicator_str.split('_')
                    if len(parts) > 1 and parts[1].isdigit():
                        period = int(parts[1])
                        df[f'ema_{period}'] = self.indicator_calc.calculate_ema(df, period)

                elif 'rsi' in indicator_str:
                    parts = indicator_str.split('_')
                    period = 14
                    if len(parts) > 1 and parts[1].isdigit():
                        period = int(parts[1])
                    df[f'rsi_{period}'] = self.indicator_calc.calculate_rsi(df, period)
                    df['rsi'] = df[f'rsi_{period}']  # 기본 RSI
                    # 대문자 버전도 추가 (전략 템플릿 호환성)
                    df[f'RSI_{period}'] = df[f'rsi_{period}']
                    df['RSI'] = df[f'rsi_{period}']

                elif 'macd' in indicator_str:
                    macd_data = self.indicator_calc.calculate_macd(df)
                    df['macd'] = macd_data['macd']
                    df['macd_signal'] = macd_data['signal']
                    df['macd_histogram'] = macd_data['histogram']
                    # 대문자 버전도 추가 (전략 템플릿 호환성)
                    df['MACD'] = macd_data['macd']
                    df['MACD_SIGNAL'] = macd_data['signal']
                    df['MACD_HISTOGRAM'] = macd_data['histogram']

                elif 'bb' in indicator_str or 'bollinger' in indicator_str:
                    bb_data = self.indicator_calc.calculate_bollinger_bands(df)
                    df['bb_upper'] = bb_data['upper']
                    df['bb_middle'] = bb_data['middle']
                    df['bb_lower'] = bb_data['lower']
                    # 대문자 버전도 추가 (전략 템플릿 호환성)
                    df['BB_UPPER'] = bb_data['upper']
                    df['BB_MIDDLE'] = bb_data['middle']
                    df['BB_LOWER'] = bb_data['lower']

                elif 'stoch' in indicator_str:
                    stoch_data = self.indicator_calc.calculate_stochastic(df)
                    df['stoch_k'] = stoch_data['k']
                    df['stoch_d'] = stoch_data['d']

                elif 'volume_ratio' in indicator_str:
                    df['volume_ratio'] = self.indicator_calc.calculate_volume_ratio(df)

                elif 'atr' in indicator_str:
                    df['atr'] = self.indicator_calc.calculate_atr(df)

                elif 'obv' in indicator_str:
                    df['obv'] = self.indicator_calc.calculate_obv(df)

            except Exception as e:
                print(f"[StrategyEngine] 지표 계산 오류 ({indicator_str}): {e}")

        # 디버그: 계산된 컬럼 확인
        calculated_indicators = [col for col in df.columns if col not in ['open', 'high', 'low', 'close', 'volume', 'date']]
        if calculated_indicators:
            print(f"[StrategyEngine] 계산된 지표: {calculated_indicators[:10]}")  # 처음 10개만

        return df

    def evaluate_condition(self, df: pd.DataFrame, idx: int, condition: Dict) -> bool:
        """단일 조건 평가"""
        try:
            # indicator를 원본 그대로 유지하고, 비교할 때만 lowercase 사용
            indicator_orig = condition.get('indicator', '')
            indicator = indicator_orig.lower()
            operator = condition.get('operator', '')
            value = condition.get('value', 0)

            if idx < 0 or idx >= len(df):
                return False

            # 현재 값 가져오기
            current_value = None

            # 가격/거래량 관련
            if indicator in ['price', 'close']:
                current_value = df.iloc[idx]['close']
            elif indicator == 'volume':
                current_value = df.iloc[idx]['volume']
            elif indicator == 'open':
                current_value = df.iloc[idx]['open']
            elif indicator == 'high':
                current_value = df.iloc[idx]['high']
            elif indicator == 'low':
                current_value = df.iloc[idx]['low']

            # 지표값 가져오기 - 원본과 lowercase 둘 다 체크
            elif indicator in df.columns:
                current_value = df.iloc[idx][indicator]
            elif indicator_orig in df.columns:
                current_value = df.iloc[idx][indicator_orig]

            # indicator_period 형태 처리 (예: rsi_14, sma_20)
            elif '_' in indicator:
                if indicator in df.columns:
                    current_value = df.iloc[idx][indicator]
                else:
                    # RSI, RSI_14 등 다양한 형태 처리
                    base_indicator = indicator.split('_')[0]
                    if base_indicator in df.columns:
                        current_value = df.iloc[idx][base_indicator]

            if current_value is None or pd.isna(current_value):
                return False

            # value가 숫자인지 지표명인지 판단
            compare_value = None
            try:
                compare_value = float(value)
            except (ValueError, TypeError):
                # value가 지표명인 경우 - 원본과 lowercase 둘 다 체크
                value_orig = str(value)
                value_str = value_orig.lower()
                if value_str in df.columns:
                    compare_value = df.iloc[idx][value_str]
                elif value_orig in df.columns:
                    compare_value = df.iloc[idx][value_orig]
                elif '_' in value_str and value_str in df.columns:
                    compare_value = df.iloc[idx][value_str]

            if compare_value is None:
                return False

            # 연산자별 평가
            if operator == '>':
                return current_value > compare_value
            elif operator == '<':
                return current_value < compare_value
            elif operator in ['=', '==']:
                return abs(current_value - compare_value) < 0.0001
            elif operator in ['>=', '≥']:
                return current_value >= compare_value
            elif operator in ['<=', '≤']:
                return current_value <= compare_value

            # 크로스오버 조건
            elif operator == 'cross_above' and idx > 0:
                if isinstance(compare_value, (int, float)):
                    # 고정값과의 크로스
                    prev_value = df.iloc[idx-1][indicator] if indicator in df.columns else None
                    if prev_value is not None:
                        return prev_value <= compare_value and current_value > compare_value
                else:
                    # 두 지표 간 크로스
                    value_col = str(value).lower()
                    if value_col in df.columns:
                        prev_current = df.iloc[idx-1][indicator] if indicator in df.columns else None
                        prev_compare = df.iloc[idx-1][value_col]
                        curr_compare = df.iloc[idx][value_col]

                        if prev_current is not None:
                            return prev_current <= prev_compare and current_value > curr_compare

            elif operator == 'cross_below' and idx > 0:
                if isinstance(compare_value, (int, float)):
                    prev_value = df.iloc[idx-1][indicator] if indicator in df.columns else None
                    if prev_value is not None:
                        return prev_value >= compare_value and current_value < compare_value
                else:
                    value_col = str(value).lower()
                    if value_col in df.columns:
                        prev_current = df.iloc[idx-1][indicator] if indicator in df.columns else None
                        prev_compare = df.iloc[idx-1][value_col]
                        curr_compare = df.iloc[idx][value_col]

                        if prev_current is not None:
                            return prev_current >= prev_compare and current_value < curr_compare

            return False

        except Exception as e:
            if self._debug_count < self._max_debug:
                print(f"[StrategyEngine] 조건 평가 오류: {e}, condition: {condition}")
                self._debug_count += 1
            return False

    def generate_signal(self, df: pd.DataFrame, date, strategy_params: Dict) -> str:
        """거래 신호 생성"""
        try:
            # 날짜에 해당하는 인덱스 찾기
            if date not in df.index:
                return 'hold'

            idx = df.index.get_loc(date)

            # 매수 조건 체크
            buy_conditions = strategy_params.get('buyConditions', [])
            if buy_conditions:
                buy_result = True

                for i, condition in enumerate(buy_conditions):
                    signal = self.evaluate_condition(df, idx, condition)

                    if i == 0:
                        buy_result = signal
                    else:
                        combine = condition.get('combineWith', 'AND')
                        if combine == 'AND':
                            buy_result = buy_result and signal
                        elif combine == 'OR':
                            buy_result = buy_result or signal

                if buy_result:
                    return 'buy'

            # 매도 조건 체크
            sell_conditions = strategy_params.get('sellConditions', [])
            if sell_conditions:
                sell_result = True

                for i, condition in enumerate(sell_conditions):
                    signal = self.evaluate_condition(df, idx, condition)

                    if i == 0:
                        sell_result = signal
                    else:
                        combine = condition.get('combineWith', 'AND')
                        if combine == 'AND':
                            sell_result = sell_result and signal
                        elif combine == 'OR':
                            sell_result = sell_result or signal

                if sell_result:
                    return 'sell'

            return 'hold'

        except Exception as e:
            if self._debug_count < self._max_debug:
                print(f"[StrategyEngine] 신호 생성 오류: {e}")
                self._debug_count += 1
            return 'hold'


# 싱글톤 인스턴스
strategy_engine = StrategyEngine()