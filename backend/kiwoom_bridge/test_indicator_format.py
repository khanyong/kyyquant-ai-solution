"""
지표 형식 테스트
params 키 유무에 따른 동작 확인
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Core 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import compute_indicators

def test_indicator_formats():
    """다양한 지표 형식 테스트"""

    # 테스트 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    prices = 70000 + np.random.randn(100) * 1000

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': [1000000] * 100
    })

    print("="*60)
    print("지표 형식 테스트")
    print("="*60)

    # 테스트 1: params 있는 형식 (권장)
    config1 = {
        "indicators": [
            {"type": "MA", "params": {"period": 20}},
            {"type": "MA", "params": {"period": 60}}
        ]
    }

    print("\n[TEST 1] params 있는 형식 (권장)")
    print("Config:", config1)

    try:
        df1 = compute_indicators(df.copy(), config1)
        ma_cols = [col for col in df1.columns if 'ma' in col]
        print("SUCCESS - Generated columns:", ma_cols)
        print("MA20 sample:", df1['ma_20'].iloc[-1] if 'ma_20' in df1.columns else "NOT FOUND")
    except Exception as e:
        print(f"ERROR: {e}")

    # 테스트 2: params 없는 형식 (레거시)
    config2 = {
        "indicators": [
            {"type": "MA", "period": 20},  # params 없음
            {"type": "MA", "period": 60}
        ]
    }

    print("\n[TEST 2] params 없는 형식 (레거시)")
    print("Config:", config2)

    try:
        df2 = compute_indicators(df.copy(), config2)
        ma_cols = [col for col in df2.columns if 'ma' in col]
        print("SUCCESS - Generated columns:", ma_cols)
        print("MA20 sample:", df2['ma_20'].iloc[-1] if 'ma_20' in df2.columns else "NOT FOUND")
    except Exception as e:
        print(f"ERROR: {e}")

    # 테스트 3: 소문자 type
    config3 = {
        "indicators": [
            {"type": "ma", "params": {"period": 20}},  # 소문자
            {"type": "rsi", "params": {"period": 14}}
        ]
    }

    print("\n[TEST 3] 소문자 type")
    print("Config:", config3)

    try:
        df3 = compute_indicators(df.copy(), config3)
        ind_cols = [col for col in df3.columns if 'ma' in col or 'rsi' in col]
        print("SUCCESS - Generated columns:", ind_cols)
    except Exception as e:
        print(f"ERROR: {e}")

    # 테스트 4: 혼합 형식
    config4 = {
        "indicators": [
            {"type": "MA", "params": {"period": 5}},   # 정상
            {"type": "ma", "period": 10},              # 레거시 + 소문자
            {"type": "RSI", "params": {"period": 14}}  # 정상
        ]
    }

    print("\n[TEST 4] 혼합 형식")
    print("Config:", config4)

    try:
        df4 = compute_indicators(df.copy(), config4)
        ind_cols = [col for col in df4.columns if any(x in col for x in ['ma', 'rsi'])]
        print("SUCCESS - Generated columns:", ind_cols)
    except Exception as e:
        print(f"ERROR: {e}")

    print("\n" + "="*60)
    print("결론")
    print("="*60)

    print("""
    1. params 키가 없어도 동작함 (기본값 사용)
    2. type은 대소문자 무관 (내부에서 upper() 처리)
    3. 지표명은 항상 소문자로 생성 (ma_20, rsi_14 등)

    권장 형식:
    {"type": "MA", "params": {"period": 20}}

    하지만 레거시 형식도 지원:
    {"type": "MA", "period": 20}
    """)

if __name__ == "__main__":
    test_indicator_formats()