"""
직접 generate_signal 메서드 테스트
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kiwoom_bridge'))

# 테스트 데이터 생성
dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
df = pd.DataFrame({
    'date': dates,
    'open': [1000 + i*10 for i in range(len(dates))],
    'high': [1100 + i*10 for i in range(len(dates))],
    'low': [900 + i*10 for i in range(len(dates))],
    'close': [1000 + i*10 for i in range(len(dates))],
    'volume': [100000 + i*1000 for i in range(len(dates))]
})
df.set_index('date', inplace=True)

# 수동으로 지표 추가
df['ma_5'] = df['close'].rolling(5).mean()
df['ma_20'] = df['close'].rolling(20).mean()
df['rsi_14'] = 50  # 고정값으로 테스트

# RSI를 변동시켜서 조건 만족 테스트
df.loc[df.index[-5:], 'rsi_14'] = 25  # 마지막 5일은 RSI < 30
df.loc[df.index[-10:-5], 'rsi_14'] = 75  # 그 전 5일은 RSI > 70

print("=== 테스트 데이터 준비 완료 ===")
print(df[['close', 'ma_5', 'ma_20', 'rsi_14']].tail(10))

# strategy_engine의 _format_condition 직접 테스트
from strategy_engine import StrategyEngine

engine = StrategyEngine()
engine.use_core = False  # Core 비활성화

# 전략 파라미터
strategy_params = {
    'buyConditions': [
        {
            'indicator': 'MA_5',
            'operator': '>',
            'value': 'MA_20'
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
            'indicator': 'RSI_14',
            'operator': '>',
            'value': '70'
        }
    ]
}

print("\n=== generate_signal 메서드 테스트 ===")

# 마지막 10일 테스트
for i in range(-10, 0):
    date = df.index[i]

    # generate_signal 호출
    try:
        result = engine.generate_signal(df, date, strategy_params)

        if isinstance(result, tuple) and len(result) == 3:
            signal, reason, details = result
            if signal != 'hold':
                print(f"\n날짜: {date.date()}")
                print(f"  신호: {signal}")
                print(f"  이유: {reason}")
                print(f"  상세: {details}")

                # 실제 값 확인
                idx = df.index.get_loc(date)
                print(f"  MA_5: {df.iloc[idx]['ma_5']:.2f}")
                print(f"  MA_20: {df.iloc[idx]['ma_20']:.2f}")
                print(f"  RSI_14: {df.iloc[idx]['rsi_14']:.2f}")
        else:
            print(f"튜플이 아닌 반환: {result}")

    except Exception as e:
        print(f"에러 발생: {e}")