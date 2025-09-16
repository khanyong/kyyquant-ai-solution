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
import sys
import os

def convert_numpy_to_native(obj):
    """Convert numpy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_numpy_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_native(item) for item in obj]
    else:
        return obj

# Core 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core 모듈 우선 임포트
try:
    from core import (
        compute_indicators,
        evaluate_conditions,
        _normalize_conditions,
        convert_legacy_column,
        _iname
    )
    USE_CORE = True
    print("[INFO] AdvancedBacktestEngine: Core 모듈 로드 성공")
except ImportError as e:
    USE_CORE = False
    print(f"[WARNING] AdvancedBacktestEngine: Core 모듈 로드 실패: {e}")

# 폴백: 기존 모듈들
try:
    from indicators_complete import CompleteIndicators
    USE_COMPLETE_INDICATORS = True
except ImportError:
    USE_COMPLETE_INDICATORS = False

try:
    from strategy_engine import StrategyEngine
    USE_STRATEGY_ENGINE = True
    if not USE_CORE:
        print("[INFO] AdvancedBacktestEngine: strategy_engine.py를 사용합니다.")
except ImportError:
    USE_STRATEGY_ENGINE = False
    if not USE_CORE:
        print("[WARNING] AdvancedBacktestEngine: strategy_engine.py를 찾을 수 없습니다.")

@dataclass
class Position:
    """포지션 정보"""
    stock_code: str
    quantity: int
    avg_price: float
    entry_date: datetime
    entry_reason: str
    entry_signal_details: Dict = field(default_factory=dict)  # 매수 신호 상세
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
    stock_name: str = ""  # 종목명
    action: str = ""  # 'buy', 'sell', 'buy_partial', 'sell_partial'
    quantity: int = 0
    price: float = 0
    commission: float = 0
    slippage: float = 0
    profit: Optional[float] = None
    profit_pct: Optional[float] = None
    position_size: Optional[int] = None  # 거래 후 포지션 크기
    signal_reason: str = ""  # 매매 이유
    signal_details: Dict = field(default_factory=dict)  # 신호 상세 정보

# 유틸리티 함수들
def _iname(base: str, *params) -> str:
    """지표명 생성 - 모든 파라미터를 소문자로 변환하여 연결"""
    parts = [str(base).lower()] + [str(p).lower() for p in params if p is not None]
    return "_".join(parts)

def _lc(s):
    """문자열을 소문자로 변환"""
    return s.lower() if isinstance(s, str) else s

def _normalize_conditions(conditions):
    """조건 정규화 - 지표명, 연산자, 값을 소문자화"""
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
    """기술적 지표 계산 클래스 - Core 모듈 사용 시 건너뜀"""

    @staticmethod
    def compute_all(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """Core 모듈 사용 시 위임"""
        if USE_CORE:
            return compute_indicators(df, config)
        # 기존 로직 유지
        return TechnicalIndicators._legacy_compute(df, config)

    @staticmethod
    def _legacy_compute(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
        """레거시 지표 계산"""
        # 기존 calculate_all 메서드로 위임
        return TechnicalIndicators.calculate_all(df, config)

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

                # price 별칭 추가
                df['price'] = df['close']

                print(f"[INFO] StrategyEngine에서 모든 지표 계산 완료")
                print(f"[DEBUG] 사용 가능한 컬럼: {list(df.columns)}")

                # Check if rsi_14 exists
                if 'rsi_14' in df.columns:
                    print(f"[DEBUG] rsi_14 발견! 샘플 값: {df['rsi_14'].iloc[-5:].values}")
                else:
                    print(f"[WARNING] rsi_14가 여전히 없습니다. RSI 관련 컬럼: {[col for col in df.columns if 'rsi' in col.lower()]}")

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
                df[_iname('sma', period)] = df['close'].rolling(window=period).mean()
                df[_iname('ma', period)] = df[_iname('sma', period)]  # 동일 값 제공

            elif ind_type == 'EMA':
                period = params.get('period', 20)
                df[_iname('ema', period)] = df['close'].ewm(span=period, adjust=False).mean()

            elif ind_type == 'RSI':
                # Wilder RSI 표준 산식
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
                # Wilder ATR 표준 산식
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
                # 표준 ADX 산식 (Wilder 방식)
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

        # price 별칭 추가 (close와 동일)
        df['price'] = df['close']

        return df

class SignalGenerator:
    """매매 신호 생성"""

    @staticmethod
    def evaluate_conditions(df: pd.DataFrame, conditions: List[Dict], signal_type: str) -> pd.Series:
        """조건 평가 및 신호 생성"""
        if not conditions:
            return pd.Series(0, index=df.index)

        # 조건 정규화
        conditions = _normalize_conditions(conditions)

        # 각 조건을 평가
        condition_results = []

        for i, condition in enumerate(conditions):
            indicator = condition.get('indicator', '')
            operator = condition.get('operator', '')
            value = condition.get('value', 0)
            combine = condition.get('combineWith', 'and' if i > 0 else None)

            # 지표 컬럼 확인
            if indicator not in df.columns:
                # 운영 환경에서는 경고만 출력
                if signal_type == 'buy':
                    print(f"경고: 매수 조건의 지표 '{indicator}'를 찾을 수 없습니다")
                else:
                    print(f"경고: 매도 조건의 지표 '{indicator}'를 찾을 수 없습니다")
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
                if condition_results[i][1] == 'and':
                    final_result = final_result & condition_results[i][0]
                else:  # or
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

                if mode == 'simple' and target_profit.get('enabled'):
                    # 단일 목표 모드 (이전 버전 호환성)
                    profit_signal = pd.Series(0, index=df.index)

                    # simple 모드: enabled가 직접 있거나 simple.enabled가 있는 경우 처리
                    if target_profit.get('simple'):
                        target_value = target_profit['simple'].get('value', 5.0)
                        combine_method = _lc(target_profit['simple'].get('combineWith', 'or'))
                    else:
                        # 이전 버전 호환성
                        target_value = target_profit.get('value', 5.0)
                        combine_method = _lc(target_profit.get('combineWith', 'or'))

                    for idx in df.index:
                        current_price = df.loc[idx, 'close']
                        profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                        if profit_pct >= target_value:
                            profit_signal[idx] = -1  # 전량 매도 신호

                    # 기존 조건과 결합
                    if combine_method == 'and':
                        base_signal = base_signal & profit_signal
                    else:  # or
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
                            stage_combine = _lc(stage.get('combineWith', staged_config.get('combineWith', 'or')))

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
                            stage_combine = _lc(getattr(profit_signal, 'stage_combines', {}).get(idx, 'or'))

                            if stage_combine == 'and':
                                # AND: 지표 조건과 목표 수익 모두 충족
                                if base_signal[idx] != 0:
                                    combined_signal[idx] = profit_signal[idx]
                            else:  # or
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
        self.stock_names: Dict[str, str] = {}  # 종목코드 -> 종목명 매핑

    def get_stock_name(self, stock_code: str) -> str:
        """종목명 조회"""
        # 주요 종목 매핑 (실제 환경에서는 DB나 API 사용)
        stock_map = {
            '005930': '삼성전자',
            '000660': 'SK하이닉스',
            '035420': 'NAVER',
            '035720': '카카오',
            '051910': 'LG화학',
            '006400': '삼성SDI',
            '207940': '삼성바이오로직스',
            '005380': '현대차',
            '000270': '기아',
            '068270': '셀트리온',
            '105560': 'KB금융',
            '055550': '신한지주',
            '086790': '하나금융지주',
            '316140': '우리금융지주',
            '034730': 'SK',
            '015760': '한국전력',
            '032830': '삼성생명',
            '003550': 'LG',
            '034220': 'LG디스플레이',
            '009150': '삼성전기'
        }
        return self.stock_names.get(stock_code, stock_map.get(stock_code, stock_code))

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

    def execute_buy(self, stock_code: str, date: datetime, price: float, config: Dict,
                    signal_reason: str = "", signal_details: Dict = None) -> Optional[Trade]:
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
                entry_reason=signal_reason or 'signal',
                entry_signal_details=signal_details or {}
            )
            action = 'buy'

        # 자본 차감
        self.capital -= cost

        # 거래 기록
        trade = Trade(
            date=date,
            stock_code=stock_code,
            stock_name=self.get_stock_name(stock_code),
            action=action,
            quantity=position_size,
            price=actual_price,
            commission=self.commission,
            slippage=self.slippage,
            position_size=self.positions[stock_code].quantity,
            signal_reason=signal_reason or 'signal',
            signal_details=signal_details or {}
        )
        self.trades.append(trade)

        return trade

    def execute_sell(self, stock_code: str, date: datetime, price: float, config: Dict,
                     exit_reason: str = "", exit_details: Dict = None) -> Optional[Trade]:
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
            stock_name=self.get_stock_name(stock_code),
            action=action,
            quantity=sell_quantity,
            price=actual_price,
            commission=self.commission,
            slippage=self.slippage,
            profit=profit,
            profit_pct=(profit / (position.avg_price * sell_quantity)) * 100 if position.avg_price > 0 else 0,
            position_size=position.quantity if stock_code in self.positions else 0,
            signal_reason=exit_reason or 'signal',
            signal_details=exit_details or {}
        )
        self.trades.append(trade)

        return trade

    def run(self, data: pd.DataFrame, strategy_config: Dict) -> Dict[str, Any]:
        """백테스트 실행 - Core 모듈 우선 사용"""
        print(f"[DEBUG] AdvancedBacktestEngine.run 시작")
        print(f"[DEBUG] 입력 데이터 shape: {data.shape}")
        print(f"[DEBUG] Core 모듈 사용: {USE_CORE}")

        # Core 모듈 사용 시
        if USE_CORE:
            print("[DEBUG] Core 모듈로 처리")

            # params 구조 자동 수정
            indicators = strategy_config.get('indicators', [])
            fixed_indicators = []
            for ind in indicators:
                if 'params' not in ind and 'period' in ind:
                    fixed_ind = {
                        'type': ind.get('type', 'MA').upper(),
                        'params': {'period': ind.get('period', 20)}
                    }
                    print(f"[FIX] 지표 구조: {ind} → {fixed_ind}")
                    fixed_indicators.append(fixed_ind)
                else:
                    fixed_indicators.append(ind)

            # 조건 가져오기 (정규화는 evaluate_conditions에서 처리)
            buy_conditions = strategy_config.get('buyConditions', [])
            sell_conditions = strategy_config.get('sellConditions', [])

            # Core 설정
            config = {
                **strategy_config,
                'indicators': fixed_indicators,
                'buyConditions': buy_conditions,
                'sellConditions': sell_conditions
            }

            # 지표 계산
            data = compute_indicators(data, config)

            # 신호 생성 (evaluate_conditions는 DataFrame을 반환)
            data_with_signals = evaluate_conditions(data, buy_conditions, sell_conditions)
            data = data_with_signals  # DataFrame 전체를 교체

            buy_count = (data['buy_signal'] == 1).sum()
            sell_count = (data['sell_signal'] == -1).sum()
            print(f"[Core] 신호: 매수 {buy_count}, 매도 {sell_count}")

        # 폴백: 기존 방식
        elif USE_COMPLETE_INDICATORS:
            print(f"[DEBUG] CompleteIndicators 사용")
            data = CompleteIndicators.calculate_all(data, strategy_config)
        else:
            print(f"[DEBUG] TechnicalIndicators 사용")
            data = TechnicalIndicators.calculate_all(data, strategy_config)

        print(f"[DEBUG] 지표 계산 후 데이터 shape: {data.shape}")
        print(f"[DEBUG] 지표 계산 후 컬럼: {list(data.columns)[:30]}...")

        # Core 모듈을 사용하지 않는 경우에만 기존 신호 생성
        if not USE_CORE:
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

            # strategy_engine을 사용하여 상세 신호 정보 가져오기
            signal_reason_buy = ""
            signal_details_buy = {}
            signal_reason_sell = ""
            signal_details_sell = {}

            # USE_STRATEGY_ENGINE이 활성화되어 있고 strategy_engine이 사용 가능한 경우
            if USE_STRATEGY_ENGINE:
                try:
                    from strategy_engine import strategy_engine
                    # 매수/매도 신호 및 상세 정보 가져오기
                    signal_result = strategy_engine.generate_signal(data, date, strategy_config)
                    if isinstance(signal_result, tuple):
                        signal_type, reason, details = signal_result
                        if signal_type == 'buy':
                            signal_reason_buy = reason
                            signal_details_buy = details
                            # 첫 번째 매수 신호에 대해서만 디버그 출력
                            if not hasattr(self, '_debug_buy_printed'):
                                print(f"[DEBUG] 매수 신호 상세: {reason}")
                                self._debug_buy_printed = True
                        elif signal_type == 'sell':
                            signal_reason_sell = reason
                            signal_details_sell = details
                            # 첫 번째 매도 신호에 대해서만 디버그 출력
                            if not hasattr(self, '_debug_sell_printed'):
                                print(f"[DEBUG] 매도 신호 상세: {reason}")
                                self._debug_sell_printed = True
                except Exception as e:
                    print(f"[DEBUG] strategy_engine 신호 생성 실패: {e}")
            else:
                # USE_STRATEGY_ENGINE이 False인 경우 디버그
                if not hasattr(self, '_debug_engine_printed'):
                    print(f"[DEBUG] USE_STRATEGY_ENGINE={USE_STRATEGY_ENGINE}, USE_CORE={USE_CORE}")
                    self._debug_engine_printed = True

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

                        exit_reason = ""
                        exit_details = {}

                        if target_profit.get('enabled') and profit_pct >= target_profit.get('value', 5.0):
                            print(f"[목표 수익률 도달] {stock_code}: {profit_pct:.2f}% >= {target_profit.get('value')}%")
                            exit_reason = f"목표 수익률 도달 ({profit_pct:.2f}% >= {target_profit.get('value')}%)"
                            exit_details = {'type': 'target_profit', 'profit_pct': profit_pct, 'target': target_profit.get('value')}
                        elif stop_loss.get('enabled') and profit_pct <= -abs(stop_loss.get('value', 3.0)):
                            print(f"[손절 실행] {stock_code}: {profit_pct:.2f}% <= -{stop_loss.get('value')}%")
                            exit_reason = f"손절 실행 ({profit_pct:.2f}% <= -{stop_loss.get('value')}%)"
                            exit_details = {'type': 'stop_loss', 'loss_pct': profit_pct, 'stop_loss': stop_loss.get('value')}
                        else:
                            # strategy_engine에서 가져온 상세 정보 사용
                            exit_reason = signal_reason_sell if signal_reason_sell else "매도 신호 발생"
                            exit_details = signal_details_sell if signal_details_sell else {'type': 'signal', 'signal_value': row.get('sell_signal', -1)}

                        self.execute_sell(stock_code, date, close, strategy_config, exit_reason, exit_details)
            elif row['sell_signal'] == -1:
                # 포지션이 없으면 기본 매도 신호 사용
                for stock_code in list(self.positions.keys()):
                    exit_reason = signal_reason_sell if signal_reason_sell else "매도 신호 발생"
                    exit_details = signal_details_sell if signal_details_sell else {'type': 'signal', 'signal_value': -1}
                    self.execute_sell(stock_code, date, close, strategy_config, exit_reason, exit_details)

            # 매수 신호 처리
            if row['buy_signal'] == 1:
                # 최대 포지션 수 체크
                max_positions = strategy_config.get('maxPositions', 1)
                if len(self.positions) < max_positions:
                    # strategy_engine에서 가져온 상세 정보 사용
                    signal_reason = signal_reason_buy if signal_reason_buy else "매수 신호 발생"
                    signal_details = signal_details_buy if signal_details_buy else {'type': 'signal', 'signal_value': 1}
                    self.execute_buy('TEST', date, close, strategy_config, signal_reason, signal_details)

        # 최종 포지션 정리
        if len(data) > 0:
            final_date = data.iloc[-1]['date']
            final_price = data.iloc[-1]['close']

            for stock_code in list(self.positions.keys()):
                position = self.positions[stock_code]
                if position.quantity > 0:
                    exit_reason = "백테스트 종료 - 포지션 청산"
                    exit_details = {'type': 'backtest_end'}
                    self.execute_sell(stock_code, final_date, final_price, strategy_config, exit_reason, exit_details)

        # 성과 분석
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
            trade_details.append(convert_numpy_to_native({
                'date': trade.date.isoformat() if isinstance(trade.date, datetime) else str(trade.date),
                'stock_code': trade.stock_code,
                'stock_name': trade.stock_name,
                'action': trade.action,
                'quantity': trade.quantity,
                'price': trade.price,
                'signal_reason': trade.signal_reason,
                'signal_details': trade.signal_details,
                'profit': trade.profit,
                'profit_pct': trade.profit_pct,
                'position_size': trade.position_size
            }))

        return convert_numpy_to_native({
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
        })
