"""
기술적 지표 계산기 v3 - 정확성과 신뢰성 강화 버전
Supabase 연동 + 표준 지표 정의 + 보안 샌드박스
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
import os
import json
import ast
import traceback
import time
import logging
from functools import wraps, lru_cache
from supabase import create_client

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExecOptions:
    """지표 실행 옵션"""
    period: int = 20
    realtime: bool = False  # True: 현재 봉 제외 (shift(1))
    min_periods: Optional[int] = None  # 초기값 정책

    def __post_init__(self):
        if self.min_periods is None:
            self.min_periods = self.period

@dataclass
class IndicatorResult:
    """지표 계산 결과"""
    columns: Dict[str, pd.Series]  # 출력 컬럼
    metadata: Dict[str, Any]  # 메타데이터
    execution_time_ms: float
    nan_ratio: float
    warnings: List[str]

class SecuritySandbox:
    """보안 샌드박스 for custom_formula/python_code"""

    # 허용된 AST 노드 타입
    ALLOWED_NODES = {
        ast.Module, ast.Expr, ast.Load, ast.Store, ast.Del,
        ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
        ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd,
        ast.FloorDiv, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
        ast.Is, ast.IsNot, ast.In, ast.NotIn, ast.And, ast.Or, ast.Not,
        ast.Name, ast.Constant, ast.Num, ast.Str, ast.List, ast.Tuple,
        ast.Dict, ast.Set, ast.Subscript, ast.Slice, ast.Index,
        ast.Call, ast.Attribute, ast.IfExp, ast.ListComp,
        ast.FunctionDef, ast.Return, ast.Assign, ast.AugAssign,
        ast.For, ast.If, ast.While, ast.Break, ast.Continue
    }

    # 허용된 함수/속성
    ALLOWED_NAMES = {
        # 기본
        'True', 'False', 'None', 'abs', 'min', 'max', 'sum', 'len', 'range',
        'round', 'int', 'float', 'str', 'list', 'dict', 'tuple', 'set',
        # NumPy
        'np', 'array', 'mean', 'std', 'sqrt', 'log', 'exp', 'nan', 'inf',
        # Pandas
        'pd', 'DataFrame', 'Series', 'rolling', 'ewm', 'shift', 'diff',
        # 지표 관련
        'df', 'params', 'result', 'calculate'
    }

    @staticmethod
    def validate_ast(code: str) -> bool:
        """AST 검증 - 허용된 노드만 사용하는지 확인"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if type(node) not in SecuritySandbox.ALLOWED_NODES:
                    logger.warning(f"Blocked AST node: {type(node).__name__}")
                    return False

                # Import 차단
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    logger.warning("Import statements not allowed")
                    return False

                # 위험한 함수 호출 차단
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['eval', 'exec', 'compile', '__import__']:
                            logger.warning(f"Blocked function: {node.func.id}")
                            return False

            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in code: {e}")
            return False

    @staticmethod
    def create_safe_namespace() -> Dict[str, Any]:
        """안전한 네임스페이스 생성"""
        return {
            '__builtins__': {},  # 빌트인 차단
            'pd': pd,
            'np': np,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'len': len,
            'range': range,
            'round': round,
            'int': int,
            'float': float,
            'True': True,
            'False': False,
            'None': None
        }

class IndicatorRegistry:
    """지표 레지스트리 - 표준 지표 관리"""

    def __init__(self):
        self._indicators = {}
        self._register_builtin_indicators()

    def _register_builtin_indicators(self):
        """내장 지표 등록"""
        # 이동평균
        self.register('sma', self._calc_sma, ['close'], ['sma'])
        self.register('ema', self._calc_ema, ['close'], ['ema'])
        self.register('wma', self._calc_wma, ['close'], ['wma'])

        # 오실레이터
        self.register('rsi', self._calc_rsi_wilder, ['close'], ['rsi'])
        self.register('stochastic', self._calc_stochastic, ['high', 'low', 'close'], ['stoch_k', 'stoch_d'])
        self.register('cci', self._calc_cci_optimized, ['high', 'low', 'close'], ['cci'])
        self.register('williams_r', self._calc_williams_r, ['high', 'low', 'close'], ['williams_r'])

        # 변동성
        self.register('bb', self._calc_bollinger_bands, ['close'], ['bb_upper', 'bb_middle', 'bb_lower'])
        self.register('atr', self._calc_atr_wilder, ['high', 'low', 'close'], ['atr'])

        # 트렌드
        self.register('macd', self._calc_macd, ['close'], ['macd_line', 'macd_signal', 'macd_hist'])
        self.register('adx', self._calc_adx_wilder, ['high', 'low', 'close'], ['adx', 'plus_di', 'minus_di'])
        self.register('psar', self._calc_psar_clamped, ['high', 'low'], ['psar'])

        # 볼륨
        self.register('obv', self._calc_obv_vectorized, ['close', 'volume'], ['obv'])
        self.register('vwap', self._calc_vwap_session, ['high', 'low', 'close', 'volume'], ['vwap'])

        # 일목균형표
        self.register('ichimoku', self._calc_ichimoku, ['high', 'low', 'close'],
                      ['tenkan', 'kijun', 'senkou_a', 'senkou_b', 'chikou'])

    def register(self, name: str, func: callable, required_cols: List[str], output_cols: List[str]):
        """지표 등록"""
        self._indicators[name] = {
            'function': func,
            'required_columns': required_cols,
            'output_columns': output_cols
        }

    def get(self, name: str) -> Optional[Dict]:
        """지표 정보 반환"""
        return self._indicators.get(name)

    def execute(self, name: str, df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """지표 실행"""
        indicator = self.get(name)
        if not indicator:
            raise ValueError(f"Unknown indicator: {name}")

        # Realtime 모드 처리 (현재 봉 제외)
        if options.realtime:
            df = df.copy()
            for col in indicator['required_columns']:
                if col in df.columns:
                    df[col] = df[col].shift(1)

        # 지표 함수 실행
        result = indicator['function'](df, options)

        # 결과 정렬
        if isinstance(result, dict):
            for key in result:
                result[key] = result[key].reindex(df.index)

        return result

    # === 표준 지표 구현 (수학적 정의 준수) ===

    @staticmethod
    def _calc_sma(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Simple Moving Average"""
        return {'sma': df['close'].rolling(window=options.period, min_periods=options.min_periods).mean()}

    @staticmethod
    def _calc_ema(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Exponential Moving Average"""
        return {'ema': df['close'].ewm(span=options.period, min_periods=options.min_periods, adjust=False).mean()}

    @staticmethod
    def _calc_wma(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Weighted Moving Average"""
        weights = np.arange(1, options.period + 1)
        wma = df['close'].rolling(window=options.period, min_periods=options.min_periods).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
        return {'wma': wma}

    @staticmethod
    def _calc_rsi_wilder(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """RSI - Wilder's method"""
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        # Wilder's smoothing
        avg_gain = gain.ewm(alpha=1/options.period, min_periods=options.min_periods, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/options.period, min_periods=options.min_periods, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan)  # 분모 0 방지
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.clip(0, 100)  # 범위 제한

        return {'rsi': rsi}

    @staticmethod
    def _calc_stochastic(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Stochastic Oscillator"""
        k_period = options.period
        d_period = options.period // 3 if options.period >= 6 else 3

        low_min = df['low'].rolling(window=k_period, min_periods=options.min_periods).min()
        high_max = df['high'].rolling(window=k_period, min_periods=options.min_periods).max()

        # 분모 0 방지
        denominator = high_max - low_min
        denominator = denominator.replace(0, np.nan)

        stoch_k = 100 * ((df['close'] - low_min) / denominator)
        stoch_k = stoch_k.clip(0, 100)
        stoch_d = stoch_k.rolling(window=d_period, min_periods=1).mean()

        return {'stoch_k': stoch_k, 'stoch_d': stoch_d}

    @staticmethod
    def _calc_cci_optimized(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """CCI - Optimized with MAD"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=options.period, min_periods=options.min_periods).mean()

        # Mean Absolute Deviation (MAD) - 벡터화
        mad = typical_price.rolling(window=options.period, min_periods=options.min_periods).apply(
            lambda x: np.abs(x - x.mean()).mean(), raw=True
        )

        # 분모 0 방지
        mad = mad.replace(0, np.nan)
        cci = (typical_price - sma) / (0.015 * mad)

        return {'cci': cci}

    @staticmethod
    def _calc_williams_r(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Williams %R"""
        highest = df['high'].rolling(window=options.period, min_periods=options.min_periods).max()
        lowest = df['low'].rolling(window=options.period, min_periods=options.min_periods).min()

        # 분모 0 방지
        denominator = highest - lowest
        denominator = denominator.replace(0, np.nan)

        williams_r = -100 * ((highest - df['close']) / denominator)
        williams_r = williams_r.clip(-100, 0)  # 범위 제한

        return {'williams_r': williams_r}

    @staticmethod
    def _calc_bollinger_bands(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Bollinger Bands with ddof=0"""
        middle = df['close'].rolling(window=options.period, min_periods=options.min_periods).mean()
        std = df['close'].rolling(window=options.period, min_periods=options.min_periods).std(ddof=0)  # ddof=0

        std_mult = 2  # 기본값
        upper = middle + (std * std_mult)
        lower = middle - (std * std_mult)

        return {'bb_upper': upper, 'bb_middle': middle, 'bb_lower': lower}

    @staticmethod
    def _calc_atr_wilder(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """ATR - Wilder's method"""
        high = df['high']
        low = df['low']
        close = df['close'].shift(1)

        tr1 = high - low
        tr2 = (high - close).abs()
        tr3 = (low - close).abs()

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Wilder's smoothing
        atr = true_range.ewm(alpha=1/options.period, min_periods=options.min_periods, adjust=False).mean()

        return {'atr': atr}

    @staticmethod
    def _calc_macd(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """MACD"""
        fast = 12
        slow = 26
        signal = 9

        ema_fast = df['close'].ewm(span=fast, min_periods=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, min_periods=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span=signal, min_periods=signal, adjust=False).mean()
        macd_hist = macd_line - macd_signal

        return {
            'macd_line': macd_line,
            'macd_signal': macd_signal,
            'macd_hist': macd_hist
        }

    @staticmethod
    def _calc_adx_wilder(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """ADX/DMI - Wilder's method"""
        high = df['high']
        low = df['low']
        close = df['close']

        # Directional Movement
        plus_dm = high.diff()
        minus_dm = -low.diff()

        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        plus_dm[plus_dm < minus_dm] = 0
        minus_dm[minus_dm < plus_dm] = 0

        # True Range
        tr = pd.concat([
            high - low,
            (high - close.shift()).abs(),
            (low - close.shift()).abs()
        ], axis=1).max(axis=1)

        # Wilder's smoothing
        atr = tr.ewm(alpha=1/options.period, min_periods=options.min_periods, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/options.period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/options.period, adjust=False).mean() / atr)

        # DX and ADX
        dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
        adx = dx.ewm(alpha=1/options.period, min_periods=options.min_periods, adjust=False).mean()

        return {
            'adx': adx,
            'plus_di': plus_di,
            'minus_di': minus_di
        }

    @staticmethod
    def _calc_psar_clamped(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Parabolic SAR with 2-bar clamp"""
        high = df['high']
        low = df['low']

        # 초기값
        psar = low.iloc[0]
        trend = 1  # 1: uptrend, -1: downtrend
        ep = high.iloc[0]  # Extreme Point
        af = 0.02  # Acceleration Factor
        max_af = 0.2

        psar_values = [psar]

        for i in range(1, len(df)):
            # SAR 업데이트
            psar = psar + af * (ep - psar)

            if trend == 1:  # Uptrend
                # 2-bar clamp
                psar = min(psar, low.iloc[i-1])
                if i >= 2:
                    psar = min(psar, low.iloc[i-2])

                if low.iloc[i] < psar:
                    # Trend reversal
                    trend = -1
                    psar = ep
                    ep = low.iloc[i]
                    af = 0.02
                else:
                    if high.iloc[i] > ep:
                        ep = high.iloc[i]
                        af = min(af + 0.02, max_af)
            else:  # Downtrend
                # 2-bar clamp
                psar = max(psar, high.iloc[i-1])
                if i >= 2:
                    psar = max(psar, high.iloc[i-2])

                if high.iloc[i] > psar:
                    # Trend reversal
                    trend = 1
                    psar = ep
                    ep = high.iloc[i]
                    af = 0.02
                else:
                    if low.iloc[i] < ep:
                        ep = low.iloc[i]
                        af = min(af + 0.02, max_af)

            psar_values.append(psar)

        return {'psar': pd.Series(psar_values, index=df.index)}

    @staticmethod
    def _calc_obv_vectorized(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """OBV - Vectorized"""
        price_diff = df['close'].diff()
        volume_direction = np.where(price_diff > 0, 1, np.where(price_diff < 0, -1, 0))
        obv = (df['volume'] * volume_direction).cumsum()

        return {'obv': obv}

    @staticmethod
    def _calc_vwap_session(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """VWAP with session reset option"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3

        # 세션 경계 감지 (날짜 변경)
        if isinstance(df.index, pd.DatetimeIndex):
            session_breaks = df.index.date != df.index.date.shift(1)
            session_id = session_breaks.cumsum()

            vwap = df.groupby(session_id).apply(
                lambda x: ((x['volume'] * typical_price.loc[x.index]).cumsum() /
                          x['volume'].cumsum())
            ).droplevel(0)
        else:
            # 세션 구분 없이 누적
            vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()

        return {'vwap': vwap}

    @staticmethod
    def _calc_ichimoku(df: pd.DataFrame, options: ExecOptions) -> Dict[str, pd.Series]:
        """Ichimoku Cloud"""
        # 기간 설정
        tenkan_period = 9
        kijun_period = 26
        senkou_period = 52
        chikou_period = 26

        # Tenkan-sen
        tenkan = (df['high'].rolling(tenkan_period).max() +
                 df['low'].rolling(tenkan_period).min()) / 2

        # Kijun-sen
        kijun = (df['high'].rolling(kijun_period).max() +
                df['low'].rolling(kijun_period).min()) / 2

        # Senkou Span A (26 periods ahead)
        senkou_a = ((tenkan + kijun) / 2).shift(kijun_period)

        # Senkou Span B (26 periods ahead)
        senkou_b = ((df['high'].rolling(senkou_period).max() +
                    df['low'].rolling(senkou_period).min()) / 2).shift(kijun_period)

        # Chikou Span (26 periods behind)
        chikou = df['close'].shift(-chikou_period)

        return {
            'tenkan': tenkan,
            'kijun': kijun,
            'senkou_a': senkou_a,
            'senkou_b': senkou_b,
            'chikou': chikou
        }


class IndicatorCalculator:
    """지표 계산기 v3 - 정확성과 신뢰성 강화"""

    def __init__(self):
        self.registry = IndicatorRegistry()
        self.sandbox = SecuritySandbox()
        self._init_database()
        self.indicators_cache = {}
        self._load_indicators()
        self._execution_cache = {}  # 중복 계산 방지

    def _init_database(self):
        """Supabase 연결"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

            if url and key:
                self.supabase = create_client(url, key)
                logger.info("Supabase connected successfully")
            else:
                self.supabase = None
                logger.warning("No Supabase connection")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self.supabase = None

    def _load_indicators(self):
        """Supabase에서 지표 로드"""
        if not self.supabase:
            return

        try:
            response = self.supabase.table('indicators').select('*').eq('is_active', True).execute()
            if response.data:
                for indicator in response.data:
                    self.indicators_cache[indicator['name']] = indicator
                logger.info(f"Loaded {len(self.indicators_cache)} indicators from database")
        except Exception as e:
            logger.error(f"Failed to load indicators: {e}")

    def calculate(self, df: pd.DataFrame, config: Dict[str, Any], options: Optional[ExecOptions] = None) -> IndicatorResult:
        """지표 계산 - 메인 엔트리포인트"""
        start_time = time.time()
        warnings = []

        # 기본 옵션
        if options is None:
            options = ExecOptions(
                period=config.get('params', {}).get('period', 20),
                realtime=config.get('realtime', False)
            )

        # 입력 검증
        df = self._validate_input(df, warnings)

        indicator_name = config.get('name')
        calculation_type = config.get('calculation_type', 'builtin')

        try:
            # 캐시 확인
            cache_key = self._get_cache_key(indicator_name, options)
            if cache_key in self._execution_cache:
                cached_result = self._execution_cache[cache_key]
                logger.info(f"Using cached result for {indicator_name}")
                return cached_result

            # 계산 타입별 처리
            if calculation_type == 'builtin' or indicator_name in self.registry._indicators:
                result_columns = self._calculate_builtin(df, indicator_name, options)
            elif calculation_type == 'custom_formula':
                result_columns = self._calculate_custom_formula(df, config, options)
            elif calculation_type == 'python_code':
                result_columns = self._calculate_python_code(df, config, options)
            else:
                # Supabase에서 로드한 지표
                indicator_def = self.indicators_cache.get(indicator_name)
                if indicator_def:
                    result_columns = self._calculate_from_definition(df, indicator_def, options)
                else:
                    raise ValueError(f"Unknown indicator: {indicator_name}")

            # 결과 생성
            execution_time = (time.time() - start_time) * 1000
            nan_ratio = self._calculate_nan_ratio(result_columns)

            result = IndicatorResult(
                columns=result_columns,
                metadata={
                    'indicator': indicator_name,
                    'calculation_type': calculation_type,
                    'engine': 'v3',
                    'options': options.__dict__
                },
                execution_time_ms=execution_time,
                nan_ratio=nan_ratio,
                warnings=warnings
            )

            # 캐시 저장
            self._execution_cache[cache_key] = result

            # 로깅
            logger.info(f"Calculated {indicator_name}: {len(result_columns)} columns, "
                       f"{execution_time:.2f}ms, NaN ratio: {nan_ratio:.2%}")

            return result

        except Exception as e:
            logger.error(f"Failed to calculate {indicator_name}: {e}")
            traceback.print_exc()
            raise

    def _validate_input(self, df: pd.DataFrame, warnings: List[str]) -> pd.DataFrame:
        """입력 데이터 검증"""
        # 타입 강제
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = df[col].astype(np.float64)

        # 인덱스 정렬
        if not df.index.is_monotonic_increasing:
            warnings.append("Index not monotonic, sorting")
            df = df.sort_index()

        # 중복 제거
        if df.index.has_duplicates:
            warnings.append("Duplicate index found, keeping last")
            df = df[~df.index.duplicated(keep='last')]

        # 음수 값 체크
        if 'volume' in df.columns and (df['volume'] < 0).any():
            warnings.append("Negative volume found, setting to 0")
            df.loc[df['volume'] < 0, 'volume'] = 0

        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns and (df[col] <= 0).any():
                warnings.append(f"Non-positive {col} found")

        return df

    def _calculate_builtin(self, df: pd.DataFrame, name: str, options: ExecOptions) -> Dict[str, pd.Series]:
        """내장 지표 계산"""
        return self.registry.execute(name, df, options)

    def _calculate_custom_formula(self, df: pd.DataFrame, config: Dict, options: ExecOptions) -> Dict[str, pd.Series]:
        """커스텀 수식 계산"""
        formula = config.get('formula', '')

        # AST 검증
        if not self.sandbox.validate_ast(formula):
            raise ValueError("Formula failed security validation")

        # 안전한 네임스페이스
        namespace = self.sandbox.create_safe_namespace()
        namespace['df'] = df.copy()
        namespace['params'] = config.get('params', {})

        try:
            # 수식 실행
            exec(f"result = {formula}", namespace)
            result = namespace.get('result')

            if isinstance(result, pd.Series):
                return {config.get('column_name', 'custom'): result}
            elif isinstance(result, dict):
                return result
            else:
                raise ValueError("Formula must return Series or dict")

        except Exception as e:
            logger.error(f"Failed to execute custom formula: {e}")
            raise

    def _calculate_python_code(self, df: pd.DataFrame, config: Dict, options: ExecOptions) -> Dict[str, pd.Series]:
        """Python 코드 실행"""
        code = config.get('code', '')

        # AST 검증
        if not self.sandbox.validate_ast(code):
            raise ValueError("Code failed security validation")

        # 안전한 네임스페이스
        namespace = self.sandbox.create_safe_namespace()
        namespace['df'] = df.copy()
        namespace['params'] = config.get('params', {})
        namespace['options'] = options

        try:
            # 타임아웃 설정 (추후 구현)
            exec(code, namespace)

            # 함수 호출 또는 result 변수 확인
            if 'calculate' in namespace:
                result = namespace['calculate'](df, **config.get('params', {}))
            else:
                result = namespace.get('result')

            if isinstance(result, pd.Series):
                return {config.get('column_name', 'custom'): result}
            elif isinstance(result, dict):
                return result
            else:
                raise ValueError("Code must return Series or dict")

        except Exception as e:
            logger.error(f"Failed to execute Python code: {e}")
            raise

    def _calculate_from_definition(self, df: pd.DataFrame, definition: Dict, options: ExecOptions) -> Dict[str, pd.Series]:
        """Supabase 정의로부터 계산"""
        calc_type = definition.get('calculation_type')

        if calc_type == 'built-in':
            method = json.loads(definition.get('formula', '{}')).get('method')
            if method in self.registry._indicators:
                return self.registry.execute(method, df, options)
        elif calc_type == 'custom_formula':
            return self._calculate_custom_formula(df, definition, options)
        elif calc_type == 'python_code':
            return self._calculate_python_code(df, definition, options)

        raise ValueError(f"Unknown calculation type: {calc_type}")

    def _get_cache_key(self, name: str, options: ExecOptions) -> str:
        """캐시 키 생성"""
        return f"{name}_{options.period}_{options.realtime}_{options.min_periods}"

    def _calculate_nan_ratio(self, columns: Dict[str, pd.Series]) -> float:
        """NaN 비율 계산"""
        total = 0
        nan_count = 0

        for series in columns.values():
            total += len(series)
            nan_count += series.isna().sum()

        return nan_count / total if total > 0 else 0

    def clear_cache(self):
        """캐시 초기화"""
        self._execution_cache.clear()
        logger.info("Execution cache cleared")


# 사용 예제
if __name__ == "__main__":
    # 샘플 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'high': 102 + np.cumsum(np.random.randn(100) * 0.5),
        'low': 98 + np.cumsum(np.random.randn(100) * 0.5),
        'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)

    # 계산기 생성
    calculator = IndicatorCalculator()

    # RSI 계산
    result = calculator.calculate(df, {
        'name': 'rsi',
        'params': {'period': 14}
    })

    print(f"RSI calculated in {result.execution_time_ms:.2f}ms")
    print(f"NaN ratio: {result.nan_ratio:.2%}")
    print(f"Columns: {list(result.columns.keys())}")

    # MACD 계산
    result = calculator.calculate(df, {
        'name': 'macd'
    })

    print(f"\nMACD calculated in {result.execution_time_ms:.2f}ms")
    print(f"Columns: {list(result.columns.keys())}")