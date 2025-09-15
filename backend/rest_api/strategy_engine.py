"""
전략 신호 생성 엔진
실제 매수/매도 조건을 평가하고 거래 신호를 생성
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import sys
import os

# kiwoom_bridge의 core 모듈 경로 추가
kiwoom_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kiwoom_bridge')
sys.path.insert(0, kiwoom_path)

# Core 모듈 임포트 시도
try:
    from core import (
        compute_indicators,
        evaluate_conditions,
        _normalize_conditions,
        convert_legacy_column
    )
    USE_CORE = True
    print("[StrategyEngine] Core 모듈 로드 성공")
except ImportError as e:
    print(f"[StrategyEngine] Core 모듈 로드 실패: {e}")
    USE_CORE = False

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
    """전략 실행 엔진 - Core 모듈 우선 사용"""

    def __init__(self):
        self.indicator_calc = IndicatorCalculator()
        self.indicators = {}
        self.use_core = USE_CORE
        if self.use_core:
            print("[StrategyEngine] Core 모듈 모드로 동작")
        else:
            print("[StrategyEngine] 레거시 모드로 동작")

    def prepare_data(self, df: pd.DataFrame, strategy_params: Dict) -> pd.DataFrame:
        """데이터에 필요한 지표들을 계산하여 추가"""
        df = df.copy()

        # Core 모듈 사용 가능한 경우
        if self.use_core:
            print("[StrategyEngine] Core 모듈로 지표 계산")

            # params 구조 자동 수정
            indicators = strategy_params.get('indicators', [])
            fixed_indicators = []

            for ind in indicators:
                if 'params' not in ind and 'period' in ind:
                    fixed_ind = {
                        'type': ind.get('type', 'MA').upper(),
                        'params': {'period': ind.get('period', 20)}
                    }
                    print(f"[FIX] 지표 구조 수정: {ind} → {fixed_ind}")
                    fixed_indicators.append(fixed_ind)
                else:
                    fixed_indicators.append(ind)

            # 조건 정규화
            buy_conditions = _normalize_conditions(strategy_params.get('buyConditions', []))
            sell_conditions = _normalize_conditions(strategy_params.get('sellConditions', []))

            # Core 설정으로 계산
            config = {
                **strategy_params,
                'indicators': fixed_indicators,
                'buyConditions': buy_conditions,
                'sellConditions': sell_conditions
            }

            df = compute_indicators(df, config)

            # 신호 생성
            df['buy_signal'] = evaluate_conditions(df, buy_conditions, 'buy')
            df['sell_signal'] = evaluate_conditions(df, sell_conditions, 'sell')
            df['signal'] = 0
            df.loc[df['buy_signal'] == 1, 'signal'] = 1
            df.loc[df['sell_signal'] == -1, 'signal'] = -1

            buy_count = (df['buy_signal'] == 1).sum()
            sell_count = (df['sell_signal'] == -1).sum()
            print(f"[Core] 신호 생성: 매수 {buy_count}개, 매도 {sell_count}개")

            return df

        # 전략에서 사용하는 지표들 추출
        indicators = strategy_params.get('indicators', [])
        buy_conditions = strategy_params.get('buyConditions', [])
        sell_conditions = strategy_params.get('sellConditions', [])

        print(f"[prepare_data] indicators array: {indicators[:2] if indicators else 'None'}")
        print(f"[prepare_data] buyConditions: {buy_conditions[:1] if buy_conditions else 'None'}")
        print(f"[prepare_data] sellConditions: {sell_conditions[:1] if sell_conditions else 'None'}")

        # 모든 조건에서 사용되는 지표 수집
        used_indicators = set()

        # indicators 배열에서 지표 타입 추출 (개선)
        for ind in indicators:
            if isinstance(ind, dict):
                ind_type = ind.get('type', '').lower()
                if ind_type:
                    used_indicators.add(ind_type)
                    # 특정 period가 있으면 추가 정보로 저장
                    if 'period' in ind:
                        used_indicators.add(f"{ind_type}_{ind.get('period')}")
            elif isinstance(ind, str):
                # 문자열인 경우 (구형 포맷 호환)
                used_indicators.add(ind.lower())

        for cond in buy_conditions + sell_conditions:
            indicator = cond.get('indicator', '').lower()
            if indicator:
                # rsi_14 -> rsi, ma_20 -> ma 형태로 파싱
                base_indicator = indicator.split('_')[0]
                used_indicators.add(base_indicator)

                # value가 지표를 참조하는 경우도 확인
                value = cond.get('value', '')
                if isinstance(value, str) and '_' in value:
                    value_base = value.lower().split('_')[0]
                    used_indicators.add(value_base)

        print(f"[prepare_data] 사용할 지표들: {used_indicators}")

        # indicators 배열에서 직접 지표 정보 추출하여 계산
        for ind in indicators:
            if isinstance(ind, dict):
                ind_type = ind.get('type', '').lower()
                period = ind.get('period')

                if ind_type == 'ma' and period:
                    col_name = f'ma_{period}'
                    df[col_name] = self.indicator_calc.calculate_sma(df, period)
                    df[f'sma_{period}'] = df[col_name]  # 별칭
                    print(f"  계산됨: {col_name}")

                elif ind_type == 'rsi' and period:
                    col_name = f'rsi_{period}'
                    df[col_name] = self.indicator_calc.calculate_rsi(df, period)
                    if period == 14:
                        df['rsi'] = df[col_name]  # 기본 rsi 별칭
                    print(f"  계산됨: {col_name}")

                elif ind_type == 'macd':
                    fast = ind.get('fast', 12)
                    slow = ind.get('slow', 26)
                    signal = ind.get('signal', 9)
                    macd_data = self.indicator_calc.calculate_macd(df, fast, slow, signal)
                    df['macd'] = macd_data['macd']
                    df['macd_signal'] = macd_data['signal']
                    df['macd_histogram'] = macd_data['histogram']
                    print(f"  계산됨: MACD ({fast},{slow},{signal})")

                elif ind_type == 'bb':
                    period = ind.get('period', 20)
                    std_dev = ind.get('std_dev', 2)
                    bb_data = self.indicator_calc.calculate_bollinger_bands(df, period, std_dev)
                    df['bb_upper'] = bb_data['upper']
                    df['bb_middle'] = bb_data['middle']
                    df['bb_lower'] = bb_data['lower']
                    print(f"  계산됨: BB ({period},{std_dev})")

                elif ind_type == 'stochastic':
                    k_period = ind.get('k_period', 14)
                    d_period = ind.get('d_period', 3)
                    stoch_data = self.indicator_calc.calculate_stochastic(df, k_period, d_period)
                    df['stoch_k'] = stoch_data['k']
                    df['stoch_d'] = stoch_data['d']
                    print(f"  계산됨: Stochastic K={k_period}, D={d_period}")

        # 기존 코드 (조건에서 사용되는 추가 지표 계산)
        for indicator in used_indicators:
            if 'sma' in indicator or 'ma' in indicator:
                # 다양한 기간의 SMA 계산
                for period in [5, 10, 20, 50, 60, 100, 200]:
                    col_name = f'sma_{period}'
                    df[col_name] = self.indicator_calc.calculate_sma(df, period)
                    # ma_20 형태도 지원
                    df[f'ma_{period}'] = df[col_name]

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
            # 지표명은 모두 소문자로 통일
            indicator = condition.get('indicator', '').lower()
            operator = condition.get('operator', '')
            value = condition.get('value', 0)

            # 디버깅용 로그 (처음 몇 번만)
            if not hasattr(self, '_eval_debug_count'):
                self._eval_debug_count = 0
            if self._eval_debug_count < 10:
                self._eval_debug_count += 1
                print(f"[EVAL DEBUG {self._eval_debug_count}] Evaluating: {indicator} {operator} {value}")
                print(f"  Available columns: {list(df.columns)[:10]}...")

            if idx < 0 or idx >= len(df):
                return False

            # 현재 값 가져오기
            current_value = None

            # 가격 관련
            if indicator == 'price' or indicator == 'close':
                current_value = df.iloc[idx]['close']
            elif indicator == 'volume':
                current_value = df.iloc[idx]['volume']

            # RSI - rsi_14, rsi_9 등
            elif 'rsi' in indicator:
                # 기본 rsi 컬럼 먼저 시도
                if 'rsi' in df.columns:
                    current_value = df.iloc[idx]['rsi']
                else:
                    # rsi_14 형태로 시도
                    parts = indicator.split('_')
                    if len(parts) > 1 and f'rsi_{parts[1]}' in df.columns:
                        current_value = df.iloc[idx][f'rsi_{parts[1]}']

            # 이동평균 - ma_20, sma_60 등
            elif 'ma' in indicator or 'sma' in indicator:
                parts = indicator.split('_')
                if len(parts) > 1:
                    period = parts[1]
                    # sma_20, ma_20 모두 시도
                    for prefix in ['sma', 'ma']:
                        col_name = f'{prefix}_{period}'
                        if col_name in df.columns:
                            current_value = df.iloc[idx][col_name]
                            break

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

            # 볼린저 밴드 - bb_upper, bb_lower 등
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
                if self._eval_debug_count <= 10:
                    print(f"  ⚠️ current_value is None for {indicator}")
                return False

            # value가 다른 지표를 참조하는 경우 처리 (예: ma_20 > ma_60)
            compare_value = value
            if isinstance(value, str) and not value.replace('.', '').replace('-', '').isdigit():
                # 다른 지표를 참조하는 경우 (소문자로 통일)
                value_indicator = value.lower()

                # 이동평균 처리
                if 'ma' in value_indicator:
                    parts = value_indicator.split('_')
                    if len(parts) > 1:
                        period = parts[1]
                        for prefix in ['sma', 'ma']:
                            col_name = f'{prefix}_{period}'
                            if col_name in df.columns:
                                compare_value = df.iloc[idx][col_name]
                                break
                # 볼린저 밴드 처리
                elif 'bb_' in value_indicator:
                    if value_indicator in df.columns:
                        compare_value = df.iloc[idx][value_indicator]
                # MACD 처리
                elif 'macd' in value_indicator:
                    if value_indicator in df.columns:
                        compare_value = df.iloc[idx][value_indicator]
                # 기타 지표
                elif value_indicator in df.columns:
                    compare_value = df.iloc[idx][value_indicator]

                if self._eval_debug_count <= 10:
                    print(f"  Comparing {indicator}={current_value} with {value_indicator}={compare_value}")
            else:
                compare_value = float(value)

            # 연산자별 평가
            if operator == '>':
                return current_value > compare_value
            elif operator == '<':
                return current_value < compare_value
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

    def normalize_strategy_params(self, strategy_params: Dict) -> Dict:
        """전략 파라미터의 지표명을 소문자로 정규화"""
        if not strategy_params:
            return strategy_params

        # buyConditions 정규화
        if 'buyConditions' in strategy_params:
            for condition in strategy_params['buyConditions']:
                if 'indicator' in condition:
                    condition['indicator'] = condition['indicator'].lower()
                if 'value' in condition and isinstance(condition['value'], str):
                    # 숫자가 아닌 문자열은 지표 참조로 간주하여 소문자로 변환
                    if not condition['value'].replace('.', '').replace('-', '').isdigit():
                        condition['value'] = condition['value'].lower()

        # sellConditions 정규화
        if 'sellConditions' in strategy_params:
            for condition in strategy_params['sellConditions']:
                if 'indicator' in condition:
                    condition['indicator'] = condition['indicator'].lower()
                if 'value' in condition and isinstance(condition['value'], str):
                    if not condition['value'].replace('.', '').replace('-', '').isdigit():
                        condition['value'] = condition['value'].lower()

        return strategy_params

    def generate_signal(self, df: pd.DataFrame, date, strategy_params: Dict) -> str:
        """거래 신호 생성"""
        try:
            # Core 모듈 사용 시 사전 계산된 신호 사용
            if self.use_core and 'signal' in df.columns:
                if date not in df.index:
                    return 'hold'

                idx = df.index.get_loc(date)
                signal_val = df.iloc[idx]['signal']

                if signal_val == 1:
                    return 'buy'
                elif signal_val == -1:
                    return 'sell'
                else:
                    return 'hold'

            # 레거시 방식
            # 전략 파라미터 정규화 (대소문자 통일)
            strategy_params = self.normalize_strategy_params(strategy_params)

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