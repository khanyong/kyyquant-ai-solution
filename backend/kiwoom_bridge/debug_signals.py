"""
신호 생성 디버깅 스크립트
- RSI 값 확인
- 조건 평가 과정 추적
- 신호 생성 여부 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from core import compute_indicators, evaluate_conditions, _normalize_conditions

def debug_rsi_signals():
    """RSI 반전 전략 디버깅"""

    # 1. 테스트 데이터 생성 (극단적인 가격 변동 포함)
    print("="*60)
    print("RSI 신호 디버깅")
    print("="*60)

    # RSI가 극단값을 갖도록 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')

    # 가격 패턴: 하락 -> 상승 -> 하락
    prices = []
    # 초기 가격
    base_price = 50000

    # 1-20일: 급락 (RSI 낮음)
    for i in range(20):
        base_price *= 0.98  # 매일 2% 하락
        prices.append(base_price)

    # 21-40일: 횡보
    for i in range(20):
        prices.append(base_price + np.random.randn() * 100)

    # 41-60일: 급등 (RSI 높음)
    for i in range(20):
        base_price *= 1.02  # 매일 2% 상승
        prices.append(base_price)

    # 61-80일: 횡보
    for i in range(20):
        prices.append(base_price + np.random.randn() * 100)

    # 81-100일: 급락
    for i in range(20):
        base_price *= 0.98
        prices.append(base_price)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000] * 100
    })

    print(f"데이터 생성 완료: {len(df)}개 행")
    print(f"가격 범위: {min(prices):.0f} ~ {max(prices):.0f}")

    # 2. RSI 계산
    config = {
        'indicators': [
            {'type': 'RSI', 'params': {'period': 14}}
        ]
    }

    df = compute_indicators(df, config)

    print(f"\nRSI 계산 완료")
    print(f"RSI 범위: {df['rsi_14'].min():.2f} ~ {df['rsi_14'].max():.2f}")
    print(f"RSI < 30인 날: {(df['rsi_14'] < 30).sum()}개")
    print(f"RSI > 70인 날: {(df['rsi_14'] > 70).sum()}개")

    # RSI 극값 확인
    print("\nRSI 극값 상위 5개:")
    print(df.nlargest(5, 'rsi_14')[['date', 'close', 'rsi_14']])

    print("\nRSI 극값 하위 5개:")
    print(df.nsmallest(5, 'rsi_14')[['date', 'close', 'rsi_14']])

    # 3. 매수 조건 평가
    buy_conditions = [
        {'indicator': 'rsi_14', 'operator': '<', 'value': 30}
    ]

    print("\n" + "="*40)
    print("매수 조건 평가")
    print("="*40)

    # 조건 정규화 확인
    normalized = _normalize_conditions(buy_conditions)
    print(f"원본 조건: {buy_conditions}")
    print(f"정규화된 조건: {normalized}")

    # 조건 평가
    buy_signal = evaluate_conditions(df, buy_conditions, 'buy')

    print(f"\n매수 신호 생성: {buy_signal.sum()}개")

    if buy_signal.sum() > 0:
        print("매수 신호 발생 시점:")
        buy_dates = df[buy_signal == 1][['date', 'close', 'rsi_14']]
        print(buy_dates)

    # 4. 매도 조건 평가
    sell_conditions = [
        {'indicator': 'rsi_14', 'operator': '>', 'value': 70}
    ]

    print("\n" + "="*40)
    print("매도 조건 평가")
    print("="*40)

    sell_signal = evaluate_conditions(df, sell_conditions, 'sell')

    print(f"매도 신호 생성: {abs(sell_signal.sum())}개")

    if sell_signal.sum() != 0:
        print("매도 신호 발생 시점:")
        sell_dates = df[sell_signal == -1][['date', 'close', 'rsi_14']]
        print(sell_dates)

    # 5. 조건 만족 여부 직접 확인
    print("\n" + "="*40)
    print("직접 조건 확인")
    print("="*40)

    # RSI < 30인 모든 시점
    rsi_low = df['rsi_14'] < 30
    print(f"RSI < 30 조건 만족: {rsi_low.sum()}개")

    # RSI > 70인 모든 시점
    rsi_high = df['rsi_14'] > 70
    print(f"RSI > 70 조건 만족: {rsi_high.sum()}개")

    # 신호는 조건을 처음 만족할 때만 발생 (진입 시점)
    # 즉, 이전에는 조건 불만족, 현재는 만족
    buy_entry = rsi_low & ~rsi_low.shift(1).fillna(False)
    sell_entry = rsi_high & ~rsi_high.shift(1).fillna(False)

    print(f"\n실제 매수 진입점: {buy_entry.sum()}개")
    print(f"실제 매도 진입점: {sell_entry.sum()}개")

    # 6. 문제 진단
    print("\n" + "="*40)
    print("문제 진단")
    print("="*40)

    if buy_signal.sum() == 0 and rsi_low.sum() > 0:
        print("❌ RSI < 30 조건은 만족하지만 신호가 생성되지 않음")
        print("   -> 신호 생성 로직 문제 (진입 시점 감지)")

        # 상세 분석
        for i in range(len(df)):
            if rsi_low.iloc[i]:
                prev_rsi = df['rsi_14'].iloc[i-1] if i > 0 else np.nan
                curr_rsi = df['rsi_14'].iloc[i]
                print(f"   {df['date'].iloc[i]}: RSI {prev_rsi:.2f} -> {curr_rsi:.2f}")
                if i > 0 and not rsi_low.iloc[i-1]:
                    print(f"     => 진입 시점! 신호가 생성되어야 함")

    elif buy_signal.sum() == 0 and rsi_low.sum() == 0:
        print("❌ RSI가 30 아래로 내려가지 않음")
        print("   -> 데이터 또는 RSI 계산 문제")

    else:
        print("✅ 신호가 정상적으로 생성됨")

    # 7. 실제 데이터로 테스트
    print("\n" + "="*60)
    print("실제 데이터 테스트 (필요시)")
    print("="*60)

    return df, buy_signal, sell_signal


def check_indicator_columns(df: pd.DataFrame):
    """데이터프레임의 지표 컬럼 확인"""
    print("\n사용 가능한 컬럼:")
    print("-" * 40)

    # 가격 관련
    price_cols = [col for col in df.columns if col in ['open', 'high', 'low', 'close', 'volume', 'price']]
    if price_cols:
        print("가격 데이터:", price_cols)

    # RSI 관련
    rsi_cols = [col for col in df.columns if 'rsi' in col.lower()]
    if rsi_cols:
        print("RSI 지표:", rsi_cols)

    # 이동평균 관련
    ma_cols = [col for col in df.columns if any(x in col.lower() for x in ['sma', 'ema', 'ma_'])]
    if ma_cols:
        print("이동평균:", ma_cols)

    # MACD 관련
    macd_cols = [col for col in df.columns if 'macd' in col.lower()]
    if macd_cols:
        print("MACD:", macd_cols)

    # 볼린저밴드 관련
    bb_cols = [col for col in df.columns if 'bb' in col.lower()]
    if bb_cols:
        print("볼린저밴드:", bb_cols)

    # 기타
    other_cols = [col for col in df.columns if not any([
        col in price_cols,
        col in rsi_cols,
        col in ma_cols,
        col in macd_cols,
        col in bb_cols,
        col in ['date', 'buy_signal', 'sell_signal']
    ])]
    if other_cols:
        print("기타:", other_cols)


def test_simple_condition():
    """가장 단순한 조건 테스트"""
    print("\n" + "="*60)
    print("단순 조건 테스트")
    print("="*60)

    # 단순 데이터
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'close': [100, 90, 80, 70, 60, 70, 80, 90, 100, 110],
        'open': [100, 90, 80, 70, 60, 70, 80, 90, 100, 110],
        'high': [100, 90, 80, 70, 60, 70, 80, 90, 100, 110],
        'low': [100, 90, 80, 70, 60, 70, 80, 90, 100, 110],
        'volume': [1000] * 10
    })

    # RSI 계산
    config = {'indicators': [{'type': 'RSI', 'params': {'period': 3}}]}
    df = compute_indicators(df, config)

    print("데이터:")
    print(df[['date', 'close', 'rsi_3']])

    # 조건: RSI < 50
    conditions = [{'indicator': 'rsi_3', 'operator': '<', 'value': 50}]
    signal = evaluate_conditions(df, conditions, 'buy')

    print(f"\nRSI < 50 신호: {signal.sum()}개")
    if signal.sum() > 0:
        print("신호 발생:")
        print(df[signal == 1][['date', 'close', 'rsi_3']])


if __name__ == "__main__":
    # 메인 디버깅 실행
    df, buy_signal, sell_signal = debug_rsi_signals()

    # 컬럼 확인
    check_indicator_columns(df)

    # 단순 테스트
    test_simple_condition()

    print("\n" + "="*60)
    print("디버깅 완료")
    print("="*60)