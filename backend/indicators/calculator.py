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
        ast.For, ast.If, ast.While, ast.Break, ast.Continue,
        ast.keyword  # 키워드 인자 허용 추가
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
        """AST 검증 - 위험한 코드만 차단 (보안과 유연성의 균형)"""
        print(f"[AST] DEBUG: Starting AST validation, code length={len(code)}")
        try:
            tree = ast.parse(code)
            print(f"[AST] DEBUG: AST parse successful")

            for node in ast.walk(tree):
                # 위험한 함수 호출만 차단
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        # eval, exec, compile, __import__, open 등 차단
                        if node.func.id in ['eval', 'exec', 'compile', '__import__', 'open', 'file']:
                            msg = f"Blocked dangerous function: {node.func.id}"
                            print(f"[AST] ERROR: {msg}")
                            logger.warning(msg)
                            return False
                    # 위험한 속성 접근 차단
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['__globals__', '__code__', '__class__', '__bases__', '__subclasses__']:
                            msg = f"Blocked dangerous attribute: {node.func.attr}"
                            print(f"[AST] ERROR: {msg}")
                            logger.warning(msg)
                            return False

            print(f"[AST] DEBUG: AST validation passed - all checks OK")
            return True
        except SyntaxError as e:
            msg = f"Syntax error in code: {e}"
            print(f"[AST] ERROR: {msg}")
            logger.error(msg)
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
            'str': str,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'bool': bool,
            'isinstance': isinstance,  # isinstance 함수 추가 (EMA 등에서 사용)
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
        # DB 전용 모드 확인 - 기본값을 True로 설정 (운영 안전)
        env_value = os.getenv('ENFORCE_DB_INDICATORS', 'true').lower()
        self.enforce_db_only = env_value in ('true', '1', 'yes')

        # 모드 로깅 (운영 상태 명확히 표시)
        if self.enforce_db_only:
            logger.warning("=" * 60)
            logger.warning("INDICATOR CALCULATOR: DB-ONLY MODE ACTIVE")
            logger.warning("Only Supabase-defined indicators will be used")
            logger.warning("Built-in and custom formulas are DISABLED")
            logger.warning("=" * 60)
            self.registry = None
        else:
            logger.info("=" * 60)
            logger.info("INDICATOR CALCULATOR: DEVELOPMENT MODE")
            logger.info("Built-in indicators and custom formulas are ENABLED")
            logger.info("WARNING: This mode should NOT be used in production")
            logger.info("=" * 60)
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

            if not url or not key:
                # DB 전용 모드에서는 Supabase 필수
                if self.enforce_db_only:
                    raise RuntimeError(
                        "FATAL: DB-only mode requires Supabase connection.\n"
                        "Please set SUPABASE_URL and SUPABASE_KEY environment variables.\n"
                        "Or set ENFORCE_DB_INDICATORS=false for development mode."
                    )
                else:
                    self.supabase = None
                    logger.warning("No Supabase connection - using development mode")
            else:
                self.supabase = create_client(url, key)
                logger.info("Supabase connected successfully")
        except RuntimeError:
            raise  # Fail-fast 에러는 그대로 전파
        except Exception as e:
            if self.enforce_db_only:
                raise RuntimeError(f"FATAL: Failed to connect to Supabase in DB-only mode: {e}")
            else:
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

    def calculate(self, df: pd.DataFrame, config: Dict[str, Any], options: Optional[ExecOptions] = None, stock_code: Optional[str] = None) -> IndicatorResult:
        """지표 계산 - 메인 엔트리포인트

        Args:
            df: 가격 데이터
            config: 지표 설정
            options: 실행 옵션
            stock_code: 종목 코드 (캐시 키 구분용)
        """
        start_time = time.time()
        warnings = []

        print(f"[Calculator] DEBUG: calculate() called with config={config}, stock_code={stock_code}")
        print(f"[Calculator] DEBUG: config keys={list(config.keys())}")
        if 'params' in config:
            print(f"[Calculator] DEBUG: config['params']={config['params']}")

        # 기본 옵션
        if options is None:
            period_from_config = config.get('params', {}).get('period', 20)
            print(f"[Calculator] DEBUG: Creating ExecOptions with period={period_from_config} from config params={config.get('params', {})}")
            options = ExecOptions(
                period=period_from_config,
                realtime=config.get('realtime', False)
            )

        # 입력 검증
        df = self._validate_input(df, warnings)

        indicator_name = config.get('name')
        calculation_type = config.get('calculation_type', 'builtin')

        try:
            # 캐시 확인 - 종목코드 및 params 포함
            cache_key = self._get_cache_key(indicator_name, options, stock_code, df.index, config.get('params', {}))
            if cache_key in self._execution_cache:
                cached_result = self._execution_cache[cache_key]
                logger.info(f"Using cached result for {indicator_name} ({stock_code})")
                return cached_result

            # 계산 타입별 처리 (Supabase 우선)

            # 1. Supabase에서 먼저 확인
            indicator_def = self.indicators_cache.get(indicator_name)
            if indicator_def:
                logger.info(f"Using Supabase definition for {indicator_name}")
                result_columns = self._calculate_from_definition(df, indicator_def, options, config.get('params', {}))

            # DB 전용 모드에서는 Supabase에 없으면 에러
            elif self.enforce_db_only:
                raise ValueError(
                    f"Indicator '{indicator_name}' not found in Supabase. "
                    f"ENFORCE_DB_INDICATORS is enabled - only database-defined indicators are allowed."
                )

            # 2. base_indicator가 지정된 경우 내장 지표 사용 (개발 모드에서만)
            elif config.get('base_indicator') and self.registry:
                base_indicator = config.get('base_indicator')
                logger.info(f"Using base indicator {base_indicator} for {indicator_name}")
                result_columns = self._calculate_builtin(df, indicator_name, options)

            # 3. 내장 지표 확인 (개발 모드에서만)
            elif self.registry and (indicator_name in self.registry._indicators or indicator_name.split('_')[0] in self.registry._indicators):
                logger.info(f"Using built-in indicator for {indicator_name}")
                result_columns = self._calculate_builtin(df, indicator_name, options)

            # 4. config에 calculation_type이 명시된 경우 (개발 모드에서만)
            elif not self.enforce_db_only and calculation_type == 'custom_formula':
                logger.warning(f"Using custom_formula for {indicator_name} - not recommended in production")
                result_columns = self._calculate_custom_formula(df, config, options)
            elif not self.enforce_db_only and calculation_type == 'python_code':
                logger.warning(f"Using python_code for {indicator_name} - not recommended in production")
                result_columns = self._calculate_python_code(df, config, options)
            else:
                if self.enforce_db_only:
                    raise ValueError(f"Indicator '{indicator_name}' must be defined in Supabase database")
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
        # name이 sma_5, sma_20 같은 형식일 수 있으므로 기본 지표명 추출
        base_name = name.split('_')[0] if '_' in name else name

        # 기본 지표가 레지스트리에 있는지 확인
        if base_name in self.registry._indicators:
            result = self.registry.execute(base_name, df, options)

            # 결과 컬럼명을 요청된 이름으로 변경
            if name != base_name:
                renamed_result = {}
                for col_name, col_data in result.items():
                    # sma -> sma_5 형식으로 변경
                    new_col_name = name if col_name == base_name else f"{name}_{col_name.split('_', 1)[-1]}" if '_' in col_name else name
                    renamed_result[new_col_name] = col_data
                return renamed_result

            return result
        else:
            raise ValueError(f"Unknown builtin indicator: {base_name}")

    def _calculate_custom_formula(self, df: pd.DataFrame, config: Dict, options: ExecOptions) -> Dict[str, pd.Series]:
        """커스텀 수식 계산"""
        # formula가 문자열이거나 dict일 수 있음
        formula_data = config.get('formula', '')

        # JSON 문자열인 경우 파싱
        if isinstance(formula_data, str):
            try:
                formula_data = json.loads(formula_data) if formula_data.startswith('{') else {'expression': formula_data}
            except:
                formula_data = {'expression': formula_data}

        # expression 추출
        if isinstance(formula_data, dict):
            formula = formula_data.get('expression', '')
            output_column = formula_data.get('output_column', config.get('name', 'custom'))
        else:
            formula = str(formula_data)
            output_column = config.get('name', 'custom')

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
                return {output_column: result}
            elif isinstance(result, dict):
                return result
            else:
                raise ValueError("Formula must return Series or dict")

        except Exception as e:
            logger.error(f"Failed to execute custom formula: {e}")
            raise

    def _calculate_python_code(self, df: pd.DataFrame, config: Dict, options: ExecOptions, custom_params: Dict = None) -> Dict[str, pd.Series]:
        """Python 코드 실행"""
        print(f"[Calculator] DEBUG: _calculate_python_code called")
        print(f"[Calculator] DEBUG: config keys={list(config.keys())}")
        print(f"[Calculator] DEBUG: custom_params={custom_params}")

        # config가 indicator definition인 경우 formula에서 code 추출
        if 'formula' in config and isinstance(config['formula'], dict):
            code = config['formula'].get('code', '')
            print(f"[Calculator] DEBUG: Code from formula, len={len(code) if code else 0}")
        else:
            code = config.get('code', '')
            print(f"[Calculator] DEBUG: Code from config, len={len(code) if code else 0}")

        print(f"[Calculator] DEBUG: About to validate AST")
        print(f"[Calculator] DEBUG: Code preview:\n{code[:500]}")
        # AST 검증
        ast_valid = self.sandbox.validate_ast(code)
        print(f"[Calculator] DEBUG: AST validation result={ast_valid}")
        if not ast_valid:
            print(f"[Calculator] ERROR: AST validation failed!")
            print(f"[Calculator] ERROR: Full code:\n{code}")
            raise ValueError("Code failed security validation")
        print(f"[Calculator] DEBUG: AST validation passed")

        # 안전한 네임스페이스
        namespace = self.sandbox.create_safe_namespace()
        namespace['df'] = df.copy()
        namespace['params'] = {
            'period': options.period,
            'realtime': options.realtime,
            'source': 'close',
            'min_periods': options.min_periods
        }

        # default_params 먼저 추가 (낮은 우선순위)
        if config.get('default_params'):
            try:
                default_params = json.loads(config['default_params']) if isinstance(config['default_params'], str) else config['default_params']
                if isinstance(default_params, dict):
                    # custom_params가 없는 키만 업데이트
                    for key, value in default_params.items():
                        if key not in namespace['params']:
                            namespace['params'][key] = value
            except:
                pass

        # custom_params 우선 적용 (최고 우선순위!)
        if custom_params:
            namespace['params'].update(custom_params)
            print(f"[Calculator] DEBUG: Applied custom_params to namespace: {custom_params}")

        namespace['options'] = options

        print(f"[Calculator] DEBUG: About to execute code")
        print(f"[Calculator] DEBUG: params={namespace['params']}")

        try:
            # 타임아웃 설정 (추후 구현)
            logger.info(f"[DEBUG] Executing code with params: {namespace['params']}")
            logger.info(f"[DEBUG] Code to execute:\n{code[:200]}...")
            print(f"[Calculator] DEBUG: Calling exec()")
            exec(code, namespace)
            print(f"[Calculator] DEBUG: exec() completed")

            # 함수 호출 또는 result 변수 확인
            if 'calculate' in namespace:
                result = namespace['calculate'](df, **config.get('params', {}))
            else:
                result = namespace.get('result')

            logger.info(f"[DEBUG] Execution result type: {type(result)}")
            if isinstance(result, dict):
                logger.info(f"[DEBUG] Result dict keys: {list(result.keys())}")
                for key, val in result.items():
                    logger.info(f"[DEBUG]   {key}: type={type(val)}, len={len(val) if hasattr(val, '__len__') else 'N/A'}")
            elif result is None:
                logger.error(f"[DEBUG] Result is None! Namespace keys: {list(namespace.keys())}")

            if isinstance(result, pd.Series):
                return {config.get('column_name', 'custom'): result}
            elif isinstance(result, dict):
                return result
            else:
                raise ValueError("Code must return Series or dict")

        except Exception as e:
            logger.error(f"Failed to execute Python code: {e}")
            raise

    def _execute_supabase_code(self, df: pd.DataFrame, code: str, definition: Dict, options: ExecOptions, custom_params: Dict = None) -> Dict[str, pd.Series]:
        """Supabase 형식의 코드 실행"""
        # 안전한 네임스페이스 생성
        namespace = self.sandbox.create_safe_namespace()
        namespace['df'] = df.copy()
        namespace['str'] = str  # str 함수 추가
        namespace['int'] = int  # int 함수 추가
        namespace['params'] = {
            'period': options.period,
            'realtime': options.realtime,
            'source': 'close',
            'min_periods': options.min_periods
        }

        # custom_params 우선 적용 (중요!)
        if custom_params:
            namespace['params'].update(custom_params)
            print(f"[Calculator] DEBUG: Applied custom_params to namespace: {custom_params}")

        # default_params 추가
        if definition.get('default_params'):
            try:
                default_params = json.loads(definition['default_params']) if isinstance(definition['default_params'], str) else definition['default_params']
                if isinstance(default_params, dict):
                    # custom_params가 없는 키만 업데이트
                    for key, value in default_params.items():
                        if key not in namespace['params']:
                            namespace['params'][key] = value
            except:
                pass

        try:
            # 디버그: namespace params 확인
            logger.info(f"[DEBUG] Executing code with params: {namespace['params']}")

            # 코드 실행
            exec(code, namespace)

            # result 변수 확인
            result = namespace.get('result')
            if result:
                if isinstance(result, pd.Series):
                    return {definition.get('name', 'custom'): result}
                elif isinstance(result, dict):
                    return result
                else:
                    raise ValueError("Code must return Series or dict")
            else:
                raise ValueError("Code did not set 'result' variable")

        except Exception as e:
            logger.error(f"Failed to execute Supabase code: {e}")
            raise

    def _calculate_from_definition(self, df: pd.DataFrame, definition: Dict, options: ExecOptions, custom_params: Dict = None) -> Dict[str, pd.Series]:
        """Supabase 정의로부터 계산"""
        calc_type = definition.get('calculation_type')
        print(f"[Calculator] DEBUG: _calculate_from_definition called")
        print(f"[Calculator] DEBUG: calc_type={calc_type}")
        print(f"[Calculator] DEBUG: definition name={definition.get('name')}")
        print(f"[Calculator] DEBUG: custom_params={custom_params}")
        print(f"[Calculator] DEBUG: options.period={options.period}, options.min_periods={options.min_periods}")

        # default_params로 options를 덮어쓰지 않음
        # custom_params가 우선순위를 가져야 하며, namespace 생성 시 default_params는 _execute_supabase_code에서 처리됨
        # 이 로직은 custom_params보다 먼저 실행되어 options.period를 덮어쓰는 버그를 일으킴

        if calc_type == 'built-in' or calc_type == 'builtin':
            print(f"[Calculator] DEBUG: calc_type is built-in")
            # built-in 지표의 경우 formula 필드에 code가 있음
            formula_str = definition.get('formula', '{}')
            print(f"[Calculator] DEBUG: formula_str type={type(formula_str)}, len={len(str(formula_str)) if formula_str else 0}")
            try:
                formula = json.loads(formula_str) if isinstance(formula_str, str) else formula_str
            except:
                formula = {'code': formula_str}

            print(f"[Calculator] DEBUG: formula keys={list(formula.keys()) if isinstance(formula, dict) else 'not a dict'}")

            if 'code' in formula:
                print(f"[Calculator] DEBUG: Using Supabase code execution")
                # 기존 Supabase 형식 - Python 코드 실행
                code = formula['code']
                return self._execute_supabase_code(df, code, definition, options, custom_params)
            else:
                print(f"[Calculator] DEBUG: Using registry execution")
                # 새 형식 - registry 사용 (DB 전용 모드에서는 불가)
                if self.registry is None:
                    raise ValueError(
                        f"Indicator '{definition.get('name')}' requires 'code' in formula. "
                        f"Registry-based execution is not available in DB-only mode."
                    )
                method = formula.get('method', definition.get('name', '').split('_')[0])
                print(f"[Calculator] DEBUG: method={method}, in registry={method in self.registry._indicators}")
                if method in self.registry._indicators:
                    return self.registry.execute(method, df, options)
                else:
                    raise ValueError(f"Method '{method}' not found in registry")

        elif calc_type == 'custom_formula':
            print(f"[Calculator] DEBUG: Using custom_formula")
            return self._calculate_custom_formula(df, definition, options)
        elif calc_type == 'python_code':
            print(f"[Calculator] DEBUG: Using python_code")
            return self._calculate_python_code(df, definition, options, custom_params)
        else:
            # 기본적으로 custom_formula로 처리
            print(f"[Calculator] DEBUG: Unknown calc_type, using custom_formula as fallback")
            logger.warning(f"Unknown calculation type '{calc_type}', treating as custom_formula")
            return self._calculate_custom_formula(df, definition, options)

    def _get_cache_key(self, name: str, options: ExecOptions, stock_code: Optional[str] = None, df_index: Optional[pd.Index] = None, params: Optional[Dict] = None) -> str:
        """캐시 키 생성 - 종목, 데이터 범위 및 파라미터 포함"""
        # 기본 키
        key_parts = [name, str(options.period), str(options.realtime), str(options.min_periods)]

        # params 추가 (중요: 동일 지표의 다른 파라미터 구분)
        if params:
            import json
            params_str = json.dumps(params, sort_keys=True)
            key_parts.append(params_str)

        # 종목 코드 추가
        if stock_code:
            key_parts.append(stock_code)

        # 데이터 범위 해시 추가 (첫/마지막 인덱스)
        if df_index is not None and len(df_index) > 0:
            index_hash = f"{df_index[0]}_{df_index[-1]}_{len(df_index)}"
            key_parts.append(str(hash(index_hash)))

        return "_".join(key_parts)

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