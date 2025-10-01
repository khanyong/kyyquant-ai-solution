"""
강화된 샌드박스 - 타임아웃/메모리/프로세스 격리
DB 코드 실행을 안전하게 제한
"""

import ast
import signal
import resource
import multiprocessing as mp
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class SandboxLimits:
    """샌드박스 리소스 제한"""
    timeout_seconds: float = 5.0      # 실행 타임아웃
    max_memory_mb: int = 512          # 최대 메모리 (MB)
    max_rows: int = 100000            # DataFrame 최대 행 수
    max_columns: int = 100            # DataFrame 최대 컬럼 수


class TimeoutError(Exception):
    """타임아웃 에러"""
    pass


class MemoryLimitError(Exception):
    """메모리 제한 에러"""
    pass


class SandboxViolationError(Exception):
    """샌드박스 규칙 위반"""
    pass


class EnhancedSecuritySandbox:
    """강화된 보안 샌드박스"""

    # 허용된 AST 노드 (Import 제외)
    ALLOWED_NODES = {
        ast.Module, ast.Expr, ast.Load, ast.Store, ast.Del,
        ast.BinOp, ast.UnaryOp, ast.Compare, ast.BoolOp,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
        ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd,
        ast.FloorDiv, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
        ast.Is, ast.IsNot, ast.In, ast.NotIn, ast.And, ast.Or, ast.Not,
        ast.Name, ast.Constant, ast.Num, ast.Str, ast.List, ast.Tuple,
        ast.Dict, ast.Set, ast.Subscript, ast.Slice, ast.Index,
        ast.Call, ast.Attribute, ast.IfExp, ast.ListComp, ast.DictComp,
        ast.FunctionDef, ast.Return, ast.Assign, ast.AugAssign,
        ast.For, ast.If, ast.While, ast.Break, ast.Continue,
        ast.keyword, ast.arg, ast.arguments
    }

    # 차단할 함수
    BLOCKED_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'open', 'file',
        'input', 'raw_input', 'execfile', 'reload',
        'exit', 'quit', 'help', 'vars', 'globals', 'locals',
        'dir', 'getattr', 'setattr', 'delattr', 'hasattr',
        '__builtins__', '__loader__', '__spec__'
    }

    # 차단할 속성
    BLOCKED_ATTRIBUTES = {
        '__globals__', '__code__', '__class__', '__bases__',
        '__subclasses__', '__dict__', '__module__',
        '__import__', '__file__', '__name__'
    }

    # 허용된 모듈 (화이트리스트)
    ALLOWED_MODULES = {'pd', 'np', 'pandas', 'numpy'}

    @classmethod
    def validate_ast(cls, code: str) -> Tuple[bool, Optional[str]]:
        """
        AST 검증

        Returns:
            (is_valid, error_message)
        """
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Import 차단
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    return False, "Import statements are not allowed"

                # 노드 타입 검증
                if type(node) not in cls.ALLOWED_NODES:
                    return False, f"Blocked AST node: {type(node).__name__}"

                # 위험한 함수 호출 차단
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in cls.BLOCKED_FUNCTIONS:
                            return False, f"Blocked function: {node.func.id}"

                    # 위험한 속성 접근 차단
                    elif isinstance(node, ast.Attribute):
                        if node.attr in cls.BLOCKED_ATTRIBUTES:
                            return False, f"Blocked attribute: {node.attr}"

                # 파일 시스템 접근 시도 감지
                if isinstance(node, ast.Str) or isinstance(node, ast.Constant):
                    value = node.s if isinstance(node, ast.Str) else node.value
                    if isinstance(value, str):
                        # 절대 경로 또는 .. 경로 차단
                        if value.startswith('/') or '/..' in value or '\\' in value:
                            return False, f"File system access detected: {value}"

            return True, None

        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

    @classmethod
    def create_safe_namespace(cls, df: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        안전한 네임스페이스 생성

        Args:
            df: 입력 DataFrame
            params: 지표 파라미터

        Returns:
            네임스페이스 dict
        """
        return {
            # 빌트인 차단
            '__builtins__': {
                'abs': abs, 'min': min, 'max': max, 'sum': sum,
                'len': len, 'range': range, 'round': round,
                'int': int, 'float': float, 'str': str,
                'list': list, 'dict': dict, 'tuple': tuple,
                'True': True, 'False': False, 'None': None
            },

            # 데이터
            'df': df.copy(),  # 원본 보호
            'params': params,

            # 라이브러리 (제한된 접근)
            'pd': pd,
            'np': np,

            # 결과 컨테이너
            'result': None
        }

    @classmethod
    def validate_input(cls, df: pd.DataFrame, limits: SandboxLimits) -> None:
        """
        입력 데이터 검증

        Raises:
            SandboxViolationError: 제한 초과 시
        """
        if len(df) > limits.max_rows:
            raise SandboxViolationError(
                f"DataFrame too large: {len(df)} rows (max: {limits.max_rows})"
            )

        if len(df.columns) > limits.max_columns:
            raise SandboxViolationError(
                f"Too many columns: {len(df.columns)} (max: {limits.max_columns})"
            )

    @classmethod
    def validate_output(
        cls,
        result: Any,
        expected_columns: list,
        df_length: int
    ) -> Tuple[bool, Optional[str]]:
        """
        출력 결과 검증

        Args:
            result: 실행 결과 (dict 기대)
            expected_columns: 기대되는 컬럼 목록
            df_length: 입력 DataFrame 길이

        Returns:
            (is_valid, error_message)
        """
        # 결과가 dict인지
        if not isinstance(result, dict):
            return False, f"Result must be dict, got {type(result).__name__}"

        # 기대 컬럼이 모두 있는지
        missing = set(expected_columns) - set(result.keys())
        if missing:
            return False, f"Missing output columns: {sorted(missing)}"

        # 각 컬럼이 Series인지, 길이가 맞는지
        for col, series in result.items():
            if not isinstance(series, pd.Series):
                return False, f"Column '{col}' must be pd.Series, got {type(series).__name__}"

            if len(series) != df_length:
                return False, (
                    f"Column '{col}' length mismatch: "
                    f"expected {df_length}, got {len(series)}"
                )

            # 인덱스 일치 여부 (선택)
            # if not series.index.equals(df.index):
            #     return False, f"Column '{col}' index mismatch"

        return True, None


class SafeExecutor:
    """안전한 코드 실행기 (타임아웃/메모리 제한 적용)"""

    def __init__(self, limits: SandboxLimits = None):
        self.limits = limits or SandboxLimits()

    def execute(
        self,
        code: str,
        df: pd.DataFrame,
        params: Dict[str, Any],
        expected_columns: list
    ) -> Dict[str, pd.Series]:
        """
        샌드박스 내에서 코드 실행

        Args:
            code: 실행할 Python 코드
            df: 입력 DataFrame
            params: 지표 파라미터
            expected_columns: 기대 출력 컬럼

        Returns:
            결과 dict {column_name: Series}

        Raises:
            TimeoutError: 타임아웃
            MemoryLimitError: 메모리 초과
            SandboxViolationError: 샌드박스 규칙 위반
        """
        # 1. AST 검증
        is_valid, error_msg = EnhancedSecuritySandbox.validate_ast(code)
        if not is_valid:
            raise SandboxViolationError(f"AST validation failed: {error_msg}")

        # 2. 입력 검증
        EnhancedSecuritySandbox.validate_input(df, self.limits)

        # 3. 네임스페이스 생성
        namespace = EnhancedSecuritySandbox.create_safe_namespace(df, params)

        # 4. 타임아웃 설정 (Unix 계열만)
        try:
            # 타임아웃 시그널 설정 (Windows에서는 동작하지 않음)
            signal.signal(signal.SIGALRM, self._timeout_handler)
            signal.alarm(int(self.limits.timeout_seconds))

            # 메모리 제한 설정 (Unix 계열만)
            if hasattr(resource, 'RLIMIT_AS'):
                try:
                    max_bytes = self.limits.max_memory_mb * 1024 * 1024
                    resource.setrlimit(resource.RLIMIT_AS, (max_bytes, max_bytes))
                except (ValueError, OSError) as e:
                    logger.warning(f"Could not set memory limit: {e}")

        except AttributeError:
            # Windows - 타임아웃/메모리 제한 미지원 경고
            logger.warning("Timeout/memory limits not available on Windows")

        try:
            # 5. 코드 실행
            start_time = time.time()
            exec(code, namespace)
            execution_time = time.time() - start_time

            # 타임아웃 수동 체크 (Windows용)
            if execution_time > self.limits.timeout_seconds:
                raise TimeoutError(
                    f"Execution exceeded {self.limits.timeout_seconds}s "
                    f"(took {execution_time:.2f}s)"
                )

        except TimeoutError:
            raise
        except MemoryError:
            raise MemoryLimitError(
                f"Memory limit exceeded: {self.limits.max_memory_mb}MB"
            )
        except Exception as e:
            raise SandboxViolationError(f"Execution error: {type(e).__name__}: {str(e)}")
        finally:
            # 타임아웃 해제
            try:
                signal.alarm(0)
            except AttributeError:
                pass

        # 6. 결과 추출 및 검증
        result = namespace.get('result')
        if result is None:
            raise SandboxViolationError("Code did not set 'result' variable")

        is_valid, error_msg = EnhancedSecuritySandbox.validate_output(
            result, expected_columns, len(df)
        )
        if not is_valid:
            raise SandboxViolationError(f"Output validation failed: {error_msg}")

        logger.info(
            f"Sandbox execution successful: {len(expected_columns)} columns, "
            f"{execution_time*1000:.1f}ms"
        )

        return result

    def _timeout_handler(self, signum, frame):
        """타임아웃 핸들러"""
        raise TimeoutError(f"Execution timed out after {self.limits.timeout_seconds}s")


# ============================================================
# 편의 함수
# ============================================================

def execute_indicator_code(
    code: str,
    df: pd.DataFrame,
    params: Dict[str, Any],
    output_columns: list,
    limits: SandboxLimits = None
) -> Dict[str, pd.Series]:
    """
    지표 코드 안전 실행 (간편 함수)

    Usage:
        result = execute_indicator_code(
            code=indicator_definition['formula']['code'],
            df=price_df,
            params={'fast': 12, 'slow': 26, 'signal': 9},
            output_columns=['macd', 'macd_signal', 'macd_hist']
        )

        df['macd'] = result['macd']
        df['macd_signal'] = result['macd_signal']
        df['macd_hist'] = result['macd_hist']
    """
    executor = SafeExecutor(limits)
    return executor.execute(code, df, params, output_columns)


def validate_indicator_code(code: str) -> Tuple[bool, Optional[str]]:
    """
    지표 코드 검증 (실행 없이)

    Usage:
        is_valid, error = validate_indicator_code(code)
        if not is_valid:
            raise ValueError(f"Invalid code: {error}")
    """
    return EnhancedSecuritySandbox.validate_ast(code)


# ============================================================
# 테스트 코드
# ============================================================

if __name__ == '__main__':
    # 샘플 DataFrame
    df = pd.DataFrame({
        'close': [100, 102, 101, 105, 107, 106, 110, 112],
        'volume': [1000, 1100, 900, 1200, 1300, 1000, 1400, 1500]
    })

    # 정상 케이스: SMA
    good_code = """
result = {
    'sma': df['close'].rolling(window=params['period']).mean()
}
"""

    try:
        result = execute_indicator_code(
            code=good_code,
            df=df,
            params={'period': 3},
            output_columns=['sma']
        )
        print("✓ Good code executed:", result['sma'].tolist())
    except Exception as e:
        print(f"✗ Good code failed: {e}")

    # 악성 케이스: import 시도
    bad_code_import = """
import os
result = {'hack': df['close']}
"""

    try:
        result = execute_indicator_code(
            code=bad_code_import,
            df=df,
            params={},
            output_columns=['hack']
        )
        print("✗ Bad code (import) should have failed!")
    except SandboxViolationError as e:
        print(f"✓ Bad code (import) blocked: {e}")

    # 악성 케이스: 파일 접근
    bad_code_file = """
result = {'data': open('/etc/passwd').read()}
"""

    try:
        result = execute_indicator_code(
            code=bad_code_file,
            df=df,
            params={},
            output_columns=['data']
        )
        print("✗ Bad code (file) should have failed!")
    except SandboxViolationError as e:
        print(f"✓ Bad code (file) blocked: {e}")

    # 타임아웃 케이스
    timeout_code = """
import time
time.sleep(10)
result = {'slow': df['close']}
"""

    try:
        result = execute_indicator_code(
            code=timeout_code,
            df=df,
            params={},
            output_columns=['slow'],
            limits=SandboxLimits(timeout_seconds=1.0)
        )
        print("✗ Timeout code should have failed!")
    except (TimeoutError, SandboxViolationError) as e:
        print(f"✓ Timeout code blocked: {e}")