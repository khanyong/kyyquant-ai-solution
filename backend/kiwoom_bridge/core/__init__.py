"""
Core 모듈 - 표준화된 지표 계산 및 신호 생성
"""

from .naming import (
    _iname,
    _lc,
    _normalize_conditions,
    DEFAULT_PARAMS,
    COLUMN_MAPPING,
    convert_legacy_column,
    extract_indicator_params
)

from .indicators import (
    StandardIndicators,
    compute_indicators
)

from .signals import (
    evaluate_single_condition,
    evaluate_conditions as evaluate_conditions_base,
    evaluate_with_position_management,
    generate_signals
)

from .wrapper import (
    evaluate_conditions
)

__all__ = [
    # Naming utilities
    '_iname',
    '_lc',
    '_normalize_conditions',
    'DEFAULT_PARAMS',
    'COLUMN_MAPPING',
    'convert_legacy_column',
    'extract_indicator_params',

    # Indicators
    'StandardIndicators',
    'compute_indicators',

    # Signals
    'evaluate_single_condition',
    'evaluate_conditions',
    'evaluate_with_position_management',
    'generate_signals'
]