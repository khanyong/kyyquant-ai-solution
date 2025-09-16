"""
Strategy Engine 신호 이유 테스트
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kiwoom_bridge'))

# Core 모듈 비활성화
os.environ['DISABLE_CORE'] = 'true'

from strategy_engine import strategy_engine

# 테스트 데이터 생성
dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
df = pd.DataFrame({
    'date': dates,
    'open': np.random.uniform(1000, 1100, len(dates)),
    'high': np.random.uniform(1100, 1200, len(dates)),
    'low': np.random.uniform(900, 1000, len(dates)),
    'close': np.random.uniform(1000, 1100, len(dates)),
    'volume': np.random.uniform(100000, 200000, len(dates))
})
df.set_index('date', inplace=True)

# 간단한 전략 설정
strategy_params = {
    'indicators': [
        {'type': 'MA', 'period': 5},
        {'type': 'MA', 'period': 20},
        {'type': 'RSI', 'period': 14}
    ],
    'buyConditions': [
        {
            'indicator': 'MA_5',
            'operator': '>',
            'value': 'MA_20',
            'combineWith': 'AND'
        },
        {
            'indicator': 'RSI_14',
            'operator': '<',
            'value': '30',
            'combineWith': 'AND'
        }
    ],
    'sellConditions': [
        {
            'indicator': 'MA_5',
            'operator': '<',
            'value': 'MA_20',
            'combineWith': 'AND'
        },
        {
            'indicator': 'RSI_14',
            'operator': '>',
            'value': '70',
            'combineWith': 'AND'
        }
    ]
}

# 지표 계산
df = strategy_engine.prepare_data(df, strategy_params)

print("=== 데이터 준비 완료 ===")
print(f"컬럼: {df.columns.tolist()}")
print(f"\n최근 5일 데이터:")
print(df[['close', 'ma_5', 'ma_20', 'rsi_14']].tail())

# 마지막 날짜에 대해 신호 생성 테스트
test_date = df.index[-1]
print(f"\n=== {test_date} 신호 생성 테스트 ===")

# generate_signal 호출
result = strategy_engine.generate_signal(df, test_date, strategy_params)

print(f"\n반환 타입: {type(result)}")
print(f"반환 값: {result}")

if isinstance(result, tuple):
    signal, reason, details = result
    print(f"\n신호: {signal}")
    print(f"이유: {reason}")
    print(f"상세: {details}")
else:
    print(f"\n단일 값 반환: {result}")

# 여러 날짜 테스트
print("\n=== 최근 10일 신호 테스트 ===")
for i in range(-10, 0):
    date = df.index[i]
    result = strategy_engine.generate_signal(df, date, strategy_params)

    if isinstance(result, tuple):
        signal, reason, details = result
        if signal != 'hold':
            print(f"{date.date()}: {signal} - {reason}")
    else:
        if result != 'hold':
            print(f"{date.date()}: {result}")