"""
프리플라이트 검증 시스템
백테스트 실행 전 전략/지표/조건의 정합성을 강제 검증
목적: "거래 0회", "컬럼 없음" 등 런타임 실패를 사전 차단
"""

import re
import ast
from typing import Dict, List, Set, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd

from indicators.calculator import IndicatorCalculator


class ValidationLevel(Enum):
    """검증 수준"""
    ERROR = "error"      # 실행 차단
    WARNING = "warning"  # 경고만
    INFO = "info"        # 정보성


@dataclass
class ValidationResult:
    """검증 결과"""
    level: ValidationLevel
    message: str
    details: Dict[str, Any] = None

    def __str__(self):
        prefix = {
            ValidationLevel.ERROR: "❌",
            ValidationLevel.WARNING: "⚠️",
            ValidationLevel.INFO: "ℹ️"
        }[self.level]
        return f"{prefix} {self.message}"


@dataclass
class PreflightReport:
    """프리플라이트 종합 보고서"""
    passed: bool
    errors: List[ValidationResult]
    warnings: List[ValidationResult]
    info: List[ValidationResult]

    def __str__(self):
        lines = ["=== Preflight Validation Report ==="]
        lines.append(f"Status: {'✅ PASS' if self.passed else '❌ FAIL'}")

        if self.errors:
            lines.append(f"\n🚫 Errors ({len(self.errors)}):")
            for err in self.errors:
                lines.append(f"  {err}")

        if self.warnings:
            lines.append(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  {warn}")

        if self.info:
            lines.append(f"\nℹ️  Info ({len(self.info)}):")
            for inf in self.info:
                lines.append(f"  {inf}")

        return "\n".join(lines)


class ConditionParser:
    """전략 조건 파서 - 필요한 컬럼 추출"""

    # 조건 연산자
    OPERATORS = {
        'crossover', 'crossunder',
        '>', '<', '>=', '<=', '==', '!=',
        'and', 'or', 'not'
    }

    # 허용된 함수
    FUNCTIONS = {
        'abs', 'min', 'max', 'round'
    }

    @staticmethod
    def extract_columns(condition: Dict[str, Any]) -> Set[str]:
        """
        조건에서 필요한 컬럼명 추출 (2가지 형식 지원)

        Format 1 (left/right):
            {"left": "macd", "operator": "crossover", "right": "macd_signal"}
            -> {"macd", "macd_signal"}

        Format 2 (indicator/compareTo):
            {"indicator": "macd", "operator": "cross_above", "compareTo": "macd_signal"}
            -> {"macd", "macd_signal"}

        Format 3 (indicator/value):
            {"indicator": "rsi", "operator": ">", "value": "70"}
            -> {"rsi"}
        """
        columns = set()

        # Format 1: left/right 피연산자 처리
        for side in ['left', 'right']:
            operand = condition.get(side)
            if not operand:
                continue

            # 문자열 피연산자 (컬럼명 또는 숫자)
            if isinstance(operand, str):
                # 숫자 리터럴 제외 (예: "0", "1.5")
                if not ConditionParser._is_numeric(operand):
                    columns.add(operand)

            # dict 피연산자 (중첩 조건)
            elif isinstance(operand, dict):
                columns.update(ConditionParser.extract_columns(operand))

        # Format 2: indicator/compareTo 처리
        indicator = condition.get('indicator')
        if indicator and isinstance(indicator, str):
            if not ConditionParser._is_numeric(indicator):
                columns.add(indicator)

        compare_to = condition.get('compareTo')
        if compare_to and isinstance(compare_to, str):
            if not ConditionParser._is_numeric(compare_to):
                columns.add(compare_to)

        # value는 숫자이므로 컬럼으로 취급 안 함

        # 중첩된 conditions 처리
        if 'conditions' in condition:
            for sub_cond in condition['conditions']:
                columns.update(ConditionParser.extract_columns(sub_cond))

        return columns

    @staticmethod
    def _is_numeric(s: str) -> bool:
        """문자열이 숫자인지 확인"""
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_condition_structure(condition: Dict[str, Any]) -> Optional[str]:
        """
        조건 구조 검증 (2가지 형식 지원)
        Returns: 에러 메시지 (없으면 None)
        """
        # 필수 필드
        if 'operator' not in condition:
            return "Missing 'operator' field"

        operator = condition['operator']

        # Binary operators - Format 1 (left/right) 또는 Format 2 (indicator/compareTo or value)
        binary_ops = {
            'crossover', 'crossunder', 'cross_above', 'cross_below',
            '>', '<', '>=', '<=', '==', '!=',
            'macd_cross_zero_up', 'macd_cross_zero_down'  # 특수 연산자
        }

        if operator in binary_ops:
            # Format 1: left/right
            has_left_right = 'left' in condition and 'right' in condition

            # Format 2: indicator + (compareTo or value)
            has_indicator = 'indicator' in condition
            has_compare_to = 'compareTo' in condition
            has_value = 'value' in condition

            if not (has_left_right or (has_indicator and (has_compare_to or has_value))):
                return (
                    f"Operator '{operator}' requires either:\n"
                    f"  - 'left' and 'right' (Format 1), or\n"
                    f"  - 'indicator' and ('compareTo' or 'value') (Format 2)"
                )

        # Logical operators
        elif operator in {'and', 'or', 'AND', 'OR'}:
            if 'conditions' not in condition:
                return f"Operator '{operator}' requires 'conditions' array"
            if not isinstance(condition['conditions'], list):
                return "'conditions' must be a list"
            if len(condition['conditions']) < 2:
                return f"Operator '{operator}' requires at least 2 conditions"

        elif operator in {'not', 'NOT'}:
            if 'condition' not in condition:
                return "Operator 'not' requires 'condition'"

        # 알 수 없는 연산자는 경고만 (유연성)
        # else:
        #     return f"Unknown operator: '{operator}'"

        return None


class IndicatorColumnMapper:
    """지표 → 생성 컬럼 매핑 (indicator_columns 테이블 활용)"""

    def __init__(self, calculator: IndicatorCalculator):
        self.calculator = calculator
        self._cache: Dict[str, List[str]] = {}

    async def get_output_columns(
        self,
        indicator_name: str,
        params: Dict[str, Any] = None
    ) -> List[str]:
        """
        지표가 생성하는 컬럼 목록 조회

        Args:
            indicator_name: 지표명 (예: 'macd', 'sma')
            params: 지표 파라미터 (예: {'period': 20})

        Returns:
            생성 컬럼 리스트 (예: ['macd', 'macd_signal', 'macd_hist'])
        """
        cache_key = f"{indicator_name}:{params}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # 1. indicator_columns 테이블에서 표준 컬럼 조회 (우선)
        try:
            result = await self.calculator.supabase.table('indicator_columns') \
                .select('column_name') \
                .eq('indicator_name', indicator_name) \
                .eq('is_active', True) \
                .order('output_order') \
                .execute()

            if result.data and len(result.data) > 0:
                columns = [row['column_name'] for row in result.data]
                self._cache[cache_key] = columns
                return columns
        except Exception as e:
            logger.warning(f"Failed to query indicator_columns: {e}")

        # 2. Fallback: indicators 테이블의 output_columns
        try:
            definition = await self.calculator.supabase.table('indicators') \
                .select('output_columns') \
                .eq('name', indicator_name) \
                .eq('is_active', True) \
                .single() \
                .execute()

            if definition.data:
                columns = definition.data.get('output_columns', [])
                self._cache[cache_key] = columns
                return columns
        except Exception as e:
            logger.warning(f"Failed to query indicators: {e}")

        return []

    def get_builtin_columns(self, indicator_name: str) -> List[str]:
        """
        내장 지표의 컬럼 (Supabase 없이 알 수 있는 것)
        가격 데이터는 항상 존재
        """
        BUILTIN_COLUMNS = {
            # 가격 데이터 (항상 존재)
            'price': ['open', 'high', 'low', 'close', 'volume'],

            # 단순 이동평균 (예측 가능)
            'sma': ['sma'],
            'ema': ['ema'],

            # 볼린저 밴드
            'bollinger_bands': ['bb_upper', 'bb_middle', 'bb_lower'],
            'bb': ['bb_upper', 'bb_middle', 'bb_lower'],

            # RSI
            'rsi': ['rsi'],

            # MACD
            'macd': ['macd', 'macd_signal', 'macd_hist'],

            # Stochastic
            'stochastic': ['stoch_k', 'stoch_d'],

            # ATR
            'atr': ['atr'],
        }

        return BUILTIN_COLUMNS.get(indicator_name.lower(), [])


class PreflightValidator:
    """프리플라이트 검증 메인 클래스"""

    def __init__(self, calculator: IndicatorCalculator):
        self.calculator = calculator
        self.mapper = IndicatorColumnMapper(calculator)

    async def validate_strategy(
        self,
        strategy_config: Dict[str, Any],
        stock_codes: List[str] = None,
        date_range: Tuple[str, str] = None
    ) -> PreflightReport:
        """
        전략 종합 검증

        Args:
            strategy_config: 전략 설정 (indicators, buyConditions, sellConditions)
            stock_codes: 백테스트 대상 종목 (선택)
            date_range: 백테스트 기간 (선택) - (start, end)

        Returns:
            PreflightReport
        """
        results = []

        # 1. 구조 검증
        results.extend(self._validate_structure(strategy_config))

        # 2. 지표 검증
        indicators = strategy_config.get('indicators', [])
        indicator_results = await self._validate_indicators(indicators)
        results.extend(indicator_results)

        # 3. 조건 검증
        buy_conditions = strategy_config.get('buyConditions', [])
        sell_conditions = strategy_config.get('sellConditions', [])

        # 지표가 생성하는 컬럼 목록
        available_columns = await self._get_available_columns(indicators)

        # 매수 조건 검증
        for i, cond in enumerate(buy_conditions):
            cond_results = self._validate_condition(
                cond, available_columns, f"buyConditions[{i}]"
            )
            results.extend(cond_results)

        # 매도 조건 검증
        for i, cond in enumerate(sell_conditions):
            cond_results = self._validate_condition(
                cond, available_columns, f"sellConditions[{i}]"
            )
            results.extend(cond_results)

        # 4. 데이터 기간 vs 지표 period 검증 (선택)
        if date_range:
            results.extend(
                self._validate_data_period(indicators, date_range)
            )

        # 결과 분류
        errors = [r for r in results if r.level == ValidationLevel.ERROR]
        warnings = [r for r in results if r.level == ValidationLevel.WARNING]
        info = [r for r in results if r.level == ValidationLevel.INFO]

        return PreflightReport(
            passed=(len(errors) == 0),
            errors=errors,
            warnings=warnings,
            info=info
        )

    def _validate_structure(self, config: Dict[str, Any]) -> List[ValidationResult]:
        """전략 구조 검증"""
        results = []

        # 필수 필드
        required = ['indicators', 'buyConditions', 'sellConditions']
        for field in required:
            if field not in config:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Missing required field: '{field}'"
                ))

        # indicators가 리스트인지
        if 'indicators' in config and not isinstance(config['indicators'], list):
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="'indicators' must be a list"
            ))

        # buyConditions가 리스트인지
        if 'buyConditions' in config and not isinstance(config['buyConditions'], list):
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="'buyConditions' must be a list"
            ))

        # sellConditions가 리스트인지
        if 'sellConditions' in config and not isinstance(config['sellConditions'], list):
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="'sellConditions' must be a list"
            ))

        # 조건이 비어있지 않은지
        if config.get('buyConditions') == []:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="No buy conditions defined (will never buy)"
            ))

        if config.get('sellConditions') == []:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="No sell conditions defined (will never sell)"
            ))

        return results

    async def _validate_indicators(
        self,
        indicators: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """지표 리스트 검증"""
        results = []

        if not indicators:
            results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="No indicators defined"
            ))
            return results

        for i, ind in enumerate(indicators):
            # name 필수
            if 'name' not in ind:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"indicators[{i}]: Missing 'name' field"
                ))
                continue

            name = ind['name']

            # Supabase에 지표 존재 확인
            try:
                definition = await self.calculator.supabase.table('indicators') \
                    .select('id, output_columns') \
                    .eq('name', name) \
                    .eq('is_active', True) \
                    .single() \
                    .execute()

                if not definition.data:
                    results.append(ValidationResult(
                        level=ValidationLevel.ERROR,
                        message=f"indicators[{i}]: Indicator '{name}' not found in Supabase"
                    ))
                else:
                    # output_columns 확인
                    columns = definition.data.get('output_columns', [])
                    if not columns:
                        results.append(ValidationResult(
                            level=ValidationLevel.ERROR,
                            message=f"indicators[{i}]: Indicator '{name}' has no output columns"
                        ))
                    else:
                        results.append(ValidationResult(
                            level=ValidationLevel.INFO,
                            message=f"indicators[{i}]: '{name}' → {columns}"
                        ))

            except Exception as e:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"indicators[{i}]: Failed to load '{name}': {e}"
                ))

        return results

    async def _get_available_columns(
        self,
        indicators: List[Dict[str, Any]]
    ) -> Set[str]:
        """지표들이 생성하는 모든 컬럼 집합"""
        columns = set()

        # 가격 데이터 (항상 존재)
        columns.update(['open', 'high', 'low', 'close', 'volume', 'trade_date'])

        # 지표가 생성하는 컬럼
        for ind in indicators:
            name = ind.get('name')
            if not name:
                continue

            try:
                ind_columns = await self.mapper.get_output_columns(
                    name, ind.get('params')
                )
                columns.update(ind_columns)
            except:
                # Supabase 실패 시 내장 컬럼으로 폴백
                builtin = self.mapper.get_builtin_columns(name)
                if builtin:
                    columns.update(builtin)

        return columns

    def _validate_condition(
        self,
        condition: Dict[str, Any],
        available_columns: Set[str],
        context: str
    ) -> List[ValidationResult]:
        """개별 조건 검증"""
        results = []

        # 구조 검증
        structure_error = ConditionParser.validate_condition_structure(condition)
        if structure_error:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"{context}: {structure_error}",
                details=condition
            ))
            return results

        # 필요한 컬럼 추출
        required_columns = ConditionParser.extract_columns(condition)

        # 컬럼 존재 확인
        missing = required_columns - available_columns
        if missing:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"{context}: Missing columns: {sorted(missing)}",
                details={
                    'condition': condition,
                    'required': sorted(required_columns),
                    'available': sorted(available_columns),
                    'missing': sorted(missing)
                }
            ))
        else:
            results.append(ValidationResult(
                level=ValidationLevel.INFO,
                message=f"{context}: ✓ All columns available ({sorted(required_columns)})"
            ))

        return results

    def _validate_data_period(
        self,
        indicators: List[Dict[str, Any]],
        date_range: Tuple[str, str]
    ) -> List[ValidationResult]:
        """데이터 기간 vs 지표 period 검증"""
        results = []

        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])
        total_days = (end_date - start_date).days

        # 최대 period 찾기
        max_period = 0
        for ind in indicators:
            params = ind.get('params', {})
            period = params.get('period', params.get('slow', params.get('length', 0)))
            if isinstance(period, (int, float)):
                max_period = max(max_period, int(period))

        if max_period > 0:
            # 최소 3배는 있어야 안정적
            min_required = max_period * 3

            if total_days < max_period:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    message=f"Data period ({total_days} days) is shorter than max indicator period ({max_period})"
                ))
            elif total_days < min_required:
                results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=f"Data period ({total_days} days) is less than 3x max period ({max_period}). May have insufficient warm-up data."
                ))

        return results


# ============================================================
# 유틸리티 함수
# ============================================================

async def preflight_check(
    strategy_config: Dict[str, Any],
    calculator: IndicatorCalculator,
    stock_codes: List[str] = None,
    date_range: Tuple[str, str] = None,
    raise_on_error: bool = True
) -> PreflightReport:
    """
    간편 프리플라이트 검증

    Usage:
        from backtest.preflight import preflight_check

        report = await preflight_check(
            strategy_config=config,
            calculator=indicator_calculator,
            raise_on_error=True
        )

        if not report.passed:
            raise ValueError(str(report))
    """
    validator = PreflightValidator(calculator)
    report = await validator.validate_strategy(
        strategy_config,
        stock_codes,
        date_range
    )

    if raise_on_error and not report.passed:
        raise ValueError(f"Preflight validation failed:\n{report}")

    return report