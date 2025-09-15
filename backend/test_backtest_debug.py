import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
from datetime import datetime, timedelta
from rest_api.strategy_engine import StrategyEngine

async def test_indicator_naming():
    """지표 명명 규칙 테스트"""

    # 테스트 전략 설정
    strategy_config = {
        "name": "테스트 전략",
        "indicators": [
            {"type": "ma", "period": 20},
            {"type": "rsi", "period": 14},
            {"type": "macd", "fast": 12, "slow": 26, "signal": 9}
        ],
        "buyConditions": [
            {
                "indicator": "rsi_14",
                "operator": "<",
                "value": 30,
                "combineWith": None
            },
            {
                "indicator": "close",
                "operator": ">",
                "value": "ma_20",
                "combineWith": "AND"
            }
        ],
        "sellConditions": [
            {
                "indicator": "rsi_14",
                "operator": ">",
                "value": 70,
                "combineWith": None
            }
        ]
    }

    # StrategyEngine 초기화
    engine = StrategyEngine()

    # 샘플 데이터로 테스트
    print("=== 지표 명명 규칙 테스트 ===")
    print(f"전략 설정: {json.dumps(strategy_config, indent=2, ensure_ascii=False)}")

    # prepare_data 호출 시 생성되는 컬럼 확인
    import pandas as pd
    import numpy as np

    # 샘플 데이터 생성
    dates = pd.date_range(start='2024-01-01', end='2024-03-01', freq='D')
    sample_data = pd.DataFrame({
        'date': dates,
        'open': np.random.uniform(100, 110, len(dates)),
        'high': np.random.uniform(110, 120, len(dates)),
        'low': np.random.uniform(90, 100, len(dates)),
        'close': np.random.uniform(95, 115, len(dates)),
        'volume': np.random.uniform(1000000, 2000000, len(dates))
    })

    # prepare_data 실행
    prepared_data = engine.prepare_data(sample_data, strategy_config)

    print("\n=== 생성된 컬럼 목록 ===")
    indicator_columns = [col for col in prepared_data.columns if col not in ['date', 'open', 'high', 'low', 'close', 'volume']]
    for col in indicator_columns:
        print(f"  - {col}")

    print("\n=== 조건에서 사용하는 지표 ===")
    for cond in strategy_config['buyConditions']:
        indicator = cond['indicator']
        value = cond['value']
        print(f"  매수 조건: {indicator} (존재: {indicator in prepared_data.columns})")
        if isinstance(value, str):
            print(f"    비교 값: {value} (존재: {value in prepared_data.columns})")

    for cond in strategy_config['sellConditions']:
        indicator = cond['indicator']
        print(f"  매도 조건: {indicator} (존재: {indicator in prepared_data.columns})")

    # 백테스트 엔진에서 사용할 컬럼명 매핑 확인
    print("\n=== 권장 수정사항 ===")
    missing_columns = []
    for cond in strategy_config['buyConditions'] + strategy_config['sellConditions']:
        indicator = cond['indicator']
        if indicator not in prepared_data.columns and indicator not in ['close', 'open', 'high', 'low', 'volume']:
            missing_columns.append(indicator)

        value = cond.get('value')
        if isinstance(value, str) and value not in prepared_data.columns:
            missing_columns.append(value)

    if missing_columns:
        print(f"  누락된 컬럼: {missing_columns}")
        print("\n  해결 방법:")
        for col in missing_columns:
            if 'rsi' in col.lower():
                print(f"    - '{col}' → 'rsi' 또는 'rsi_14'로 변경")
            elif 'ma' in col.lower():
                period = col.split('_')[-1] if '_' in col else '20'
                print(f"    - '{col}' → 'ma_{period}' 또는 'sma_{period}'로 변경")
    else:
        print("  모든 지표가 올바르게 매핑되어 있습니다.")

if __name__ == "__main__":
    asyncio.run(test_indicator_naming())