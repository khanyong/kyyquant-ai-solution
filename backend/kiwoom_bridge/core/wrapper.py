"""
Core 모듈 Wrapper - 호환성을 위한 래퍼 함수들
"""

import pandas as pd
from typing import List, Dict, Any
from .signals import evaluate_conditions as _evaluate_conditions_base


def evaluate_conditions(df: pd.DataFrame,
                       buy_conditions: List[Dict[str, Any]],
                       sell_conditions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    매수/매도 조건을 평가하고 buy_signal, sell_signal 컬럼을 추가

    Args:
        df: 입력 데이터프레임
        buy_conditions: 매수 조건 리스트
        sell_conditions: 매도 조건 리스트

    Returns:
        buy_signal, sell_signal 컬럼이 추가된 데이터프레임
    """
    df = df.copy()

    # 매수 신호 평가
    buy_signal = _evaluate_conditions_base(df, buy_conditions, 'buy')
    df['buy_signal'] = buy_signal

    # 매도 신호 평가
    sell_signal = _evaluate_conditions_base(df, sell_conditions, 'sell')
    df['sell_signal'] = sell_signal

    return df