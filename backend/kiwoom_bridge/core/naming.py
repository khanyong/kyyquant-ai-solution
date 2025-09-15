"""
네이밍 규약 및 유틸리티 함수
- 모든 컬럼명은 소문자 + 파라미터 포함
- 조건 정규화
"""

from typing import Any, List, Dict, Optional

def _iname(base: str, *params) -> str:
    """
    지표명 생성 - 모든 파라미터를 소문자로 변환하여 연결

    Examples:
        _iname('rsi', 14) -> 'rsi_14'
        _iname('macd', 12, 26) -> 'macd_12_26'
        _iname('bb_upper', 20, 2) -> 'bb_upper_20_2'
    """
    parts = [str(base).lower()] + [str(p).lower() for p in params if p is not None]
    return "_".join(parts)

def _lc(s: Any) -> Any:
    """
    문자열을 소문자로 변환, 다른 타입은 그대로 반환

    Examples:
        _lc('RSI') -> 'rsi'
        _lc(14) -> 14
        _lc(None) -> None
    """
    return s.lower() if isinstance(s, str) else s

def _normalize_conditions(conditions: Optional[List[Dict]]) -> List[Dict]:
    """
    조건 정규화 - 지표명, 연산자, 값을 소문자화

    Args:
        conditions: 조건 리스트

    Returns:
        정규화된 조건 리스트

    Example:
        Input: [{'indicator': 'RSI_14', 'operator': 'CROSS_ABOVE', 'value': 'SMA_20'}]
        Output: [{'indicator': 'rsi_14', 'operator': 'cross_above', 'value': 'sma_20'}]
    """
    norm = []
    for c in conditions or []:
        # c가 이미 dict인지 확인
        if isinstance(c, dict):
            c = dict(c)  # 복사본 생성
        else:
            # c가 dict가 아닌 경우 스킵
            continue
        c['indicator'] = _lc(c.get('indicator', ''))
        c['operator'] = _lc(c.get('operator', ''))
        v = c.get('value', 0)
        c['value'] = _lc(v) if isinstance(v, str) else v
        c['combineWith'] = _lc(c.get('combineWith')) if c.get('combineWith') else None
        norm.append(c)
    return norm

# 표준 지표 파라미터 기본값
DEFAULT_PARAMS = {
    'sma': {'period': 20},
    'ema': {'period': 20},
    'rsi': {'period': 14},
    'macd': {'fast': 12, 'slow': 26, 'signal': 9},
    'bb': {'period': 20, 'std': 2},
    'stoch': {'k_period': 14, 'd_period': 3},
    'atr': {'period': 14},
    'adx': {'period': 14},
    'cci': {'period': 20},
    'mfi': {'period': 14},
    'willr': {'period': 14},
    'vr': {'period': 20},
}

# 대문자 별칭 -> 소문자 표준 매핑 테이블
COLUMN_MAPPING = {
    # 가격 데이터
    'OPEN': 'open',
    'HIGH': 'high',
    'LOW': 'low',
    'CLOSE': 'close',
    'VOLUME': 'volume',
    'PRICE': 'price',

    # 이동평균
    'SMA_20': 'sma_20',
    'EMA_20': 'ema_20',
    'MA_20': 'ma_20',
    'SMA_50': 'sma_50',
    'EMA_50': 'ema_50',
    'MA_50': 'ma_50',
    'SMA_200': 'sma_200',
    'EMA_200': 'ema_200',

    # RSI
    'RSI_14': 'rsi_14',
    'RSI_9': 'rsi_9',
    'RSI_25': 'rsi_25',

    # MACD
    'MACD': 'macd_12_26',
    'MACD_SIGNAL': 'macd_signal_12_26_9',
    'MACD_HIST': 'macd_hist_12_26_9',

    # 볼린저 밴드
    'BB_UPPER': 'bb_upper_20_2',
    'BB_MIDDLE': 'bb_middle_20',
    'BB_LOWER': 'bb_lower_20_2',

    # 스토캐스틱
    'STOCH_K': 'stoch_k_14_3',
    'STOCH_D': 'stoch_d_14_3',

    # 기타 지표
    'ATR_14': 'atr_14',
    'ADX_14': 'adx_14',
    'CCI_20': 'cci_20',
    'MFI_14': 'mfi_14',
    'WILLR_14': 'willr_14',
    'OBV': 'obv',
    'VR_20': 'vr_20',
}

def convert_legacy_column(column_name: str) -> str:
    """
    레거시 대문자 컬럼명을 표준 소문자 컬럼명으로 변환

    Args:
        column_name: 변환할 컬럼명

    Returns:
        표준 컬럼명

    Examples:
        convert_legacy_column('RSI_14') -> 'rsi_14'
        convert_legacy_column('BB_UPPER') -> 'bb_upper_20_2'
    """
    return COLUMN_MAPPING.get(column_name.upper(), column_name.lower())

def extract_indicator_params(indicator_name: str) -> Dict[str, Any]:
    """
    지표명에서 파라미터 추출

    Args:
        indicator_name: 파라미터가 포함된 지표명

    Returns:
        지표 타입과 파라미터 딕셔너리

    Examples:
        extract_indicator_params('rsi_14') -> {'type': 'rsi', 'period': 14}
        extract_indicator_params('macd_12_26') -> {'type': 'macd', 'fast': 12, 'slow': 26}
    """
    parts = indicator_name.lower().split('_')
    indicator_type = parts[0]

    result = {'type': indicator_type}

    if indicator_type in ['sma', 'ema', 'ma', 'rsi', 'atr', 'adx', 'cci', 'mfi', 'willr', 'vr']:
        if len(parts) > 1:
            result['period'] = int(parts[1])
    elif indicator_type == 'macd':
        if 'signal' in indicator_name:
            if len(parts) >= 4:
                result['fast'] = int(parts[2])
                result['slow'] = int(parts[3])
                result['signal'] = int(parts[4]) if len(parts) > 4 else 9
        elif 'hist' in indicator_name:
            if len(parts) >= 4:
                result['fast'] = int(parts[2])
                result['slow'] = int(parts[3])
                result['signal'] = int(parts[4]) if len(parts) > 4 else 9
        else:
            if len(parts) >= 3:
                result['fast'] = int(parts[1])
                result['slow'] = int(parts[2])
    elif indicator_type == 'bb':
        if len(parts) >= 3:
            result['period'] = int(parts[2])
            if len(parts) > 3:
                result['std'] = int(parts[3])
    elif indicator_type == 'stoch':
        if len(parts) >= 3:
            result['k_period'] = int(parts[2])
            if len(parts) > 3:
                result['d_period'] = int(parts[3])

    return result