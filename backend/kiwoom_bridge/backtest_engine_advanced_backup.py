"""
고급 백테?�트 ?�진
- 분할매수/매도 지??
- ?�확??기술??지??계산
- ?�제 주�? ?�이???�용
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import sys
import os

# Core 모듈 경로 추�?
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core 모듈 ?�선 ?�포??
try:
    from core import (
        compute_indicators,
        evaluate_conditions,
        _normalize_conditions,
        convert_legacy_column,
        _iname
    )
    USE_CORE = True
    print("[INFO] AdvancedBacktestEngine: Core 모듈 로드 ?�공")
except ImportError as e:
    USE_CORE = False
    print(f"[WARNING] AdvancedBacktestEngine: Core 모듈 로드 ?�패: {e}")

# ?�백: 기존 모듈??
try:
    from indicators_complete import CompleteIndicators
    USE_COMPLETE_INDICATORS = True
except ImportError:
    USE_COMPLETE_INDICATORS = False

try:
    from strategy_engine import StrategyEngine
    USE_STRATEGY_ENGINE = True
    if not USE_CORE:
        print("[INFO] AdvancedBacktestEngine: strategy_engine.py�??�용?�니??")
except ImportError:
    USE_STRATEGY_ENGINE = False
    if not USE_CORE:
        print("[WARNING] AdvancedBacktestEngine: strategy_engine.py�?찾을 ???�습?�다.")

@dataclass
class Position:
    """?��????�보"""
    stock_code: str
    quantity: int
    avg_price: float
    entry_date: datetime
    entry_reason: str
    partial_entries: List[Dict] = field(default_factory=list)  # 분할매수 기록

    def add_partial(self, quantity: int, price: float, date: datetime):
        """분할매수 추�?"""
        # ?�균?��? ?�계??
        total_value = self.quantity * self.avg_price + quantity * price
        self.quantity += quantity
        self.avg_price = total_value / self.quantity if self.quantity > 0 else 0

        self.partial_entries.append({
            'date': date,
            'quantity': quantity,
            'price': price
        })

    def remove_partial(self, quantity: int, price: float, date: datetime) -> float:
        """분할매도 ?�행"""
        if quantity > self.quantity:
            quantity = self.quantity

        profit = (price - self.avg_price) * quantity
        self.quantity -= quantity

        return profit

@dataclass
class Trade:
    """거래 기록"""
    date: datetime
    stock_code: str
    action: str  # 'buy', 'sell', 'buy_partial', 'sell_partial'
    quantity: int
    price: float
    commission: float
    slippage: float
    profit: Optional[float] = None
    profit_pct: Optional[float] = None
    position_size: Optional[int] = None  # 거래 ???��????�기

# ?�틸리티 ?�수??
def _iname(base: str, *params) -> str:
    """지?�명 ?�성 - 모든 ?�라미터�??�문?�로 변?�하???�결"""
    parts = [str(base).lower()] + [str(p).lower() for p in params if p is not None]
    return "_".join(parts)

def _lc(s):
    """문자?�을 ?�문?�로 변??""
    return s.lower() if isinstance(s, str) else s

def _normalize_conditions(conditions):
    """조건 ?�규??- 지?�명, ?�산?? 값을 ?�문?�화"""
    norm = []
    for c in conditions or []:
        c = dict(c)
        c['indicator'] = _lc(c.get('indicator', ''))
        c['operator'] = _lc(c.get('operator', ''))
        v = c.get('value', 0)
        c['value'] = _lc(v) if isinstance(v, str) else v
        c['combineWith'] = _lc(c.get('combineWith')) if c.get('combineWith') else None
        norm.append(c)
    return norm

class TechnicalIndicators:
    """기술??지??계산 ?�래??- Core 모듈 ?�용 ??건너?�"""

    @staticmethod
    def compute_all(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Core 모듈 ?�용 ???�임"""
        if USE_CORE:
            return compute_indicators(df, config)
        # 기존 로직 ?��?
        return TechnicalIndicators._legacy_compute(df, config)

    @staticmethod
    def _legacy_compute(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """?�거??지??계산""
    """?�확??기술??지??계산"""

    @staticmethod
    def calculate_all(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """모든 지??계산"""
        # ?�이??검�?
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"?�수 컬럼 ?�락: {col}")

        # Use StrategyEngine if available for comprehensive indicator calculation
        if USE_STRATEGY_ENGINE:
            try:
                print(f"[DEBUG] StrategyEngine ?�용 ?�작. DataFrame shape: {df.shape}")
                engine = StrategyEngine()
                df = engine.calculate_all_indicators(df)

                # price 별칭 추�?
                df['price'] = df['close']

                print(f"[INFO] StrategyEngine?�서 모든 지??계산 ?�료")
                print(f"[DEBUG] ?�용 가?�한 컬럼: {list(df.columns)}")

                # Check if rsi_14 exists
                if 'rsi_14' in df.columns:
                    print(f"[DEBUG] rsi_14 발견! ?�플 �? {df['rsi_14'].iloc[-5:].values}")
                else:
                    print(f"[WARNING] rsi_14가 ?�전???�습?�다. RSI 관??컬럼: {[col for col in df.columns if 'rsi' in col.lower()]}")

                return df
            except Exception as e:
                print(f"[WARNING] StrategyEngine ?�용 ?�패: {e}. 기본 방법?�로 ?�환.")
                import traceback
                traceback.print_exc()

        # 지???�정
        indicators = config.get('indicators', [])

        for indicator in indicators:
            ind_type = indicator.get('type')
            params = indicator.get('params', {})

            if ind_type == 'SMA' or ind_type == 'MA':
                period = params.get('period', 20)
                df[_iname('sma', period)] = df['close'].rolling(window=period).mean()
                df[_iname('ma', period)] = df[_iname('sma', period)]  # ?�일 �??�공

            elif ind_type == 'EMA':
                period = params.get('period', 20)
                df[_iname('ema', period)] = df['close'].ewm(span=period, adjust=False).mean()

            elif ind_type == 'RSI':
                # Wilder RSI ?��? ?�식
                period = params.get('period', 14)
                delta = df['close'].diff()
                up = delta.clip(lower=0)
                down = (-delta).clip(lower=0)
                rma_up = up.ewm(alpha=1/period, adjust=False).mean()
                rma_down = down.ewm(alpha=1/period, adjust=False).mean()
                rs = rma_up / rma_down.replace(0, 1e-10)
                df[_iname('rsi', period)] = 100 - (100 / (1 + rs))

            elif ind_type == 'MACD':
                f = params.get('fast', 12)
                s = params.get('slow', 26)
                sig = params.get('signal', 9)

                macd = df['close'].ewm(span=f, adjust=False).mean() - df['close'].ewm(span=s, adjust=False).mean()
                df[_iname('macd', f, s)] = macd
                df[_iname('macd_signal', f, s, sig)] = macd.ewm(span=sig, adjust=False).mean()
                df[_iname('macd_hist', f, s, sig)] = df[_iname('macd', f, s)] - df[_iname('macd_signal', f, s, sig)]

            elif ind_type == 'BB':
                p = params.get('period', 20)
                k = params.get('std', 2)
                ma = df['close'].rolling(window=p).mean()
                sd = df['close'].rolling(window=p).std()
                df[_iname('bb_middle', p)] = ma
                df[_iname('bb_upper', p, k)] = ma + k * sd
                df[_iname('bb_lower', p, k)] = ma - k * sd

            elif ind_type == 'Stochastic':
                k_period = params.get('k_period', 14)
                d_period = params.get('d_period', 3)
                low_min = df['low'].rolling(window=k_period).min()
                high_max = df['high'].rolling(window=k_period).max()
                k_fast = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
                df[_iname('stoch_k', k_period, d_period)] = k_fast
                df[_iname('stoch_d', k_period, d_period)] = k_fast.rolling(window=d_period).mean()

            elif ind_type == 'ATR':
                # Wilder ATR ?��? ?�식
                p = params.get('period', 14)
                tr = pd.concat([
                    df['high'] - df['low'],
                    (df['high'] - df['close'].shift()).abs(),
                    (df['low'] - df['close'].shift()).abs()
                ], axis=1).max(axis=1)
                df[_iname('atr', p)] = tr.ewm(alpha=1/p, adjust=False).mean()

            elif ind_type == 'OBV':
                df[_iname('obv')] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

            elif ind_type == 'ADX':
                # ?��? ADX ?�식 (Wilder 방식)
                p = params.get('period', 14)
                upMove = df['high'].diff()
                downMove = df['low'].shift(1) - df['low']
                plus_dm = np.where((upMove > downMove) & (upMove > 0), upMove, 0.0)
                minus_dm = np.where((downMove > upMove) & (downMove > 0), downMove, 0.0)

                tr = pd.concat([
                    df['high'] - df['low'],
                    (df['high'] - df['close'].shift()).abs(),
                    (df['low'] - df['close'].shift()).abs()
                ], axis=1).max(axis=1)

                atr = tr.ewm(alpha=1/p, adjust=False).mean()
                plus_di = 100 * (pd.Series(plus_dm, index=df.index).ewm(alpha=1/p, adjust=False).mean() / atr.replace(0,1e-10))
                minus_di = 100 * (pd.Series(minus_dm, index=df.index).ewm(alpha=1/p, adjust=False).mean() / atr.replace(0,1e-10))
                dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0,1e-10)
                df[_iname('adx', p)] = dx.ewm(alpha=1/p, adjust=False).mean()

            elif ind_type == 'CCI':
                p = params.get('period', 20)
                tp = (df['high'] + df['low'] + df['close']) / 3
                sma_tp = tp.rolling(window=p).mean()
                mad = tp.rolling(window=p).apply(lambda x: np.abs(x - x.mean()).mean())
                df[_iname('cci', p)] = (tp - sma_tp) / (0.015 * mad + 1e-10)

            elif ind_type == 'MFI':
                p = params.get('period', 14)
                tp = (df['high'] + df['low'] + df['close']) / 3
                mf = tp * df['volume']
                pos_mf = pd.Series(np.where(tp > tp.shift(), mf, 0), index=df.index)
                neg_mf = pd.Series(np.where(tp < tp.shift(), mf, 0), index=df.index)
                mfr = pos_mf.rolling(window=p).sum() / (neg_mf.rolling(window=p).sum() + 1e-10)
                df[_iname('mfi', p)] = 100 - (100 / (1 + mfr))

            elif ind_type == 'WILLIAMS_R':
                p = params.get('period', 14)
                hh = df['high'].rolling(window=p).max()
                ll = df['low'].rolling(window=p).min()
                df[_iname('willr', p)] = -100 * (hh - df['close']) / (hh - ll + 1e-10)

        # price 별칭 추�? (close?� ?�일)
        df['price'] = df['close']

        return df

class SignalGenerator:
    """매매 ?�호 ?�성"""

    @staticmethod
    def evaluate_conditions(df: pd.DataFrame, conditions: List[Dict], signal_type: str) -> pd.Series:
        """조건 ?��? �??�호 ?�성"""
        if not conditions:
            return pd.Series(0, index=df.index)

        # 조건 ?�규??
        conditions = _normalize_conditions(conditions)

        # �?조건???��?
        condition_results = []

        for i, condition in enumerate(conditions):
            indicator = condition.get('indicator', '')
            operator = condition.get('operator', '')
            value = condition.get('value', 0)
            combine = condition.get('combineWith', 'and' if i > 0 else None)

            # 지??컬럼 ?�인
            if indicator not in df.columns:
                # ?�영 ?�경?�서??경고�?출력
                if signal_type == 'buy':
                    print(f"경고: 매수 조건??지??'{indicator}'�?찾을 ???�습?�다")
                else:
                    print(f"경고: 매도 조건??지??'{indicator}'�?찾을 ???�습?�다")
                continue

            ind_values = df[indicator]

            # 비교 값이 ?�른 지?�인 경우
            if isinstance(value, str):
                # 문자?�인 경우, 먼�? 컬럼명인지 ?�인
                if value in df.columns:
                    compare_values = df[value]
                else:
                    # 컬럼명이 ?�니�??�자�?변???�도
                    try:
                        compare_values = float(value)
                    except ValueError:
                        print(f"경고: �?'{value}'�?처리?????�습?�다 (지?�도 ?�니�??�자???�님)")
                        continue
            else:
                compare_values = float(value)

            # 조건 ?��?
            if operator == '>':
                result = ind_values > compare_values
            elif operator == '<':
                result = ind_values < compare_values
            elif operator == '>=':
                result = ind_values >= compare_values
            elif operator == '<=':
                result = ind_values <= compare_values
            elif operator == '==':
                result = ind_values == compare_values
            elif operator == 'cross_above':
                if isinstance(compare_values, pd.Series):
                    result = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values.shift(1))
                else:
                    result = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values)
            elif operator == 'cross_below':
                if isinstance(compare_values, pd.Series):
                    result = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values.shift(1))
                else:
                    result = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values)
            else:
                continue

            condition_results.append((result, combine))

        # 조건 결합
        if condition_results:
            final_result = condition_results[0][0]

            for i in range(1, len(condition_results)):
                if condition_results[i][1] == 'and':
                    final_result = final_result & condition_results[i][0]
                else:  # or
                    final_result = final_result | condition_results[i][0]

            # ?�호 ?�성 (진입 ?�점�?
            signal = pd.Series(0, index=df.index)
            signal[final_result & ~final_result.shift(1).fillna(False)] = 1 if signal_type == 'buy' else -1

            return signal

        return pd.Series(0, index=df.index)

    @staticmethod
    def evaluate_conditions_with_profit(df: pd.DataFrame, strategy_config: Dict,
                                       signal_type: str, positions: Dict = None,
                                       stock_code: str = 'TEST') -> pd.Series:
        """목표 ?�익률을 ?�함??조건 ?��? (?�계�?목표 지??"""

        # 1. 기본 지??조건 ?��?
        if signal_type == 'sell':
            conditions = strategy_config.get('sellConditions', [])
        else:
            conditions = strategy_config.get('buyConditions', [])

        base_signal = SignalGenerator.evaluate_conditions(df, conditions, signal_type)

        # 2. 매도 ??목표 ?�익�?조건 추�? ?��?
        if signal_type == 'sell' and positions and stock_code in positions:
            target_profit = strategy_config.get('targetProfit', {})
            stop_loss = strategy_config.get('stopLoss', {})
            position = positions[stock_code]

            # 목표 ?�익�??�호 ?�성
            if target_profit:
                mode = target_profit.get('mode', 'simple')

                if mode == 'simple' and target_profit.get('enabled'):
                    # ?�일 목표 모드 (?�전 버전 ?�환??
                    profit_signal = pd.Series(0, index=df.index)

                    # simple 모드: enabled가 직접 ?�거??simple.enabled가 ?�는 경우 처리
                    if target_profit.get('simple'):
                        target_value = target_profit['simple'].get('value', 5.0)
                        combine_method = _lc(target_profit['simple'].get('combineWith', 'or'))
                    else:
                        # ?�전 버전 ?�환??
                        target_value = target_profit.get('value', 5.0)
                        combine_method = _lc(target_profit.get('combineWith', 'or'))

                    for idx in df.index:
                        current_price = df.loc[idx, 'close']
                        profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                        if profit_pct >= target_value:
                            profit_signal[idx] = -1  # ?�량 매도 ?�호

                    # 기존 조건�?결합
                    if combine_method == 'and':
                        base_signal = base_signal & profit_signal
                    else:  # or
                        base_signal = base_signal | profit_signal

                elif mode == 'staged' and target_profit.get('staged', {}).get('enabled'):
                    # ?�계�?목표 모드
                    profit_signal = pd.Series(0, index=df.index)
                    staged_config = target_profit['staged']
                    stages = staged_config.get('stages', [])

                    # ?��? ?�행???�계 추적
                    if not hasattr(position, 'executed_stages'):
                        position.executed_stages = []

                    for idx in df.index:
                        current_price = df.loc[idx, 'close']
                        profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                        # �??�계�?목표 ?�인
                        for stage in stages:
                            stage_num = stage.get('stage', 1)
                            stage_target = stage.get('targetProfit', 5.0)
                            exit_ratio = stage.get('exitRatio', 100) / 100.0
                            stage_combine = _lc(stage.get('combineWith', staged_config.get('combineWith', 'or')))

                            # ?��? ?�행???�계???�킵
                            if stage_num in position.executed_stages:
                                continue

                            if profit_pct >= stage_target:
                                # �??�계�?결합 방식 ?�??
                                if not hasattr(profit_signal, 'stage_combines'):
                                    profit_signal.stage_combines = {}
                                profit_signal.stage_combines[idx] = stage_combine

                                # 부�?매도 ?�호 (비율 ?�??
                                if not hasattr(profit_signal, 'exit_ratios'):
                                    profit_signal.exit_ratios = {}
                                profit_signal.exit_ratios[idx] = exit_ratio
                                profit_signal[idx] = -exit_ratio  # ?�수�?매도 비율 ?�시
                                position.executed_stages.append(stage_num)

                                # ?�적 ?�절 조정
                                if stage.get('dynamicStopLoss', False):
                                    # ?�절?�을 ?�재 ?�계??목표 ?�익률로 ?�향
                                    if hasattr(position, 'dynamic_stop_loss'):
                                        position.dynamic_stop_loss = max(
                                            position.dynamic_stop_loss,
                                            position.avg_price * (1 + stage_target / 100)
                                        )
                                    else:
                                        position.dynamic_stop_loss = position.avg_price * (1 + stage_target / 100)
                                break  # ??번에 ?�나???�계�??�행

                    # ?�계�?결합 방식 ?�용
                    # profit_signal??�??�덱?�별 결합 방식???�?�되???�음
                    combined_signal = pd.Series(0, index=df.index)

                    for idx in df.index:
                        if profit_signal[idx] != 0:
                            # ?�당 ?�덱?�의 결합 방식 ?�인
                            stage_combine = _lc(getattr(profit_signal, 'stage_combines', {}).get(idx, 'or'))

                            if stage_combine == 'and':
                                # AND: 지??조건�?목표 ?�익 모두 충족
                                if base_signal[idx] != 0:
                                    combined_signal[idx] = profit_signal[idx]
                            else:  # or
                                # OR: ??�??�나�?충족
                                if profit_signal[idx] != 0:
                                    combined_signal[idx] = profit_signal[idx]
                                elif base_signal[idx] != 0:
                                    combined_signal[idx] = base_signal[idx]
                        elif base_signal[idx] != 0:
                            # 목표 ?�익 미달????지??조건�??�인
                            combined_signal[idx] = base_signal[idx]

                    base_signal = combined_signal

            # ?�절 조건 (??�� OR�?결합)
            if stop_loss.get('enabled'):
                loss_signal = pd.Series(0, index=df.index)
                loss_value = stop_loss.get('value', 3.0)

                # ?�레?�링 ?�톱 ?�인
                trailing_stop = stop_loss.get('trailingStop', {})

                for idx in df.index:
                    current_price = df.loc[idx, 'close']
                    profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                    # ?�적 ?�절 ?�인 (Break Even Stop)
                    if hasattr(position, 'dynamic_stop_loss'):
                        dynamic_loss_pct = ((current_price - position.dynamic_stop_loss) / position.dynamic_stop_loss) * 100
                        if dynamic_loss_pct <= 0:
                            loss_signal[idx] = -1  # ?�적 ?�절 매도
                            continue

                    # ?�레?�링 ?�톱 ?�인
                    if trailing_stop.get('enabled'):
                        activation = trailing_stop.get('activation', 5.0)
                        distance = trailing_stop.get('distance', 2.0)

                        # 최고가 추적
                        if not hasattr(position, 'peak_price'):
                            position.peak_price = position.avg_price

                        if profit_pct >= activation:
                            # ?�레?�링 ?�톱 ?�성??
                            position.peak_price = max(position.peak_price, current_price)
                            peak_drop_pct = ((current_price - position.peak_price) / position.peak_price) * 100

                            if peak_drop_pct <= -abs(distance):
                                loss_signal[idx] = -1  # ?�레?�링 ?�톱 매도
                                continue

                    # ?�반 ?�절
                    if profit_pct <= -abs(loss_value):
                        loss_signal[idx] = -1  # ?�절 매도

                # ?�절?� ??�� OR (즉시 ?�행)
                base_signal = base_signal | loss_signal

        return base_signal

class AdvancedBacktestEngine:
    """고급 백테?�트 ?�진"""

    def __init__(self, initial_capital: float = 10000000, commission: float = 0.00015, slippage: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []

    def calculate_position_size(self, capital: float, price: float, config: Dict) -> int:
        """?��????�기 계산"""
        position_sizing = config.get('positionSizing', {})
        method = position_sizing.get('method', 'fixed')

        if method == 'fixed':
            # 고정 금액
            amount = position_sizing.get('amount', capital * 0.1)
            shares = int(amount / price)
        elif method == 'percent':
            # ?�본???�정 비율
            percent = position_sizing.get('percent', 10) / 100
            amount = capital * percent
            shares = int(amount / price)
        elif method == 'kelly':
            # 켈리 공식 (win_rate�?avg_win/avg_loss ?�요)
            win_rate = position_sizing.get('win_rate', 0.5)
            win_loss_ratio = position_sizing.get('win_loss_ratio', 1.5)
            kelly_percent = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            kelly_percent = max(0, min(kelly_percent, 0.25))  # 최�? 25% ?�한
            amount = capital * kelly_percent
            shares = int(amount / price)
        else:
            # 기본�? ?�본??10%
            shares = int((capital * 0.1) / price)

        return max(0, shares)

    def execute_buy(self, stock_code: str, date: datetime, price: float, config: Dict) -> Optional[Trade]:
        """매수 ?�행"""
        # 분할매수 ?�정
        split_buy = config.get('splitBuy', {})
        enable_split = split_buy.get('enabled', False)
        split_count = split_buy.get('count', 1)
        split_interval = split_buy.get('interval', 'price')  # 'price' or 'time'

        # ?�리?��? ?�용
        actual_price = price * (1 + self.slippage)

        # ?��????�기 계산
        position_size = self.calculate_position_size(self.capital, actual_price, config)

        if enable_split and split_count > 1:
            # 분할매수
            split_size = position_size // split_count
            if split_size <= 0:
                return None

            # �?번째 분할매수�??�행 (?�머지??조건 충족 ??
            position_size = split_size

        # ?�수�?계산
        cost = position_size * actual_price * (1 + self.commission)

        if cost > self.capital:
            return None

        # ?��????�성 ?�는 추�?
        if stock_code in self.positions:
            # 기존 ?��??�에 추�? (?�라미딩)
            position = self.positions[stock_code]
            position.add_partial(position_size, actual_price, date)
            action = 'buy_partial'
        else:
            # ???��????�성
            self.positions[stock_code] = Position(
                stock_code=stock_code,
                quantity=position_size,
                avg_price=actual_price,
                entry_date=date,
                entry_reason='signal'
            )
            action = 'buy'

        # ?�본 차감
        self.capital -= cost

        # 거래 기록
        trade = Trade(
            date=date,
            stock_code=stock_code,
            action=action,
            quantity=position_size,
            price=actual_price,
            commission=self.commission,
            slippage=self.slippage,
            position_size=self.positions[stock_code].quantity
        )
        self.trades.append(trade)

        return trade

    def execute_sell(self, stock_code: str, date: datetime, price: float, config: Dict) -> Optional[Trade]:
        """매도 ?�행"""
        if stock_code not in self.positions:
            return None

        position = self.positions[stock_code]
        if position.quantity <= 0:
            return None

        # 분할매도 ?�정
        split_sell = config.get('splitSell', {})
        enable_split = split_sell.get('enabled', False)
        split_count = split_sell.get('count', 1)

        # ?�리?��? ?�용
        actual_price = price * (1 - self.slippage)

        # 매도 ?�량 결정
        if enable_split and split_count > 1:
            sell_quantity = position.quantity // split_count
            if sell_quantity <= 0:
                sell_quantity = position.quantity
        else:
            sell_quantity = position.quantity

        # ?�익 계산
        profit = position.remove_partial(sell_quantity, actual_price, date)
        proceeds = sell_quantity * actual_price * (1 - self.commission)

        # ?�본 증�?
        self.capital += proceeds

        # ?��????�리
        if position.quantity <= 0:
            del self.positions[stock_code]
            action = 'sell'
        else:
            action = 'sell_partial'

        # 거래 기록
        trade = Trade(
            date=date,
            stock_code=stock_code,
            action=action,
            quantity=sell_quantity,
            price=actual_price,
            commission=self.commission,
            slippage=self.slippage,
            profit=profit,
            profit_pct=(profit / (position.avg_price * sell_quantity)) * 100 if position.avg_price > 0 else 0,
            position_size=position.quantity if stock_code in self.positions else 0
        )
        self.trades.append(trade)

        return trade

    def run(self, data: pd.DataFrame, strategy_config: Dict) -> Dict[str, Any]:
        """백테?�트 ?�행 - Core 모듈 ?�선 ?�용"""
        print(f"[DEBUG] AdvancedBacktestEngine.run ?�작")
        print(f"[DEBUG] ?�력 ?�이??shape: {data.shape}")
        print(f"[DEBUG] Core 모듈 ?�용: {USE_CORE}")

        # Core 모듈 ?�용 ??
        if USE_CORE:
            print("[DEBUG] Core 모듈�?처리")

            # params 구조 ?�동 ?�정
            indicators = strategy_config.get('indicators', [])
            fixed_indicators = []
            for ind in indicators:
                if 'params' not in ind and 'period' in ind:
                    fixed_ind = {
                        'type': ind.get('type', 'MA').upper(),
                        'params': {'period': ind.get('period', 20)}
                    }
                    print(f"[FIX] 지??구조: {ind} ??{fixed_ind}")
                    fixed_indicators.append(fixed_ind)
                else:
                    fixed_indicators.append(ind)

            # 조건 ?�규??
            buy_conditions = _normalize_conditions(strategy_config.get('buyConditions', []))
            sell_conditions = _normalize_conditions(strategy_config.get('sellConditions', []))

            # Core ?�정
            config = {
                **strategy_config,
                'indicators': fixed_indicators,
                'buyConditions': buy_conditions,
                'sellConditions': sell_conditions
            }

            # 지??계산
            data = compute_indicators(data, config)

            # ?�호 ?�성
            data['buy_signal'] = evaluate_conditions(data, buy_conditions, 'buy')
            data['sell_signal'] = evaluate_conditions(data, sell_conditions, 'sell')

            buy_count = (data['buy_signal'] == 1).sum()
            sell_count = (data['sell_signal'] == -1).sum()
            print(f"[Core] ?�호: 매수 {buy_count}, 매도 {sell_count}")

        # ?�백: 기존 방식
        elif USE_COMPLETE_INDICATORS:
            print(f"[DEBUG] CompleteIndicators ?�용")
            data = CompleteIndicators.calculate_all(data, strategy_config)
        else:
            print(f"[DEBUG] TechnicalIndicators ?�용")
            data = TechnicalIndicators.calculate_all(data, strategy_config)

        print(f"[DEBUG] 지??계산 ???�이??shape: {data.shape}")
        print(f"[DEBUG] 지??계산 ??컬럼: {list(data.columns)[:30]}...")

        # Core 모듈???�용?��? ?�는 경우?�만 기존 ?�호 ?�성
        if not USE_CORE:
            # ?�호 ?�성
            buy_conditions = strategy_config.get('buyConditions', [])
            sell_conditions = strategy_config.get('sellConditions', [])

            print(f"[DEBUG] 매수 조건: {buy_conditions}")
            print(f"[DEBUG] 매도 조건: {sell_conditions}")

            # 목표 ?�익�??�보 출력
            target_profit = strategy_config.get('targetProfit', {})
            if target_profit.get('enabled'):
                print(f"[DEBUG] 목표 ?�익�? {target_profit.get('value')}%, 결합: {target_profit.get('combineWith', 'OR')}")

            data['buy_signal'] = SignalGenerator.evaluate_conditions(data, buy_conditions, 'buy')

        # 매도 ?�호???��??�이 ?�을 ?�만 목표 ?�익�?고려
        if self.positions:
            data['sell_signal'] = SignalGenerator.evaluate_conditions_with_profit(
                data, strategy_config, 'sell', self.positions, 'TEST'
            )
        else:
            data['sell_signal'] = SignalGenerator.evaluate_conditions(data, sell_conditions, 'sell')

        # 백테?�트 ?�행
        for i in range(len(data)):
            row = data.iloc[i]
            date = row['date']
            close = row['close']

            # ?�재 ?�트?�리??가�?계산
            portfolio_value = self.capital
            for stock_code, position in self.positions.items():
                portfolio_value += position.quantity * close
            self.equity_curve.append(portfolio_value)

            # ?��??�이 ?�을 ??매도 ?�호 ?�계??(목표 ?�익�??�시�?체크)
            if self.positions:
                current_sell_signal = SignalGenerator.evaluate_conditions_with_profit(
                    data.iloc[[i]], strategy_config, 'sell', self.positions, 'TEST'
                )
                if not current_sell_signal.empty and current_sell_signal.iloc[0] == -1:
                    for stock_code in list(self.positions.keys()):
                        position = self.positions[stock_code]
                        profit_pct = ((close - position.avg_price) / position.avg_price) * 100

                        # 목표 ?�익�??�는 ?�절 ?�달 ??로그
                        target_profit = strategy_config.get('targetProfit', {})
                        stop_loss = strategy_config.get('stopLoss', {})

                        if target_profit.get('enabled') and profit_pct >= target_profit.get('value', 5.0):
                            print(f"[목표 ?�익�??�달] {stock_code}: {profit_pct:.2f}% >= {target_profit.get('value')}%")
                        elif stop_loss.get('enabled') and profit_pct <= -abs(stop_loss.get('value', 3.0)):
                            print(f"[?�절 ?�행] {stock_code}: {profit_pct:.2f}% <= -{stop_loss.get('value')}%")

                        self.execute_sell(stock_code, date, close, strategy_config)
            elif row['sell_signal'] == -1:
                # ?��??�이 ?�으�?기본 매도 ?�호 ?�용
                for stock_code in list(self.positions.keys()):
                    self.execute_sell(stock_code, date, close, strategy_config)

            # 매수 ?�호 처리
            if row['buy_signal'] == 1:
                # 최�? ?��?????체크
                max_positions = strategy_config.get('maxPositions', 1)
                if len(self.positions) < max_positions:
                    self.execute_buy('TEST', date, close, strategy_config)

        # 최종 ?��????�리
        if len(data) > 0:
            final_date = data.iloc[-1]['date']
            final_price = data.iloc[-1]['close']

            for stock_code in list(self.positions.keys()):
                position = self.positions[stock_code]
                if position.quantity > 0:
                    self.execute_sell(stock_code, final_date, final_price, strategy_config)

        # ?�과 분석
        return self.analyze_performance()

    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze performance"""
        if not self.trades:
            return {
                'total_return': 0,
                'win_rate': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'trades': []
            }

        # 기본 ?�계
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100

        # ?�료??거래�?분석
        completed_trades = [t for t in self.trades if t.profit is not None]
        winning_trades = [t for t in completed_trades if t.profit > 0]
        losing_trades = [t for t in completed_trades if t.profit <= 0]

        win_rate = (len(winning_trades) / len(completed_trades) * 100) if completed_trades else 0

        # ?�균 ?�익
        avg_win = np.mean([t.profit for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.profit for t in losing_trades])) if losing_trades else 0

        # Profit Factor
        total_wins = sum([t.profit for t in winning_trades]) if winning_trades else 0
        total_losses = abs(sum([t.profit for t in losing_trades])) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # 최�? ?�폭
        if self.equity_curve:
            equity_array = np.array(self.equity_curve)
            peak = np.maximum.accumulate(equity_array)
            drawdown = (peak - equity_array) / peak * 100
            max_drawdown = np.max(drawdown)
        else:
            max_drawdown = 0

        # Sharpe Ratio (?�간 ?�익�?기�?)
        if len(self.equity_curve) > 1:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        # 거래 ?�세 ?�보
        trade_details = []
        for trade in self.trades:
            trade_details.append({
                'date': trade.date.isoformat() if isinstance(trade.date, datetime) else str(trade.date),
                'stock_code': trade.stock_code,
                'action': trade.action,
                'quantity': trade.quantity,
                'price': trade.price,
                'profit': trade.profit,
                'profit_pct': trade.profit_pct,
                'position_size': trade.position_size
            })

        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': len(completed_trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'buy_count': len([t for t in self.trades if 'buy' in t.action]),
            'sell_count': len([t for t in self.trades if 'sell' in t.action]),
            'trades': trade_details,
            'equity_curve': self.equity_curve
        }
