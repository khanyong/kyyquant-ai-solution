"""
골든크로스 전략 테스트
"""
import sys
import os
import json

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'kiwoom_bridge'))

# 골든크로스 전략 예시
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

print("=== 골든크로스 전략 구조 ===")
print(json.dumps(golden_cross_strategy, indent=2, ensure_ascii=False))

# backtest_engine_advanced 테스트
from backtest_engine_advanced import AdvancedBacktestEngine

engine = AdvancedBacktestEngine()

print("\n=== USE_STRATEGY_ENGINE 상태 ===")
from backtest_engine_advanced import USE_STRATEGY_ENGINE, USE_CORE
print(f"USE_STRATEGY_ENGINE: {USE_STRATEGY_ENGINE}")
print(f"USE_CORE: {USE_CORE}")

if USE_STRATEGY_ENGINE:
    print("\n=== strategy_engine 테스트 ===")
    from strategy_engine import strategy_engine
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    # 테스트 데이터 생성
    dates = pd.date_range(start='2024-01-01', end='2024-02-01', freq='D')
    df = pd.DataFrame({
        'date': dates,
        'open': [1000 + i*5 for i in range(len(dates))],
        'high': [1100 + i*5 for i in range(len(dates))],
        'low': [900 + i*5 for i in range(len(dates))],
        'close': [1000 + i*5 for i in range(len(dates))],
        'volume': [100000 + i*100 for i in range(len(dates))]
    })
    df.set_index('date', inplace=True)

    # 지표 계산
    df = strategy_engine.prepare_data(df, golden_cross_strategy)

    print(f"\n계산된 컬럼: {df.columns.tolist()}")
    print(f"\nMA_20 존재: {'ma_20' in df.columns or 'MA_20' in df.columns}")
    print(f"MA_60 존재: {'ma_60' in df.columns or 'MA_60' in df.columns}")

    # 마지막 날짜 신호 테스트
    last_date = df.index[-1]
    result = strategy_engine.generate_signal(df, last_date, golden_cross_strategy)

    print(f"\n=== generate_signal 결과 ===")
    print(f"타입: {type(result)}")
    print(f"값: {result}")

    if isinstance(result, tuple) and len(result) == 3:
        signal, reason, details = result
        print(f"\n신호: {signal}")
        print(f"이유: {reason}")
        print(f"상세: {details}")

    # 크로스 시뮬레이션
    print("\n=== 크로스 시뮬레이션 ===")
    # MA_20이 MA_60을 상향돌파하는 상황 만들기
    df['ma_20'] = 50
    df['ma_60'] = 60
    df.iloc[-2]['ma_20'] = 59  # 어제는 아래
    df.iloc[-1]['ma_20'] = 61  # 오늘은 위

    result = strategy_engine.generate_signal(df, last_date, golden_cross_strategy)
    print(f"크로스 후 결과: {result}")

else:
    print("USE_STRATEGY_ENGINE이 False입니다.")