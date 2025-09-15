"""
신호 생성 및 조건 평가 모듈
- 정규화된 조건 평가
- 교차(cross) 및 비교 연산 지원
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from .naming import _normalize_conditions, _lc

def evaluate_single_condition(df: pd.DataFrame, condition: Dict[str, Any]) -> pd.Series:
    """
    단일 조건 평가

    Args:
        df: 데이터프레임
        condition: 평가할 조건

    Returns:
        조건 결과 (Boolean Series)
    """
    indicator = condition.get('indicator', '').lower()
    operator = condition.get('operator', '').lower()
    value = condition.get('value', 0)

    # 지표 컬럼 확인
    if indicator not in df.columns:
        print(f"경고: 지표 '{indicator}'를 찾을 수 없습니다")
        return pd.Series(False, index=df.index)

    ind_values = df[indicator]

    # 비교 값 처리
    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in df.columns:
            compare_values = df[value_lower]
        else:
            try:
                compare_values = float(value)
            except ValueError:
                print(f"경고: 값 '{value}'를 처리할 수 없습니다")
                return pd.Series(False, index=df.index)
    else:
        compare_values = float(value)

    # 조건 평가
    if operator == '>':
        result = ind_values > compare_values
    elif operator == '<':
        result = ind_values < compare_values
    elif operator == '>=':
        result = ind_values >= compare_values
    elif operator == '<=':
        result = ind_values <= compare_values
    elif operator == '==':
        result = ind_values == compare_values
    elif operator == '!=':
        result = ind_values != compare_values
    elif operator == 'cross_above':
        if isinstance(compare_values, pd.Series):
            result = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values.shift(1))
        else:
            result = (ind_values > compare_values) & (ind_values.shift(1) <= compare_values)
    elif operator == 'cross_below':
        if isinstance(compare_values, pd.Series):
            result = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values.shift(1))
        else:
            result = (ind_values < compare_values) & (ind_values.shift(1) >= compare_values)
    else:
        print(f"경고: 알 수 없는 연산자 '{operator}'")
        result = pd.Series(False, index=df.index)

    return result

def evaluate_conditions(df: pd.DataFrame, conditions: List[Dict], signal_type: str = 'buy') -> pd.Series:
    """
    여러 조건 평가 및 신호 생성

    Args:
        df: 데이터프레임
        conditions: 평가할 조건 리스트
        signal_type: 신호 타입 ('buy' or 'sell')

    Returns:
        신호 Series (1: buy, -1: sell, 0: no signal)
    """
    if not conditions:
        return pd.Series(0, index=df.index)

    # 조건 정규화
    conditions = _normalize_conditions(conditions)

    # 각 조건 평가
    condition_results = []
    for i, condition in enumerate(conditions):
        result = evaluate_single_condition(df, condition)
        combine = condition.get('combineWith', 'and' if i > 0 else None)
        condition_results.append((result, combine))

    # 조건 결합
    if condition_results:
        final_result = condition_results[0][0]

        for i in range(1, len(condition_results)):
            if condition_results[i][1] == 'and':
                final_result = final_result & condition_results[i][0]
            else:  # or
                final_result = final_result | condition_results[i][0]

        # 신호 생성 (진입 시점만)
        signal = pd.Series(0, index=df.index)
        signal[final_result & ~final_result.shift(1).fillna(False)] = 1 if signal_type == 'buy' else -1

        return signal

    return pd.Series(0, index=df.index)

def evaluate_with_position_management(df: pd.DataFrame, strategy_config: Dict,
                                     signal_type: str, positions: Dict = None,
                                     stock_code: str = 'TEST') -> pd.Series:
    """
    포지션 관리를 포함한 조건 평가 (목표수익률, 손절 등)

    Args:
        df: 데이터프레임
        strategy_config: 전략 설정
        signal_type: 신호 타입
        positions: 현재 포지션 딕셔너리
        stock_code: 종목 코드

    Returns:
        신호 Series
    """
    # 기본 조건 평가
    if signal_type == 'sell':
        conditions = strategy_config.get('sellConditions', [])
    else:
        conditions = strategy_config.get('buyConditions', [])

    base_signal = evaluate_conditions(df, conditions, signal_type)

    # 매도 시 포지션 관리 로직
    if signal_type == 'sell' and positions and stock_code in positions:
        position = positions[stock_code]
        target_profit = strategy_config.get('targetProfit', {})
        stop_loss = strategy_config.get('stopLoss', {})

        # 목표 수익률 처리
        if target_profit:
            mode = target_profit.get('mode', 'simple')

            if mode == 'simple' and target_profit.get('enabled'):
                profit_signal = pd.Series(0, index=df.index)

                # simple 모드 처리
                if target_profit.get('simple'):
                    target_value = target_profit['simple'].get('value', 5.0)
                    combine_method = _lc(target_profit['simple'].get('combineWith', 'or'))
                else:
                    # 이전 버전 호환성
                    target_value = target_profit.get('value', 5.0)
                    combine_method = _lc(target_profit.get('combineWith', 'or'))

                for idx in df.index:
                    current_price = df.loc[idx, 'close']
                    profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                    if profit_pct >= target_value:
                        profit_signal[idx] = -1

                # 기존 조건과 결합
                if combine_method == 'and':
                    base_signal = base_signal & profit_signal
                else:  # or
                    base_signal = base_signal | profit_signal

            elif mode == 'staged' and target_profit.get('staged', {}).get('enabled'):
                # 단계별 목표 모드
                profit_signal = pd.Series(0, index=df.index)
                staged_config = target_profit['staged']
                stages = staged_config.get('stages', [])

                # 이미 실행된 단계 추적
                if not hasattr(position, 'executed_stages'):
                    position.executed_stages = []

                for idx in df.index:
                    current_price = df.loc[idx, 'close']
                    profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                    for stage in stages:
                        stage_num = stage.get('stage', 1)
                        stage_target = stage.get('targetProfit', 5.0)
                        exit_ratio = stage.get('exitRatio', 100) / 100.0
                        stage_combine = _lc(stage.get('combineWith', staged_config.get('combineWith', 'or')))

                        if stage_num in position.executed_stages:
                            continue

                        if profit_pct >= stage_target:
                            # 단계별 매도 비율 저장
                            if not hasattr(profit_signal, 'exit_ratios'):
                                profit_signal.exit_ratios = {}
                            profit_signal.exit_ratios[idx] = exit_ratio

                            # 단계별 결합 방식 저장
                            if not hasattr(profit_signal, 'stage_combines'):
                                profit_signal.stage_combines = {}
                            profit_signal.stage_combines[idx] = stage_combine

                            profit_signal[idx] = -exit_ratio
                            position.executed_stages.append(stage_num)

                            # 동적 손절 조정
                            if stage.get('dynamicStopLoss', False):
                                if hasattr(position, 'dynamic_stop_loss'):
                                    position.dynamic_stop_loss = max(
                                        position.dynamic_stop_loss,
                                        position.avg_price * (1 + stage_target / 100)
                                    )
                                else:
                                    position.dynamic_stop_loss = position.avg_price * (1 + stage_target / 100)
                            break

                # 단계별 신호 결합
                combined_signal = pd.Series(0, index=df.index)
                for idx in df.index:
                    if profit_signal[idx] != 0:
                        stage_combine = _lc(getattr(profit_signal, 'stage_combines', {}).get(idx, 'or'))

                        if stage_combine == 'and':
                            if base_signal[idx] != 0:
                                combined_signal[idx] = profit_signal[idx]
                        else:  # or
                            if profit_signal[idx] != 0:
                                combined_signal[idx] = profit_signal[idx]
                            elif base_signal[idx] != 0:
                                combined_signal[idx] = base_signal[idx]
                    elif base_signal[idx] != 0:
                        combined_signal[idx] = base_signal[idx]

                base_signal = combined_signal

        # 손절 처리 (항상 OR)
        if stop_loss.get('enabled'):
            loss_signal = pd.Series(0, index=df.index)
            loss_value = stop_loss.get('value', 3.0)

            # 트레일링 스톱
            trailing_stop = stop_loss.get('trailingStop', {})

            for idx in df.index:
                current_price = df.loc[idx, 'close']
                profit_pct = ((current_price - position.avg_price) / position.avg_price) * 100

                # 동적 손절 확인
                if hasattr(position, 'dynamic_stop_loss'):
                    dynamic_loss_pct = ((current_price - position.dynamic_stop_loss) / position.dynamic_stop_loss) * 100
                    if dynamic_loss_pct <= 0:
                        loss_signal[idx] = -1
                        continue

                # 트레일링 스톱
                if trailing_stop.get('enabled'):
                    activation = trailing_stop.get('activation', 5.0)
                    distance = trailing_stop.get('distance', 2.0)

                    if not hasattr(position, 'peak_price'):
                        position.peak_price = position.avg_price

                    if profit_pct >= activation:
                        position.peak_price = max(position.peak_price, current_price)
                        peak_drop_pct = ((current_price - position.peak_price) / position.peak_price) * 100

                        if peak_drop_pct <= -abs(distance):
                            loss_signal[idx] = -1
                            continue

                # 일반 손절
                if profit_pct <= -abs(loss_value):
                    loss_signal[idx] = -1

            # 손절은 항상 OR로 결합
            base_signal = base_signal | loss_signal

    return base_signal

def generate_signals(df: pd.DataFrame, strategy_config: Dict) -> pd.DataFrame:
    """
    전략 설정에 따라 매수/매도 신호 생성

    Args:
        df: OHLCV + 지표 데이터프레임
        strategy_config: 전략 설정

    Returns:
        신호가 추가된 데이터프레임
    """
    buy_conditions = strategy_config.get('buyConditions', [])
    sell_conditions = strategy_config.get('sellConditions', [])

    df['buy_signal'] = evaluate_conditions(df, buy_conditions, 'buy')
    df['sell_signal'] = evaluate_conditions(df, sell_conditions, 'sell')

    return df