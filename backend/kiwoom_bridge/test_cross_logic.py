"""
cross_above/cross_below 로직 테스트
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_clear_cross_data():
    """명확한 교차가 있는 데이터 생성"""
    dates = pd.date_range('2024-01-01', periods=100)

    # MA20과 MA60이 확실히 교차하도록 설계
    prices = []

    # 첫 40일: 급격한 하락 (MA20 < MA60)
    for i in range(40):
        price = 60000 - i * 500  # 60000에서 40000까지 하락
        prices.append(price)

    # 다음 30일: 급격한 상승 (MA20이 MA60을 추월)
    for i in range(30):
        price = 40000 + i * 1000  # 40000에서 70000까지 상승
        prices.append(price)

    # 마지막 30일: 급격한 하락 (MA20이 다시 MA60 아래로)
    for i in range(30):
        price = 70000 - i * 1000  # 70000에서 40000까지 하락
        prices.append(price)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })

    return df

def test_manual_cross():
    """수동으로 교차 확인"""
    print("="*60)
    print("수동 교차 테스트")
    print("="*60)

    df = create_clear_cross_data()

    # MA 계산
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_60'] = df['close'].rolling(window=60).mean()

    # 유효한 데이터만 (NaN 제거)
    df_valid = df[60:].copy()

    print(f"\n가격 범위: {df['close'].min():.0f} ~ {df['close'].max():.0f}")
    print(f"유효 데이터: {len(df_valid)}개")

    # 교차 확인
    df_valid['ma_20_prev'] = df_valid['ma_20'].shift(1)
    df_valid['ma_60_prev'] = df_valid['ma_60'].shift(1)

    df_valid['golden_cross'] = (
        (df_valid['ma_20'] > df_valid['ma_60']) &
        (df_valid['ma_20_prev'] <= df_valid['ma_60_prev'])
    )

    df_valid['dead_cross'] = (
        (df_valid['ma_20'] < df_valid['ma_60']) &
        (df_valid['ma_20_prev'] >= df_valid['ma_60_prev'])
    )

    golden = df_valid[df_valid['golden_cross']]
    dead = df_valid[df_valid['dead_cross']]

    print(f"\n골든크로스: {len(golden)}개")
    for _, row in golden.iterrows():
        print(f"  {row['date'].date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

    print(f"\n데드크로스: {len(dead)}개")
    for _, row in dead.iterrows():
        print(f"  {row['date'].date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

    # MA 차이 확인
    df_valid['ma_diff'] = df_valid['ma_20'] - df_valid['ma_60']
    print(f"\nMA20-MA60 차이:")
    print(f"  최소: {df_valid['ma_diff'].min():.0f}")
    print(f"  최대: {df_valid['ma_diff'].max():.0f}")

    # 중간 지점 확인
    mid_point = len(df_valid) // 2
    print(f"\n중간 지점 데이터:")
    print(df_valid.iloc[mid_point-2:mid_point+2][['date', 'close', 'ma_20', 'ma_60', 'ma_diff']])

    return df

def test_core_cross():
    """Core 모듈의 cross_above 테스트"""
    print("\n" + "="*60)
    print("Core 모듈 cross_above 테스트")
    print("="*60)

    try:
        from core import compute_indicators, evaluate_conditions

        df = create_clear_cross_data()

        # 지표 계산
        indicators = [
            {"type": "ma", "params": {"period": 20}},
            {"type": "ma", "params": {"period": 60}}
        ]

        df_with_ind = compute_indicators(df, indicators)

        # 디버깅: 생성된 MA 값 확인
        print("\nMA 값 샘플 (60일 이후):")
        sample = df_with_ind[60:65][['date', 'close', 'ma_20', 'ma_60']].copy()
        sample['ma_diff'] = sample['ma_20'] - sample['ma_60']
        print(sample)

        # 조건 평가
        buy_conditions = [
            {"indicator": "ma_20", "operator": "cross_above", "value": "ma_60"}
        ]
        sell_conditions = [
            {"indicator": "ma_20", "operator": "cross_below", "value": "ma_60"}
        ]

        df_final = evaluate_conditions(df_with_ind, buy_conditions, sell_conditions)

        buy_signals = (df_final['buy_signal'] == 1).sum()
        sell_signals = (df_final['sell_signal'] == -1).sum()

        print(f"\nCore 모듈 신호:")
        print(f"  매수: {buy_signals}")
        print(f"  매도: {sell_signals}")

        if buy_signals > 0:
            print("\n매수 신호 위치:")
            for _, row in df_final[df_final['buy_signal'] == 1].iterrows():
                print(f"  {row['date'].date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

        if sell_signals > 0:
            print("\n매도 신호 위치:")
            for _, row in df_final[df_final['sell_signal'] == -1].iterrows():
                print(f"  {row['date'].date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

        # cross_above 내부 로직 테스트
        print("\n" + "="*60)
        print("cross_above 내부 로직 분석")
        print("="*60)

        # signals.py의 로직을 직접 테스트
        df_test = df_with_ind[60:].copy()  # NaN 제거

        # cross_above: 현재 > AND 이전 <=
        current_above = df_test['ma_20'] > df_test['ma_60']
        prev_below = df_test['ma_20'].shift(1) <= df_test['ma_60'].shift(1)
        cross_above_manual = current_above & prev_below

        print(f"현재 MA20 > MA60: {current_above.sum()}개")
        print(f"이전 MA20 <= MA60: {prev_below.sum()}개")
        print(f"교차 (AND): {cross_above_manual.sum()}개")

        if cross_above_manual.sum() > 0:
            print("\n수동 계산 교차점:")
            for idx in df_test[cross_above_manual].index:
                row = df_test.loc[idx]
                print(f"  {row['date'].date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

    except ImportError as e:
        print(f"❌ Core 모듈 로드 실패: {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 1. 수동 교차 테스트
    test_manual_cross()

    # 2. Core 모듈 테스트
    test_core_cross()

    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)