"""
고급 백테스트 엔진
- 분할매수/매도 지원
- 정확한 기술적 지표 계산
- 실제 주가 데이터 활용
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
try:
    from indicators_complete import CompleteIndicators
    USE_COMPLETE_INDICATORS = True
except ImportError:
    USE_COMPLETE_INDICATORS = False

# Import StrategyEngine for indicator calculations
try:
    from strategy_engine import StrategyEngine
    USE_STRATEGY_ENGINE = True
    print("[INFO] AdvancedBacktestEngine: strategy_engine.py를 사용합니다.")
except ImportError:
    USE_STRATEGY_ENGINE = False
    print("[WARNING] AdvancedBacktestEngine: strategy_engine.py를 찾을 수 없습니다.")

@dataclass
class Position:
    """포지션 정보"""
    stock_code: str
    quantity: int
    avg_price: float
    entry_date: datetime
    entry_reason: str
    partial_entries: List[Dict] = field(default_factory=list)  # 분할매수 기록

    def add_partial(self, quantity: int, price: float, date: datetime):
        """분할매수 추가"""
        # 평균단가 재계산
        total_value = self.quantity * self.avg_price + quantity * price
        self.quantity += quantity
        self.avg_price = total_value / self.quantity if self.quantity > 0 else 0

        self.partial_entries.append({
            'date': date,
            'quantity': quantity,
            'price': price
        })

    def remove_partial(self, quantity: int, price: float, date: datetime) -> float:
        """분할매도 실행"""
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
    position_size: Optional[int] = None  # 거래 후 포지션 크기

class TechnicalIndicators:
    """정확한 기술적 지표 계산"""

    @staticmethod
    def calculate_all(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """모든 지표 계산"""
        # 데이터 검증
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"필수 컬럼 누락: {col}")

        # Use StrategyEngine if available for comprehensive indicator calculation
        if USE_STRATEGY_ENGINE:
            try:
                print(f"[DEBUG] StrategyEngine 사용 시작. DataFrame shape: {df.shape}")
                engine = StrategyEngine()
                df = engine.calculate_all_indicators(df)

                # Ensure PRICE column exists for compatibility
                if 'PRICE' not in df.columns:
                    df['PRICE'] = df['close']

                print(f"[INFO] StrategyEngine에서 모든 지표 계산 완료")
                print(f"[DEBUG] 사용 가능한 컬럼: {list(df.columns)}")

                # Check if RSI_14 exists
                if 'RSI_14' in df.columns:
                    print(f"[DEBUG] RSI_14 발견! 샘플 값: {df['RSI_14'].iloc[-5:].values}")
                else:
                    print(f"[WARNING] RSI_14가 여전히 없습니다. RSI 관련 컬럼: {[col for col in df.columns if 'rsi' in col.lower() or 'RSI' in col]}")

                return df
            except Exception as e:
                print(f"[WARNING] StrategyEngine 사용 실패: {e}. 기본 방법으로 전환.")
                import traceback
                traceback.print_exc()

        # 지표 설정
        indicators = config.get('indicators', [])

        for indicator in indicators:
            ind_type = indicator.get('type')
            params = indicator.get('params', {})

            if ind_type == 'SMA' or ind_type == 'MA':
                period = params.get('period', 20)
                df[f'SMA_{period}'] = df['close'].rolling(window=period).mean()

            elif ind_type == 'EMA':
                period = params.get('period', 20)
                df[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

            elif ind_type == 'RSI':
                period = params.get('period', 14)
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss.replace(0, 1e-10)  # Avoid division by zero
                df[f'RSI_{period}'] = 100 - (100 / (1 + rs))

            elif ind_type == 'MACD':
                fast = params.get('fast', 12)
                slow = params.get('slow', 26)
                signal = params.get('signal', 9)

                exp1 = df['close'].ewm(span=fast, adjust=False).mean()
                exp2 = df['close'].ewm(span=slow, adjust=False).mean()
                df['MACD'] = exp1 - exp2
                df['MACD_signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
                df['MACD_hist'] = df['MACD'] - df['MACD_signal']

            elif ind_type == 'BB':
                period = params.get('period', 20)
                std = params.get('std', 2)
                ma = df['close'].rolling(window=period).mean()
                std_dev = df['close'].rolling(window=period).std()
                df['BB_upper'] = ma + (std_dev * std)
                df['BB_lower'] = ma - (std_dev * std)
                df['BB_middle'] = ma

            elif ind_type == 'Stochastic':
                k_period = params.get('k_period', 14)
                d_period = params.get('d_period', 3)
                low_min = df['low'].rolling(window=k_period).min()
                high_max = df['high'].rolling(window=k_period).max()
                df['Stoch_K'] = 100 * ((df['close'] - low_min) / (high_max - low_min + 1e-10))
                df['Stoch_D'] = df['Stoch_K'].rolling(window=d_period).mean()

            elif ind_type == 'ATR':
                period = params.get('period', 14)
                high_low = df['high'] - df['low']
                high_close = np.abs(df['high'] - df['close'].shift())
                low_close = np.abs(df['low'] - df['close'].shift())
                ranges = pd.concat([high_low, high_close, low_close], axis=1)
                true_range = ranges.max(axis=1)
                df[f'ATR_{period}'] = true_range.rolling(window=period).mean()

            elif ind_type == 'OBV':
                df['OBV'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

            elif ind_type == 'ADX':
                period = params.get('period', 14)
                # Simplified ADX calculation
                plus_dm = df['high'].diff()
                minus_dm = -df['low'].diff()
                plus_dm[plus_dm < 0] = 0
                minus_dm[minus_dm < 0] = 0

                tr = pd.concat([
                    df['high'] - df['low'],
                    np.abs(df['high'] - df['close'].shift()),
                    np.abs(df['low'] - df['close'].shift())
                ], axis=1).max(axis=1)

                atr = tr.rolling(window=period).mean()
                plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
                minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
                dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di + 1e-10)
                df[f'ADX_{period}'] = dx.rolling(window=period).mean()

            elif ind_type == 'CCI':
                period = params.get('period', 20)
                tp = (df['high'] + df['low'] + df['close']) / 3
                ma = tp.rolling(window=period).mean()
                mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
                df[f'CCI_{period}'] = (tp - ma) / (0.015 * mad + 1e-10)

            elif ind_type == 'MFI':
                period = params.get('period', 14)
                tp = (df['high'] + df['low'] + df['close']) / 3
                mf = tp * df['volume']

                pos_mf = pd.Series(np.where(tp > tp.shift(), mf, 0), index=df.index)
                neg_mf = pd.Series(np.where(tp < tp.shift(), mf, 0), index=df.index)

                pos_mf_sum = pos_mf.rolling(window=period).sum()
                neg_mf_sum = neg_mf.rolling(window=period).sum()

                mfi = 100 - (100 / (1 + pos_mf_sum / (neg_mf_sum + 1e-10)))
                df[f'MFI_{period}'] = mfi

            elif ind_type == 'WILLIAMS_R':
                period = params.get('period', 14)
                high_max = df['high'].rolling(window=period).max()
                low_min = df['low'].rolling(window=period).min()
                df[f'WILLR_{period}'] = -100 * (high_max - df['close']) / (high_max - low_min + 1e-10)

        # Add PRICE column for template compatibility
        df['PRICE'] = df['close']

        # Add uppercase versions of common indicators for compatibility
        # This ensures both uppercase and lowercase versions are available
        for col in df.columns:
            if col.startswith('bb_'):
                uppercase_name = col.replace('bb_', 'BB_')
                df[uppercase_name] = df[col]
            elif col.startswith('rsi_'):
                uppercase_name = col.replace('rsi_', 'RSI_')
                df[uppercase_name] = df[col]
            elif col.startswith('macd'):
                uppercase_name = col.upper()
                df[uppercase_name] = df[col]
            elif col.startswith('sma_'):
                uppercase_name = col.replace('sma_', 'SMA_')
                df[uppercase_name] = df[col]
            elif col.startswith('ema_'):
                uppercase_name = col.replace('ema_', 'EMA_')
                df[uppercase_name] = df[col]

        return df

class SignalGenerator:
    """매매 신호 생성"""

    @staticmethod
    def evaluate_conditions(df: pd.DataFrame, conditions: List[Dict], signal_type: str) -> pd.Series:
        """조건 평가 및 신호 생성"""
        if not conditions:
            return pd.Series(0, index=df.index)

        # 각 조건을 평가
        condition_results = []

        for i, condition in enumerate(conditions):
            indicator = condition.get('indicator', '')
            operator = condition.get('operator', '')
            value = condition.get('value', 0)
            combine = condition.get('combineWith', 'AND' if i > 0 else None)

            # 지표 컬럼 확인
            if indicator not in df.columns:
                print(f"경고: 지표 {indicator}를 찾을 수 없습니다")
                continue

            ind_values = df[indicator]

            # 비교 값이 다른 지표인 경우
            if isinstance(value, str):
                # 문자열인 경우, 먼저 컬럼명인지 확인
                if value in df.columns:
                    compare_values = df[value]
                else:
                    # 컬럼명이 아니면 숫자로 변환 시도
                    try:
                        compare_values = float(value)
                    except ValueError:
                        print(f"경고: 값 '{value}'를 처리할 수 없습니다 (지표도 아니고 숫자도 아님)")
                        continue
            else:
                compare_values = float(value)

            # 조건 평가
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
                if condition_results[i][1] == 'AND':
                    final_result = final_result & condition_results[i][0]
                else:  # OR
                    final_result = final_result | condition_results[i][0]

            # 신호 생성 (진입 시점만)
            signal = pd.Series(0, index=df.index)
            signal[final_result & ~final_result.shift(1).fillna(False)] = 1 if signal_type == 'buy' else -1

            return signal

        return pd.Series(0, index=df.index)

    @staticmethod
    def evaluate_conditions_with_profit(df: pd.DataFrame, strategy_config: Dict,
                                       signal_type: str, positions: Dict = None,
                                       stock_code: str = 'TEST') -> pd.Series:
        """목표 수익률을 포함한 조건 평가 (단계별 목표 지원)"""

        # 1. 기본 지표 조건 평가
        if signal_type == 'sell':
            conditions = strategy_config.get('sellConditions', [])
        else:
            conditions = strategy_config.get('buyConditions', [])

        base_signal = SignalGenerator.evaluate_conditions(df, conditions, signal_type)

        # 2. 매도 시 목표 수익률 조건 추가 평가
        if signal_type == 'sell' and positions and stock_code in positions:
            target_profit = strategy_config.get('targetProfit', {})
            stop_loss = strategy_config.get('stopLoss', {})
            position = positions[stock_code]

            # 목표 수익률 신호 생성
            if target_profit:
                mode = target_profit.get('mode', 'simple')

                if mode == 'simple' and target_profit.get('simple', {}).get('enabled'):
                    # 단일 목표 모드
                    profit_signal = pd.Series(0, index=df.index)
                    target_value = target_profit['simple'].get('value', 5.0)

                    for idx in df.index:
                        current_price = df.loc[idx, 'close']
                        profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                        if profit_pct >= target_value:
                            profit_signal[idx] = -1  # 전량 매도 신호

                    # 기존 조건과 결합
                    combine_method = target_profit['simple'].get('combineWith', 'OR')
                    if combine_method == 'AND':
                        base_signal = base_signal & profit_signal
                    else:  # OR
                        base_signal = base_signal | profit_signal

                elif mode == 'staged' and target_profit.get('staged', {}).get('enabled'):
                    # 단계별 목표 모드
                    profit_signal = pd.Series(0, index=df.index)
                    staged_config = target_profit['staged']
                    stages = staged_config.get('stages', [])

                    # 이미 실행된 단계 추적
                    if not hasattr(position, 'executed_stages'):
                        position.executed_stages = []

                    for idx in df.index:
                        current_price = df.loc[idx, 'close']
                        profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                        # 각 단계별 목표 확인
                        for stage in stages:
                            stage_num = stage.get('stage', 1)
                            stage_target = stage.get('targetProfit', 5.0)
                            exit_ratio = stage.get('exitRatio', 100) / 100.0
                            stage_combine = stage.get('combineWith', staged_config.get('combineWith', 'OR'))

                            # 이미 실행된 단계는 스킵
                            if stage_num in position.executed_stages:
                                continue

                            if profit_pct >= stage_target:
                                # 각 단계별 결합 방식 저장
                                if not hasattr(profit_signal, 'stage_combines'):
                                    profit_signal.stage_combines = {}
                                profit_signal.stage_combines[idx] = stage_combine

                                # 부분 매도 신호 (비율 저장)
                                if not hasattr(profit_signal, 'exit_ratios'):
                                    profit_signal.exit_ratios = {}
                                profit_signal.exit_ratios[idx] = exit_ratio
                                profit_signal[idx] = -exit_ratio  # 음수로 매도 비율 표시
                                position.executed_stages.append(stage_num)

                                # 동적 손절 조정
                                if stage.get('dynamicStopLoss', False):
                                    # 손절선을 현재 단계의 목표 수익률로 상향
                                    if hasattr(position, 'dynamic_stop_loss'):
                                        position.dynamic_stop_loss = max(
                                            position.dynamic_stop_loss,
                                            position.avg_price * (1 + stage_target / 100)
                                        )
                                    else:
                                        position.dynamic_stop_loss = position.avg_price * (1 + stage_target / 100)
                                break  # 한 번에 하나의 단계만 실행

                    # 단계별 결합 방식 적용
                    # profit_signal에 각 인덱스별 결합 방식이 저장되어 있음
                    combined_signal = pd.Series(0, index=df.index)

                    for idx in df.index:
                        if profit_signal[idx] != 0:
                            # 해당 인덱스의 결합 방식 확인
                            stage_combine = getattr(profit_signal, 'stage_combines', {}).get(idx, 'OR')

                            if stage_combine == 'AND':
                                # AND: 지표 조건과 목표 수익 모두 충족
                                if base_signal[idx] != 0:
                                    combined_signal[idx] = profit_signal[idx]
                            else:  # OR
                                # OR: 둘 중 하나만 충족
                                if profit_signal[idx] != 0:
                                    combined_signal[idx] = profit_signal[idx]
                                elif base_signal[idx] != 0:
                                    combined_signal[idx] = base_signal[idx]
                        elif base_signal[idx] != 0:
                            # 목표 수익 미달성 시 지표 조건만 확인
                            combined_signal[idx] = base_signal[idx]

                    base_signal = combined_signal

            # 손절 조건 (항상 OR로 결합)
            if stop_loss.get('enabled'):
                loss_signal = pd.Series(0, index=df.index)
                loss_value = stop_loss.get('value', 3.0)

                # 트레일링 스톱 확인
                trailing_stop = stop_loss.get('trailingStop', {})

                for idx in df.index:
                    current_price = df.loc[idx, 'close']
                    profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                    # 동적 손절 확인 (Break Even Stop)
                    if hasattr(position, 'dynamic_stop_loss'):
                        dynamic_loss_pct = ((current_price - position.dynamic_stop_loss) / position.dynamic_stop_loss) * 100
                        if dynamic_loss_pct <= 0:
                            loss_signal[idx] = -1  # 동적 손절 매도
                            continue

                    # 트레일링 스톱 확인
                    if trailing_stop.get('enabled'):
                        activation = trailing_stop.get('activation', 5.0)
                        distance = trailing_stop.get('distance', 2.0)

                        # 최고가 추적
                        if not hasattr(position, 'peak_price'):
                            position.peak_price = position.avg_price

                        if profit_pct >= activation:
                            # 트레일링 스톱 활성화
                            position.peak_price = max(position.peak_price, current_price)
                            peak_drop_pct = ((current_price - position.peak_price) / position.peak_price) * 100

                            if peak_drop_pct <= -abs(distance):
                                loss_signal[idx] = -1  # 트레일링 스톱 매도
                                continue

                    # 일반 손절
                    if profit_pct <= -abs(loss_value):
                        loss_signal[idx] = -1  # 손절 매도

                # 손절은 항상 OR (즉시 실행)
                base_signal = base_signal | loss_signal

        return base_signal

class AdvancedBacktestEngine:
    """고급 백테스트 엔진"""

    def __init__(self, initial_capital: float = 10000000, commission: float = 0.00015, slippage: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.capital = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []

    def calculate_position_size(self, capital: float, price: float, config: Dict) -> int:
        """포지션 크기 계산"""
        position_sizing = config.get('positionSizing', {})
        method = position_sizing.get('method', 'fixed')

        if method == 'fixed':
            # 고정 금액
            amount = position_sizing.get('amount', capital * 0.1)
            shares = int(amount / price)
        elif method == 'percent':
            # 자본의 일정 비율
            percent = position_sizing.get('percent', 10) / 100
            amount = capital * percent
            shares = int(amount / price)
        elif method == 'kelly':
            # 켈리 공식 (win_rate과 avg_win/avg_loss 필요)
            win_rate = position_sizing.get('win_rate', 0.5)
            win_loss_ratio = position_sizing.get('win_loss_ratio', 1.5)
            kelly_percent = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
            kelly_percent = max(0, min(kelly_percent, 0.25))  # 최대 25% 제한
            amount = capital * kelly_percent
            shares = int(amount / price)
        else:
            # 기본값: 자본의 10%
            shares = int((capital * 0.1) / price)

        return max(0, shares)

    def execute_buy(self, stock_code: str, date: datetime, price: float, config: Dict) -> Optional[Trade]:
        """매수 실행"""
        # 분할매수 설정
        split_buy = config.get('splitBuy', {})
        enable_split = split_buy.get('enabled', False)
        split_count = split_buy.get('count', 1)
        split_interval = split_buy.get('interval', 'price')  # 'price' or 'time'

        # 슬리피지 적용
        actual_price = price * (1 + self.slippage)

        # 포지션 크기 계산
        position_size = self.calculate_position_size(self.capital, actual_price, config)

        if enable_split and split_count > 1:
            # 분할매수
            split_size = position_size // split_count
            if split_size <= 0:
                return None

            # 첫 번째 분할매수만 실행 (나머지는 조건 충족 시)
            position_size = split_size

        # 수수료 계산
        cost = position_size * actual_price * (1 + self.commission)

        if cost > self.capital:
            return None

        # 포지션 생성 또는 추가
        if stock_code in self.positions:
            # 기존 포지션에 추가 (피라미딩)
            position = self.positions[stock_code]
            position.add_partial(position_size, actual_price, date)
            action = 'buy_partial'
        else:
            # 새 포지션 생성
            self.positions[stock_code] = Position(
                stock_code=stock_code,
                quantity=position_size,
                avg_price=actual_price,
                entry_date=date,
                entry_reason='signal'
            )
            action = 'buy'

        # 자본 차감
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
        """매도 실행"""
        if stock_code not in self.positions:
            return None

        position = self.positions[stock_code]
        if position.quantity <= 0:
            return None

        # 분할매도 설정
        split_sell = config.get('splitSell', {})
        enable_split = split_sell.get('enabled', False)
        split_count = split_sell.get('count', 1)

        # 슬리피지 적용
        actual_price = price * (1 - self.slippage)

        # 매도 수량 결정
        if enable_split and split_count > 1:
            sell_quantity = position.quantity // split_count
            if sell_quantity <= 0:
                sell_quantity = position.quantity
        else:
            sell_quantity = position.quantity

        # 수익 계산
        profit = position.remove_partial(sell_quantity, actual_price, date)
        proceeds = sell_quantity * actual_price * (1 - self.commission)

        # 자본 증가
        self.capital += proceeds

        # 포지션 정리
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
        """백테스트 실행"""
        print(f"[DEBUG] AdvancedBacktestEngine.run 시작")
        print(f"[DEBUG] 입력 데이터 shape: {data.shape}")
        print(f"[DEBUG] 입력 데이터 컬럼: {list(data.columns)}")
        print(f"[DEBUG] USE_COMPLETE_INDICATORS: {USE_COMPLETE_INDICATORS}")
        print(f"[DEBUG] USE_STRATEGY_ENGINE: {USE_STRATEGY_ENGINE}")

        # 지표 계산 - 완전한 지표 모듈 사용 가능 시 우선 사용
        if USE_COMPLETE_INDICATORS:
            print(f"[DEBUG] CompleteIndicators 사용")
            data = CompleteIndicators.calculate_all(data, strategy_config)
        else:
            print(f"[DEBUG] TechnicalIndicators 사용")
            data = TechnicalIndicators.calculate_all(data, strategy_config)

        print(f"[DEBUG] 지표 계산 후 데이터 shape: {data.shape}")
        print(f"[DEBUG] 지표 계산 후 컬럼: {list(data.columns)[:30]}...")

        # 신호 생성
        buy_conditions = strategy_config.get('buyConditions', [])
        sell_conditions = strategy_config.get('sellConditions', [])

        print(f"[DEBUG] 매수 조건: {buy_conditions}")
        print(f"[DEBUG] 매도 조건: {sell_conditions}")

        # 목표 수익률 정보 출력
        target_profit = strategy_config.get('targetProfit', {})
        if target_profit.get('enabled'):
            print(f"[DEBUG] 목표 수익률: {target_profit.get('value')}%, 결합: {target_profit.get('combineWith', 'OR')}")

        data['buy_signal'] = SignalGenerator.evaluate_conditions(data, buy_conditions, 'buy')

        # 매도 신호는 포지션이 있을 때만 목표 수익률 고려
        if self.positions:
            data['sell_signal'] = SignalGenerator.evaluate_conditions_with_profit(
                data, strategy_config, 'sell', self.positions, 'TEST'
            )
        else:
            data['sell_signal'] = SignalGenerator.evaluate_conditions(data, sell_conditions, 'sell')

        # 백테스트 실행
        for i in range(len(data)):
            row = data.iloc[i]
            date = row['date']
            close = row['close']

            # 현재 포트폴리오 가치 계산
            portfolio_value = self.capital
            for stock_code, position in self.positions.items():
                portfolio_value += position.quantity * close
            self.equity_curve.append(portfolio_value)

            # 포지션이 있을 때 매도 신호 재계산 (목표 수익률 실시간 체크)
            if self.positions:
                current_sell_signal = SignalGenerator.evaluate_conditions_with_profit(
                    data.iloc[[i]], strategy_config, 'sell', self.positions, 'TEST'
                )
                if not current_sell_signal.empty and current_sell_signal.iloc[0] == -1:
                    for stock_code in list(self.positions.keys()):
                        position = self.positions[stock_code]
                        profit_pct = ((close - position.avg_price) / position.avg_price) * 100

                        # 목표 수익률 또는 손절 도달 시 로그
                        target_profit = strategy_config.get('targetProfit', {})
                        stop_loss = strategy_config.get('stopLoss', {})

                        if target_profit.get('enabled') and profit_pct >= target_profit.get('value', 5.0):
                            print(f"[목표 수익률 도달] {stock_code}: {profit_pct:.2f}% >= {target_profit.get('value')}%")
                        elif stop_loss.get('enabled') and profit_pct <= -abs(stop_loss.get('value', 3.0)):
                            print(f"[손절 실행] {stock_code}: {profit_pct:.2f}% <= -{stop_loss.get('value')}%")

                        self.execute_sell(stock_code, date, close, strategy_config)
            elif row['sell_signal'] == -1:
                # 포지션이 없으면 기본 매도 신호 사용
                for stock_code in list(self.positions.keys()):
                    self.execute_sell(stock_code, date, close, strategy_config)

            # 매수 신호 처리
            if row['buy_signal'] == 1:
                # 최대 포지션 수 체크
                max_positions = strategy_config.get('maxPositions', 1)
                if len(self.positions) < max_positions:
                    self.execute_buy('TEST', date, close, strategy_config)

        # 최종 포지션 정리
        if len(data) > 0:
            final_date = data.iloc[-1]['date']
            final_price = data.iloc[-1]['close']

            for stock_code in list(self.positions.keys()):
                position = self.positions[stock_code]
                if position.quantity > 0:
                    self.execute_sell(stock_code, final_date, final_price, strategy_config)

        # 성과 분석
        return self.analyze_performance()

    def analyze_performance(self) -> Dict[str, Any]:
        """성과 분석"""
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

        # 기본 통계
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100

        # 완료된 거래만 분석
        completed_trades = [t for t in self.trades if t.profit is not None]
        winning_trades = [t for t in completed_trades if t.profit > 0]
        losing_trades = [t for t in completed_trades if t.profit <= 0]

        win_rate = (len(winning_trades) / len(completed_trades) * 100) if completed_trades else 0

        # 평균 손익
        avg_win = np.mean([t.profit for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t.profit for t in losing_trades])) if losing_trades else 0

        # Profit Factor
        total_wins = sum([t.profit for t in winning_trades]) if winning_trades else 0
        total_losses = abs(sum([t.profit for t in losing_trades])) if losing_trades else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0

        # 최대 낙폭
        if self.equity_curve:
            equity_array = np.array(self.equity_curve)
            peak = np.maximum.accumulate(equity_array)
            drawdown = (peak - equity_array) / peak * 100
            max_drawdown = np.max(drawdown)
        else:
            max_drawdown = 0

        # Sharpe Ratio (일간 수익률 기준)
        if len(self.equity_curve) > 1:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
        else:
            sharpe_ratio = 0

        # 거래 상세 정보
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