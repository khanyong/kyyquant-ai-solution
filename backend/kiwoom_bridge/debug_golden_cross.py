"""
골든크로스 전략 디버깅
- 실제 데이터로 MA 계산
- 조건 평가 과정 추적
- 신호 생성 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# core 모듈 import
from core import compute_indicators, evaluate_conditions, _normalize_conditions

def debug_golden_cross():
    """골든크로스 전략 디버깅"""

    print("="*60)
    print("골든크로스 전략 디버깅")
    print("="*60)

    # 1. 실제와 유사한 데이터 생성 (삼성전자 패턴)
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')

    # 추세가 있는 가격 데이터 생성
    base_price = 70000
    prices = []
    for i in range(100):
        if i < 30:
            # 하락 추세
            base_price = base_price * 0.995
        elif i < 60:
            # 상승 추세 (골든크로스 발생)
            base_price = base_price * 1.005
        else:
            # 다시 하락 (데드크로스 발생)
            base_price = base_price * 0.997

        # 약간의 노이즈 추가
        price = base_price + np.random.randn() * 500
        prices.append(price)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })

    print(f"데이터 생성 완료: {len(df)}개")
    print(f"가격 범위: {min(prices):.0f} ~ {max(prices):.0f}")

    # 2. 전략 설정 (실제 전략과 동일)
    config = {
        "indicators": [
            {"type": "MA", "params": {"period": 20}},
            {"type": "MA", "params": {"period": 60}}
        ],
        "buyConditions": [
            {
                "indicator": "ma_20",
                "operator": ">",
                "value": "ma_60",
                "combineWith": "AND"
            }
        ],
        "sellConditions": [
            {
                "indicator": "ma_20",
                "operator": "<",
                "value": "ma_60",
                "combineWith": "AND"
            }
        ]
    }

    print("\n전략 설정:")
    print(json.dumps(config, indent=2, ensure_ascii=False))

    # 3. 지표 계산
    print("\n" + "="*40)
    print("지표 계산")
    print("="*40)

    df = compute_indicators(df, config)

    # 계산된 컬럼 확인
    print("계산된 컬럼:", [col for col in df.columns if 'ma' in col.lower()])

    # MA 값 확인
    if 'ma_20' in df.columns and 'ma_60' in df.columns:
        print("\nMA 값 샘플 (마지막 10일):")
        print(df[['date', 'close', 'ma_20', 'ma_60']].tail(10))

        # 골든크로스/데드크로스 시점 찾기
        df['ma_20_above'] = df['ma_20'] > df['ma_60']
        cross_points = df['ma_20_above'] != df['ma_20_above'].shift(1)

        print(f"\n교차 발생 횟수: {cross_points.sum()}회")

        if cross_points.sum() > 0:
            print("교차 시점:")
            print(df[cross_points][['date', 'close', 'ma_20', 'ma_60', 'ma_20_above']].head(10))
    else:
        print("❌ MA 컬럼이 생성되지 않음!")
        print("실제 컬럼:", df.columns.tolist())

    # 4. 조건 평가
    print("\n" + "="*40)
    print("조건 평가")
    print("="*40)

    # 매수 조건
    buy_conditions = config['buyConditions']
    print(f"원본 매수 조건: {buy_conditions}")

    # 정규화 확인
    normalized_buy = _normalize_conditions(buy_conditions)
    print(f"정규화된 매수 조건: {normalized_buy}")

    # 신호 생성
    buy_signal = evaluate_conditions(df, buy_conditions, 'buy')
    print(f"\n매수 신호 생성: {buy_signal.sum()}개")

    if buy_signal.sum() > 0:
        print("매수 신호 시점:")
        print(df[buy_signal == 1][['date', 'close', 'ma_20', 'ma_60']].head())

    # 매도 조건
    sell_conditions = config['sellConditions']
    sell_signal = evaluate_conditions(df, sell_conditions, 'sell')
    print(f"\n매도 신호 생성: {abs(sell_signal.sum())}개")

    if sell_signal.sum() != 0:
        print("매도 신호 시점:")
        print(df[sell_signal == -1][['date', 'close', 'ma_20', 'ma_60']].head())

    # 5. 문제 진단
    print("\n" + "="*40)
    print("문제 진단")
    print("="*40)

    # 조건 만족 확인 (진입 시점 무시)
    if 'ma_20' in df.columns and 'ma_60' in df.columns:
        buy_condition_met = df['ma_20'] > df['ma_60']
        sell_condition_met = df['ma_20'] < df['ma_60']

        print(f"ma_20 > ma_60 조건 만족: {buy_condition_met.sum()}일")
        print(f"ma_20 < ma_60 조건 만족: {sell_condition_met.sum()}일")

        # 진입 시점 계산
        buy_entry = buy_condition_met & ~buy_condition_met.shift(1).fillna(False)
        sell_entry = sell_condition_met & ~sell_condition_met.shift(1).fillna(False)

        print(f"\n실제 매수 진입점: {buy_entry.sum()}개")
        print(f"실제 매도 진입점: {sell_entry.sum()}개")

        if buy_entry.sum() > 0:
            print("\n매수 진입 시점 상세:")
            for idx in df[buy_entry].index[:5]:
                if idx > 0:
                    prev_ma20 = df.loc[idx-1, 'ma_20']
                    prev_ma60 = df.loc[idx-1, 'ma_60']
                    curr_ma20 = df.loc[idx, 'ma_20']
                    curr_ma60 = df.loc[idx, 'ma_60']
                    print(f"  {df.loc[idx, 'date']}: MA20 {prev_ma20:.0f}->{curr_ma20:.0f}, MA60 {prev_ma60:.0f}->{curr_ma60:.0f}")

    # 6. 가능한 문제들
    print("\n" + "="*40)
    print("가능한 문제들")
    print("="*40)

    problems = []

    # 문제 1: MA 컬럼명 불일치
    if 'ma_20' not in df.columns:
        problems.append("❌ ma_20 컬럼이 없음 (실제 컬럼명 확인 필요)")
        ma_cols = [col for col in df.columns if 'ma' in col.lower() or 'sma' in col.lower()]
        if ma_cols:
            problems.append(f"   발견된 MA 관련 컬럼: {ma_cols}")

    # 문제 2: NaN 값
    if 'ma_60' in df.columns:
        nan_count = df['ma_60'].isna().sum()
        if nan_count > 60:
            problems.append(f"❌ MA60의 NaN 값이 너무 많음: {nan_count}개")
            problems.append("   -> 60일 이동평균은 최소 60일 데이터 필요")

    # 문제 3: 조건 설정 오류
    if buy_signal.sum() == 0 and 'ma_20' in df.columns and 'ma_60' in df.columns:
        if (df['ma_20'] > df['ma_60']).sum() > 0:
            problems.append("❌ 조건은 만족하지만 신호가 생성되지 않음")
            problems.append("   -> 신호 생성 로직 문제 또는 포지션 관리 문제")

    for problem in problems:
        print(problem)

    if not problems:
        print("✅ 명백한 문제를 찾지 못함")
        print("   -> 실제 데이터나 백테스트 엔진 로직 확인 필요")

    return df, buy_signal, sell_signal


def check_actual_strategy():
    """실제 전략 JSON 검증"""
    print("\n" + "="*60)
    print("실제 전략 검증")
    print("="*60)

    actual_config = {
        "indicators": [
            {"type": "ma", "period": 20},  # ❌ params가 없음!
            {"type": "ma", "period": 60}   # ❌ params가 없음!
        ],
        "buyConditions": [
            {
                "indicator": "ma_20",
                "operator": ">",
                "value": "ma_60"
            }
        ]
    }

    print("문제 발견!")
    print("❌ indicators에 'params' 키가 없음")
    print("   기존: {'type': 'ma', 'period': 20}")
    print("   필요: {'type': 'MA', 'params': {'period': 20}}")

    # 올바른 설정
    correct_config = {
        "indicators": [
            {"type": "MA", "params": {"period": 20}},
            {"type": "MA", "params": {"period": 60}}
        ],
        "buyConditions": [
            {"indicator": "ma_20", "operator": ">", "value": "ma_60"}
        ],
        "sellConditions": [
            {"indicator": "ma_20", "operator": "<", "value": "ma_60"}
        ]
    }

    print("\n✅ 올바른 설정:")
    print(json.dumps(correct_config, indent=2, ensure_ascii=False))

    return correct_config


if __name__ == "__main__":
    # 골든크로스 디버깅
    df, buy_signal, sell_signal = debug_golden_cross()

    # 실제 전략 검증
    correct_config = check_actual_strategy()

    print("\n" + "="*60)
    print("디버깅 완료")
    print("="*60)