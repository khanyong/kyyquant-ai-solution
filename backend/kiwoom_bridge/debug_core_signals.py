"""
Core 모듈 신호 생성 디버깅
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core import compute_indicators, evaluate_conditions

# 테스트 데이터 생성
dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
prices = []
base_price = 50000

# 골든크로스 패턴 생성
for i in range(len(dates)):
    if i < 15:
        # 초기: MA20이 MA60보다 아래
        prices.append(base_price - 1000 + i * 50)
    else:
        # 후기: MA20이 MA60을 상향돌파
        prices.append(base_price + 500 + i * 100)

df = pd.DataFrame({
    'date': dates,
    'open': prices,
    'high': [p + 100 for p in prices],
    'low': [p - 100 for p in prices],
    'close': prices,
    'volume': [1000000] * len(dates)
})

print("=== 테스트 데이터 생성 ===")
print(df[['date', 'close']].head(10))
print("...")
print(df[['date', 'close']].tail(10))

# 전략 설정
config = {
    "indicators": [
        {"type": "ma", "params": {"period": 5}},  # 단기 이동평균 (테스트용 짧은 기간)
        {"type": "ma", "params": {"period": 10}}  # 장기 이동평균
    ],
    "buyConditions": [
        {
            "indicator": "ma_5",
            "operator": "cross_above",
            "value": "ma_10",
            "combineWith": "AND"
        }
    ],
    "sellConditions": [
        {
            "indicator": "ma_5",
            "operator": "cross_below",
            "value": "ma_10",
            "combineWith": "AND"
        }
    ]
}

# 지표 계산
print("\n=== 지표 계산 ===")
df_with_indicators = compute_indicators(df.copy(), config)
print(f"계산된 컬럼: {df_with_indicators.columns.tolist()}")

# MA 값 확인
if 'ma_5' in df_with_indicators.columns and 'ma_10' in df_with_indicators.columns:
    print("\n=== MA 값 확인 (중간 부분) ===")
    for i in range(10, 20):
        ma5 = df_with_indicators.iloc[i]['ma_5']
        ma10 = df_with_indicators.iloc[i]['ma_10']
        print(f"날짜 {i}: MA5={ma5:.0f}, MA10={ma10:.0f}, 차이={ma5-ma10:.0f}")

# 신호 평가
print("\n=== 신호 평가 ===")
buy_conditions = config.get('buyConditions', [])
sell_conditions = config.get('sellConditions', [])

df_with_signals = evaluate_conditions(df_with_indicators, buy_conditions, sell_conditions)

# 신호 확인
if 'buy_signal' in df_with_signals.columns:
    buy_signals = df_with_signals[df_with_signals['buy_signal'] == 1]
    print(f"매수 신호: {len(buy_signals)}개")
    if len(buy_signals) > 0:
        print("매수 신호 날짜:")
        for idx, row in buy_signals.iterrows():
            print(f"  - {row['date']}: MA5={row['ma_5']:.0f}, MA10={row['ma_10']:.0f}")
else:
    print("buy_signal 컬럼이 없습니다!")

if 'sell_signal' in df_with_signals.columns:
    sell_signals = df_with_signals[df_with_signals['sell_signal'] == -1]
    print(f"매도 신호: {len(sell_signals)}개")
else:
    print("sell_signal 컬럼이 없습니다!")

# 수동으로 크로스 확인
print("\n=== 수동 크로스 확인 ===")
for i in range(1, len(df_with_indicators)):
    curr_ma5 = df_with_indicators.iloc[i]['ma_5']
    curr_ma10 = df_with_indicators.iloc[i]['ma_10']
    prev_ma5 = df_with_indicators.iloc[i-1]['ma_5']
    prev_ma10 = df_with_indicators.iloc[i-1]['ma_10']

    # 골든크로스 체크
    if prev_ma5 <= prev_ma10 and curr_ma5 > curr_ma10:
        print(f"골든크로스 발견! 날짜: {df_with_indicators.iloc[i]['date']}")
        print(f"  어제: MA5={prev_ma5:.0f} <= MA10={prev_ma10:.0f}")
        print(f"  오늘: MA5={curr_ma5:.0f} > MA10={curr_ma10:.0f}")

    # 데드크로스 체크
    if prev_ma5 >= prev_ma10 and curr_ma5 < curr_ma10:
        print(f"데드크로스 발견! 날짜: {df_with_indicators.iloc[i]['date']}")
        print(f"  어제: MA5={prev_ma5:.0f} >= MA10={prev_ma10:.0f}")
        print(f"  오늘: MA5={curr_ma5:.0f} < MA10={curr_ma10:.0f}")