"""
Supabase 전용 지표 계산기 - 내장 지표 없음
모든 지표는 Supabase에서 관리
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import os
import json
import ast
import traceback
import time
import logging
from supabase import create_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ExecOptions:
    """지표 실행 옵션"""
    period: int = 20
    realtime: bool = False
    min_periods: Optional[int] = None

    def __post_init__(self):
        if self.min_periods is None:
            self.min_periods = self.period

class SupabaseIndicatorCalculator:
    """Supabase 전용 지표 계산기"""

    def __init__(self):
        self.supabase = None
        self.indicators_cache = {}
        self._init_database()
        self._load_indicators()
        self._execution_cache = {}

    def _init_database(self):
        """Supabase 연결"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

            if url and key:
                self.supabase = create_client(url, key)
                logger.info("Supabase connected successfully")
            else:
                raise ValueError("SUPABASE_URL and SUPABASE_KEY are required")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def _load_indicators(self):
        """Supabase에서 모든 지표 로드"""
        if not self.supabase:
            raise ValueError("No Supabase connection")

        try:
            response = self.supabase.table('indicators').select('*').eq('is_active', True).execute()
            if response.data:
                for indicator in response.data:
                    self.indicators_cache[indicator['name']] = indicator
                logger.info(f"Loaded {len(self.indicators_cache)} indicators from Supabase")

                # 로드된 지표 목록 출력
                logger.info(f"Available indicators: {list(self.indicators_cache.keys())}")
            else:
                logger.warning("No active indicators found in Supabase")
        except Exception as e:
            logger.error(f"Failed to load indicators: {e}")
            raise

    def refresh_indicators(self):
        """지표 캐시 새로고침 (실시간 업데이트용)"""
        self.indicators_cache.clear()
        self._execution_cache.clear()
        self._load_indicators()
        logger.info("Indicators refreshed from Supabase")

    async def calculate(self, df: pd.DataFrame, indicator_config: Dict[str, Any]) -> pd.DataFrame:
        """지표 계산 - Supabase 정의만 사용"""
        name = indicator_config.get('name')
        params = indicator_config.get('params', {})
        column_name = indicator_config.get('column_name', name)

        # Supabase에서 지표 정의 가져오기
        indicator_def = self.indicators_cache.get(name)

        if not indicator_def:
            # 지표가 캐시에 없으면 다시 로드 시도
            self.refresh_indicators()
            indicator_def = self.indicators_cache.get(name)

            if not indicator_def:
                available = list(self.indicators_cache.keys())
                raise ValueError(f"Indicator '{name}' not found in Supabase. Available: {available}")

        calculation_type = indicator_def.get('calculation_type')
        formula = indicator_def.get('formula')
        output_columns = indicator_def.get('output_columns', [])

        logger.info(f"Calculating {name} using {calculation_type} from Supabase")

        try:
            if calculation_type == 'built-in':
                df = self._calculate_builtin(df, formula, params, column_name, output_columns)
            elif calculation_type == 'python_code':
                df = self._calculate_python_code(df, formula, params, column_name, output_columns)
            elif calculation_type == 'custom_formula':
                df = self._calculate_custom_formula(df, formula, params, column_name, output_columns)
            else:
                raise ValueError(f"Unknown calculation_type: {calculation_type}")

            return df

        except Exception as e:
            logger.error(f"Failed to calculate {name}: {e}")
            traceback.print_exc()
            raise

    def _calculate_builtin(self, df: pd.DataFrame, formula: Any, params: Dict,
                          column_name: str, output_columns: List[str]) -> pd.DataFrame:
        """Supabase built-in 메서드 실행"""
        if isinstance(formula, str):
            formula = json.loads(formula)

        method = formula.get('method', '').lower()
        source = formula.get('source', 'close')
        period = params.get('period', formula.get('period', 20))

        logger.info(f"Built-in method: {method}, period: {period}")

        # 기본 메서드들 (필요시 확장)
        if method in ['sma', 'ma']:
            result = df[source].rolling(window=period).mean()
            df[column_name] = result

        elif method == 'ema':
            result = df[source].ewm(span=period, adjust=False).mean()
            df[column_name] = result

        elif method == 'rsi':
            delta = df[source].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))
            df[column_name] = rsi.clip(0, 100)

        elif method == 'bb':
            middle = df[source].rolling(window=period).mean()
            std = df[source].rolling(window=period).std(ddof=0)
            std_mult = params.get('std', 2)

            if output_columns and len(output_columns) >= 3:
                df[output_columns[0]] = middle + (std * std_mult)
                df[output_columns[1]] = middle
                df[output_columns[2]] = middle - (std * std_mult)
            else:
                df[f'{column_name}_upper'] = middle + (std * std_mult)
                df[f'{column_name}_middle'] = middle
                df[f'{column_name}_lower'] = middle - (std * std_mult)

        elif method == 'volume':
            df[column_name] = df['volume']

        elif method == 'price':
            df[column_name] = df[source]

        else:
            raise ValueError(f"Unknown built-in method: {method}")

        return df

    def _calculate_python_code(self, df: pd.DataFrame, formula: Any, params: Dict,
                               column_name: str, output_columns: List[str]) -> pd.DataFrame:
        """Supabase Python 코드 실행"""
        if isinstance(formula, str) and formula.startswith('{'):
            try:
                formula_dict = json.loads(formula)
                code = formula_dict.get('code', '')
            except:
                code = formula
        elif isinstance(formula, dict):
            code = formula.get('code', '')
        else:
            code = str(formula)

        if not code:
            raise ValueError("No Python code found in formula")

        # 안전한 네임스페이스
        namespace = {
            '__builtins__': {},
            'pd': pd,
            'np': np,
            'df': df.copy(),
            'params': params,
            'output_columns': output_columns,
            'column_name': column_name
        }

        try:
            # 코드 실행
            exec(code, namespace)

            # 결과 처리
            if 'result' in namespace:
                result = namespace['result']
                if isinstance(result, pd.Series):
                    df[column_name] = result
                elif isinstance(result, dict):
                    for key, value in result.items():
                        df[key] = value
                elif isinstance(result, pd.DataFrame):
                    # DataFrame 반환 시 병합
                    for col in result.columns:
                        if col not in df.columns:
                            df[col] = result[col]

            # calculate 함수가 정의된 경우
            elif 'calculate' in namespace:
                result = namespace['calculate'](df, **params)
                if isinstance(result, pd.DataFrame):
                    return result
                elif isinstance(result, dict):
                    for key, value in result.items():
                        df[key] = value

            # df가 직접 수정된 경우
            else:
                modified_df = namespace.get('df')
                if isinstance(modified_df, pd.DataFrame):
                    # 새로 추가된 컬럼만 복사
                    for col in modified_df.columns:
                        if col not in df.columns or not df[col].equals(modified_df[col]):
                            df[col] = modified_df[col]

        except Exception as e:
            logger.error(f"Python code execution failed: {e}")
            logger.error(f"Code: {code[:200]}...")
            raise

        return df

    def _calculate_custom_formula(self, df: pd.DataFrame, formula: Any, params: Dict,
                                  column_name: str, output_columns: List[str]) -> pd.DataFrame:
        """커스텀 수식 실행"""
        if isinstance(formula, dict):
            formula_str = formula.get('formula', '')
        else:
            formula_str = str(formula)

        if not formula_str:
            raise ValueError("No formula found")

        # 파라미터와 데이터프레임 컬럼을 로컬 변수로
        local_vars = params.copy()
        for col in df.columns:
            local_vars[col] = df[col]

        try:
            # 수식 실행
            result = eval(formula_str, {'__builtins__': {}, 'np': np, 'pd': pd}, local_vars)

            if isinstance(result, pd.Series):
                df[column_name] = result
            else:
                df[column_name] = result

        except Exception as e:
            logger.error(f"Custom formula execution failed: {e}")
            logger.error(f"Formula: {formula_str}")
            raise

        return df

    def get_indicator_info(self, name: str) -> Optional[Dict]:
        """특정 지표 정보 반환"""
        return self.indicators_cache.get(name)

    def list_indicators(self) -> List[str]:
        """사용 가능한 모든 지표 목록"""
        return list(self.indicators_cache.keys())

    def validate_indicator(self, name: str) -> bool:
        """지표 존재 여부 확인"""
        return name in self.indicators_cache


# 호환성을 위한 별칭
IndicatorCalculator = SupabaseIndicatorCalculator


if __name__ == "__main__":
    import asyncio

    async def test():
        # 계산기 생성
        calc = SupabaseIndicatorCalculator()

        # 사용 가능한 지표 확인
        print(f"Available indicators: {calc.list_indicators()}")

        # 샘플 데이터
        df = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [101, 102, 103, 104, 105],
            'low': [99, 100, 101, 102, 103],
            'close': [100.5, 101.5, 102.5, 103.5, 104.5],
            'volume': [1000, 1100, 1200, 1300, 1400]
        })

        # RSI 계산 (Supabase에서 정의된 대로)
        result = await calc.calculate(df, {
            'name': 'rsi',
            'params': {'period': 14}
        })

        print(f"Result columns: {result.columns.tolist()}")

    asyncio.run(test())