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
        formula = indicator_def.get('formula', {})
        if isinstance(formula, str):
            formula = json.loads(formula)

        code = formula.get('code')
        default_params = indicator_def.get('default_params', {})
        if isinstance(default_params, str):
            default_params = json.loads(default_params)
        final_params = {**default_params, **params}

        try:
            # Python 코드 실행
            exec_globals = {
                'pd': pd,
                'np': np,
                'df': df,
                'params': final_params
            }
            exec(code, exec_globals)
            df = exec_globals['df']
        except Exception as e:
            print(f"[ERROR] Failed to execute Python code for {column_name}: {e}")

        return df

    def _calculate_legacy(self, df: pd.DataFrame, name: str, params: Dict, column_name: str) -> pd.DataFrame:
        """레거시 하드코딩된 지표 계산 (Fallback)"""
        if name == 'ma':
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
        elif name == 'bollinger':
            period = params.get('period', 20)
            std_dev = params.get('std', 2)
            self._calc_bollinger(df, column_name, period, std_dev)
        elif name == 'stochastic':
            k_period = params.get('k_period', 14)
            d_period = params.get('d_period', 3)
            self._calc_stochastic(df, column_name, k_period, d_period)
        elif name == 'volume_ma':
            period = params.get('period', 20)
            df[column_name] = df['volume'].rolling(window=period).mean()
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