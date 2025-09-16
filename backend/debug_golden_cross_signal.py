"""
골든크로스 신호 디버깅
"""
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kiwoom_bridge'))

# 모듈 임포트
from strategy_engine import strategy_engine

# 골든크로스 전략
golden_cross_strategy = {
    "name": "골든크로스",
    "indicators": [
        {"type": "MA", "period": 20},
        {"type": "MA", "period": 60}
    ],
    "buyConditions": [
        {
            "indicator": "MA_20",
            "operator": "cross_up",
            "value": "MA_60",
            "combineWith": "AND"
        }
    ],
    "sellConditions": [
        {
            "indicator": "MA_20",
            "operator": "cross_down",
            "value": "MA_60",
            "combineWith": "AND"
        }
    ]
}

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

# 수동으로 MA 추가 (크로스 상황 만들기)
df['ma_20'] = 1050
df['ma_60'] = 1060
df['MA_20'] = df['ma_20']  # 대문자 버전
df['MA_60'] = df['ma_60']  # 대문자 버전

# 크로스 상황 만들기: 25일에 골든크로스 발생
df.loc[df.index[23], 'ma_20'] = 1055  # 24일: 아래
df.loc[df.index[23], 'MA_20'] = 1055
df.loc[df.index[24], 'ma_20'] = 1065  # 25일: 위로 (골든크로스)
df.loc[df.index[24], 'MA_20'] = 1065

print("=== 데이터 준비 완료 ===")
print(df[['close', 'ma_20', 'ma_60']].iloc[22:27])

# Core 모듈 상태 확인
print(f"\n=== 모듈 상태 ===")
print(f"strategy_engine.use_core: {strategy_engine.use_core}")

# 신호 컬럼 추가 (Core 모듈이 기대하는 형태)
df['signal'] = 0
df.loc[df.index[24], 'signal'] = 1  # 25일에 매수 신호

# generate_signal 테스트
test_date = df.index[24]  # 골든크로스 발생일
print(f"\n=== {test_date.date()} 신호 테스트 ===")

result = strategy_engine.generate_signal(df, test_date, golden_cross_strategy)

print(f"반환 타입: {type(result)}")
print(f"반환 값: {result}")

if isinstance(result, tuple) and len(result) == 3:
    signal, reason, details = result
    print(f"\n[결과]")
    print(f"신호: {signal}")
    print(f"이유: {reason}")
    print(f"상세: {details}")

    if reason == "매수 신호 발생" or "Core" in reason:
        print("\n⚠️ 문제: 상세 조건이 표시되지 않음!")
        print("기대값: MA_20(1065.00) ↗ MA_60(1060.00)")
    else:
        print("\n✅ 성공: 상세 조건이 표시됨!")

# _format_condition 직접 테스트
print("\n=== _format_condition 직접 테스트 ===")
condition = golden_cross_strategy['buyConditions'][0]
idx = df.index.get_loc(test_date)
try:
    formatted = strategy_engine._format_condition(df, idx, condition)
    print(f"포맷된 조건: {formatted}")
except Exception as e:
    print(f"에러: {e}")

# 컬럼 확인
print("\n=== DataFrame 컬럼 확인 ===")
print(f"컬럼 목록: {df.columns.tolist()}")
print(f"'ma_20' in columns: {'ma_20' in df.columns}")
print(f"'MA_20' in columns: {'MA_20' in df.columns}")
print(f"'ma_60' in columns: {'ma_60' in df.columns}")
print(f"'MA_60' in columns: {'MA_60' in df.columns}")