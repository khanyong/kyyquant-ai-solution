"""
기술적 지표 계산기 v2
Supabase에서 지표 정의를 로드하여 동적으로 계산
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import os
from supabase import create_client
import json

class IndicatorCalculator:
    """지표 계산기 - Supabase 연동"""

    def __init__(self):
        self._init_database()
        self.indicators_cache = {}
        self._load_indicators()

    def _init_database(self):
        """데이터베이스 연결 초기화"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

            if url and key:
                self.supabase = create_client(url, key)
                print("[OK] IndicatorCalculator: Supabase connected")
            else:
                self.supabase = None
                print("[WARNING] IndicatorCalculator: No database connection")
        except Exception as e:
            print(f"[ERROR] IndicatorCalculator: Database connection failed: {e}")
            self.supabase = None

    def _load_indicators(self):
        """Supabase에서 모든 활성 지표 로드"""
        if not self.supabase:
            print("[INFO] Using built-in indicators only")
            return

        try:
            response = self.supabase.table('indicators').select('*').eq('is_active', True).execute()
            if response.data:
                for indicator in response.data:
                    self.indicators_cache[indicator['name']] = indicator
                print(f"[OK] Loaded {len(self.indicators_cache)} indicators from database")
            else:
                print("[WARNING] No indicators found in database")
        except Exception as e:
            print(f"[ERROR] Failed to load indicators: {e}")

    async def calculate(self, df: pd.DataFrame, indicator_config: Dict[str, Any]) -> pd.DataFrame:
        """지표 계산 - Supabase 정의 또는 내장 함수 사용"""
        name = indicator_config.get('name')
        params = indicator_config.get('params', {})
        column_name = indicator_config.get('column_name', name)

        # Supabase에서 지표 정의 가져오기
        indicator_def = self.indicators_cache.get(name)

        if indicator_def:
            calculation_type = indicator_def.get('calculation_type')

            if calculation_type == 'built-in':
                # 내장 함수 사용
                return self._calculate_builtin(df, indicator_def, params, column_name)
            elif calculation_type == 'custom_formula':
                # 커스텀 수식 사용
                return self._calculate_custom_formula(df, indicator_def, params, column_name)
            elif calculation_type == 'python_code':
                # Python 코드 실행
                return self._calculate_python_code(df, indicator_def, params, column_name)

        # Fallback: 기존 하드코딩된 지표들
        return self._calculate_legacy(df, name, params, column_name)

    def _calculate_builtin(self, df: pd.DataFrame, indicator_def: Dict, params: Dict, column_name: str) -> pd.DataFrame:
        """내장 함수로 지표 계산"""
        formula = indicator_def.get('formula', {})
        if isinstance(formula, str):
            formula = json.loads(formula)

        method = formula.get('method')
        source = formula.get('source', 'close')

        # 파라미터 병합 (사용자 파라미터가 우선)
        default_params = indicator_def.get('default_params', {})
        if isinstance(default_params, str):
            default_params = json.loads(default_params)
        final_params = {**default_params, **params}

        if method == 'rolling_mean':
            period = final_params.get('period', 20)
            df[column_name] = df[source].rolling(window=period).mean()

        elif method == 'ewm_mean':
            period = final_params.get('period', 20)
            df[column_name] = df[source].ewm(span=period, adjust=False).mean()

        elif method == 'rsi':
            period = final_params.get('period', 14)
            df[column_name] = self._calc_rsi(df[source], period)

        elif method == 'macd':
            fast = final_params.get('fast', 12)
            slow = final_params.get('slow', 26)
            signal = final_params.get('signal', 9)
            self._calc_macd(df, column_name, fast, slow, signal)

        elif method == 'bollinger':
            period = final_params.get('period', 20)
            std_dev = final_params.get('std', 2)
            self._calc_bollinger(df, column_name, period, std_dev)

        elif method == 'stochastic':
            k_period = final_params.get('k_period', 14)
            d_period = final_params.get('d_period', 3)
            self._calc_stochastic(df, column_name, k_period, d_period)

        elif method == 'price' or method == 'close':
            # 가격/종가는 그대로 사용
            df[column_name] = df[source]

        elif method == 'volume':
            # 거래량은 그대로 사용
            df[column_name] = df['volume']

        elif method == 'cross_above':
            # 교차 상승 체크 (이전 구현 필요)
            pass

        elif method == 'cross_below':
            # 교차 하락 체크 (이전 구현 필요)
            pass

        return df

    def _calculate_custom_formula(self, df: pd.DataFrame, indicator_def: Dict, params: Dict, column_name: str) -> pd.DataFrame:
        """커스텀 수식으로 지표 계산"""
        formula = indicator_def.get('formula', {})
        if isinstance(formula, str):
            formula = json.loads(formula)

        formula_str = formula.get('formula')
        default_params = indicator_def.get('default_params', {})
        if isinstance(default_params, str):
            default_params = json.loads(default_params)
        final_params = {**default_params, **params}

        try:
            # 파라미터를 로컬 변수로 설정
            for key, value in final_params.items():
                locals()[key] = value

            # 수식 실행 (pandas eval 사용)
            df[column_name] = eval(formula_str)
        except Exception as e:
            print(f"[ERROR] Failed to calculate custom formula for {column_name}: {e}")

        return df

    def _calculate_python_code(self, df: pd.DataFrame, indicator_def: Dict, params: Dict, column_name: str) -> pd.DataFrame:
        """Python 코드로 지표 계산"""
        formula_code = indicator_def.get('formula', '')

        # formula가 JSON 문자열인 경우 처리
        if isinstance(formula_code, str) and formula_code.startswith('{'):
            try:
                formula_dict = json.loads(formula_code)
                formula_code = formula_dict.get('code', '')
            except:
                pass  # 이미 Python 코드 문자열
        elif isinstance(formula_code, dict):
            # 이미 파싱된 dict인 경우
            formula_code = formula_code.get('code', '')

        default_params = indicator_def.get('default_params', {})
        if isinstance(default_params, str):
            default_params = json.loads(default_params)
        final_params = {**default_params, **params}

        try:
            # 코드 실행을 위한 네임스페이스 준비
            exec_namespace = {
                'pd': pd,
                'np': np,
                'df': df.copy(),  # 안전을 위해 복사본 사용
                'params': final_params  # params를 네임스페이스에 추가
            }

            # 함수 정의 포함 여부 확인
            if 'def calculate' in formula_code:
                # 함수 정의가 있는 경우
                exec(formula_code, exec_namespace)
                result = exec_namespace['calculate'](df, **final_params)
            else:
                # 단순 표현식인 경우
                exec(f"result = {formula_code}", exec_namespace)
                result = exec_namespace['result']

            # 결과 처리
            if isinstance(result, dict):
                # 여러 컬럼 반환 (예: MACD, 볼린저밴드)
                for key, value in result.items():
                    df[key] = value
                print(f"[Calculator] Python code executed: {column_name} -> {list(result.keys())}")
            else:
                # 단일 컬럼 반환
                df[column_name] = result
                print(f"[Calculator] Python code executed: {column_name}")

        except Exception as e:
            print(f"[ERROR] Failed to execute Python code for {column_name}: {e}")
            import traceback
            traceback.print_exc()

        return df

    def _calculate_legacy(self, df: pd.DataFrame, name: str, params: Dict, column_name: str) -> pd.DataFrame:
        """레거시 하드코딩된 지표 계산 (Fallback)"""
        if name == 'ma' or name == 'sma':
            period = params.get('period', 20)
            df[column_name] = df['close'].rolling(window=period).mean()
        elif name == 'ema':
            period = params.get('period', 20)
            df[column_name] = df['close'].ewm(span=period, adjust=False).mean()
        elif name == 'rsi':
            period = params.get('period', 14)
            df[column_name] = self._calc_rsi(df['close'], period)
        elif name == 'macd':
            fast = params.get('fast', 12)
            slow = params.get('slow', 26)
            signal = params.get('signal', 9)
            self._calc_macd(df, column_name, fast, slow, signal)
        elif name == 'bollinger' or name == 'bb':
            period = params.get('period', 20)
            std_dev = params.get('std', 2)
            self._calc_bollinger(df, column_name, period, std_dev)
        elif name == 'stochastic':
            k_period = params.get('k', 14) or params.get('k_period', 14)
            d_period = params.get('d', 3) or params.get('d_period', 3)
            self._calc_stochastic(df, column_name, k_period, d_period)
        elif name == 'ichimoku':
            self._calc_ichimoku(df, column_name, params)
        elif name == 'obv':
            df[column_name] = self._calc_obv(df)
        elif name == 'vwap':
            df[column_name] = self._calc_vwap(df)
        elif name == 'atr':
            period = params.get('period', 14)
            df[column_name] = self._calc_atr(df, period)
        elif name == 'cci':
            period = params.get('period', 20)
            df[column_name] = self._calc_cci(df, period)
        elif name == 'williams':
            period = params.get('period', 14)
            df[column_name] = self._calc_williams(df, period)
        elif name == 'adx':
            period = params.get('period', 14)
            df[column_name] = self._calc_adx(df, period)
        elif name == 'dmi':
            period = params.get('period', 14)
            self._calc_dmi(df, column_name, period)
        elif name == 'parabolic':
            acc = params.get('acc', 0.02)
            max_acc = params.get('max', 0.2)
            df[column_name] = self._calc_parabolic_sar(df, acc, max_acc)
        elif name == 'volume_ma':
            period = params.get('period', 20)
            df[column_name] = df['volume'].rolling(window=period).mean()
        elif name == 'volume':
            df[column_name] = df['volume']
        elif name == 'price' or name == 'close':
            df[column_name] = df['close']
        else:
            print(f"[WARNING] Unknown indicator: {name}")

        return df

    # 헬퍼 함수들
    def _calc_rsi(self, prices: pd.Series, period: int) -> pd.Series:
        """RSI 계산"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calc_macd(self, df: pd.DataFrame, column_name: str, fast: int, slow: int, signal: int):
        """MACD 계산"""
        exp1 = df['close'].ewm(span=fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=slow, adjust=False).mean()
        df[f'{column_name}_line'] = exp1 - exp2
        df[f'{column_name}_signal'] = df[f'{column_name}_line'].ewm(span=signal, adjust=False).mean()
        df[f'{column_name}_hist'] = df[f'{column_name}_line'] - df[f'{column_name}_signal']

    def _calc_bollinger(self, df: pd.DataFrame, column_name: str, period: int, std_dev: int):
        """볼린저 밴드 계산"""
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        df[f'{column_name}_upper'] = sma + (std * std_dev)
        df[f'{column_name}_middle'] = sma
        df[f'{column_name}_lower'] = sma - (std * std_dev)

    def _calc_stochastic(self, df: pd.DataFrame, column_name: str, k_period: int, d_period: int):
        """스토캐스틱 계산"""
        low_min = df['low'].rolling(window=k_period).min()
        high_max = df['high'].rolling(window=k_period).max()
        df[f'{column_name}_k'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
        df[f'{column_name}_d'] = df[f'{column_name}_k'].rolling(window=d_period).mean()

    def _calc_ichimoku(self, df: pd.DataFrame, column_name: str, params: Dict):
        """일목균형표 계산"""
        tenkan = params.get('tenkan', 9)
        kijun = params.get('kijun', 26)
        senkou = params.get('senkou', 52)
        chikou = params.get('chikou', 26)

        # 전환선 (Tenkan-sen)
        tenkan_high = df['high'].rolling(window=tenkan).max()
        tenkan_low = df['low'].rolling(window=tenkan).min()
        df[f'{column_name}_tenkan'] = (tenkan_high + tenkan_low) / 2

        # 기준선 (Kijun-sen)
        kijun_high = df['high'].rolling(window=kijun).max()
        kijun_low = df['low'].rolling(window=kijun).min()
        df[f'{column_name}_kijun'] = (kijun_high + kijun_low) / 2

        # 선행스팬 A (Senkou Span A)
        df[f'{column_name}_senkou_a'] = ((df[f'{column_name}_tenkan'] + df[f'{column_name}_kijun']) / 2).shift(kijun)

        # 선행스팬 B (Senkou Span B)
        senkou_high = df['high'].rolling(window=senkou).max()
        senkou_low = df['low'].rolling(window=senkou).min()
        df[f'{column_name}_senkou_b'] = ((senkou_high + senkou_low) / 2).shift(kijun)

        # 후행스팬 (Chikou Span)
        df[f'{column_name}_chikou'] = df['close'].shift(-chikou)

    def _calc_obv(self, df: pd.DataFrame) -> pd.Series:
        """OBV (On Balance Volume) 계산"""
        obv = [0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + df['volume'].iloc[i])
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - df['volume'].iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=df.index)

    def _calc_vwap(self, df: pd.DataFrame) -> pd.Series:
        """VWAP (Volume Weighted Average Price) 계산"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        cumulative_volume = df['volume'].cumsum()
        cumulative_pv = (typical_price * df['volume']).cumsum()
        return cumulative_pv / cumulative_volume

    def _calc_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """ATR (Average True Range) 계산"""
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return true_range.rolling(window=period).mean()

    def _calc_cci(self, df: pd.DataFrame, period: int) -> pd.Series:
        """CCI (Commodity Channel Index) 계산"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
        return (typical_price - sma) / (0.015 * mad)

    def _calc_williams(self, df: pd.DataFrame, period: int) -> pd.Series:
        """Williams %R 계산"""
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        return -100 * ((highest_high - df['close']) / (highest_high - lowest_low))

    def _calc_adx(self, df: pd.DataFrame, period: int) -> pd.Series:
        """ADX (Average Directional Index) 계산"""
        # +DM, -DM 계산
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # TR (True Range) 계산
        tr = self._calc_atr(df, 1)

        # +DI, -DI 계산
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())

        # DX 계산
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

        # ADX 계산
        return dx.rolling(window=period).mean()

    def _calc_dmi(self, df: pd.DataFrame, column_name: str, period: int):
        """DMI (Directional Movement Index) 계산"""
        # +DM, -DM 계산
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0

        # TR 계산
        tr = self._calc_atr(df, 1)

        # +DI, -DI 계산
        df[f'{column_name}_plus_di'] = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        df[f'{column_name}_minus_di'] = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())

    def _calc_parabolic_sar(self, df: pd.DataFrame, acc: float, max_acc: float) -> pd.Series:
        """Parabolic SAR 계산"""
        sar = df['close'].copy()
        ep = df['high'].copy() if df['close'].iloc[1] > df['close'].iloc[0] else df['low'].copy()
        af = acc
        uptrend = df['close'].iloc[1] > df['close'].iloc[0]

        for i in range(2, len(df)):
            if uptrend:
                sar.iloc[i] = sar.iloc[i-1] + af * (ep.iloc[i-1] - sar.iloc[i-1])
                if df['low'].iloc[i] < sar.iloc[i]:
                    uptrend = False
                    sar.iloc[i] = ep.iloc[i-1]
                    ep.iloc[i] = df['low'].iloc[i]
                    af = acc
                else:
                    if df['high'].iloc[i] > ep.iloc[i-1]:
                        ep.iloc[i] = df['high'].iloc[i]
                        af = min(af + acc, max_acc)
                    else:
                        ep.iloc[i] = ep.iloc[i-1]
            else:
                sar.iloc[i] = sar.iloc[i-1] + af * (ep.iloc[i-1] - sar.iloc[i-1])
                if df['high'].iloc[i] > sar.iloc[i]:
                    uptrend = True
                    sar.iloc[i] = ep.iloc[i-1]
                    ep.iloc[i] = df['high'].iloc[i]
                    af = acc
                else:
                    if df['low'].iloc[i] < ep.iloc[i-1]:
                        ep.iloc[i] = df['low'].iloc[i]
                        af = min(af + acc, max_acc)
                    else:
                        ep.iloc[i] = ep.iloc[i-1]

        return sar