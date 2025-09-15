"""
rest_api의 strategy_engine 테스트
실제 백테스트 서버가 사용하는 모듈 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# 현재 폴더를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_strategy_engine():
    """strategy_engine 테스트"""

    print("="*60)
    print("REST API Strategy Engine 테스트")
    print("="*60)

    # 1. 임포트 확인
    try:
        from strategy_engine import StrategyEngine
        engine = StrategyEngine()
        print(f"✅ StrategyEngine 임포트 성공")
        print(f"   Core 모듈 사용: {getattr(engine, 'use_core', False)}")
    except ImportError as e:
        print(f"❌ StrategyEngine 임포트 실패: {e}")
        return False

    # 2. 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100)
    prices = []
    base = 50000

    for i in range(100):
        if i < 30:
            base = base * 0.98
        elif i < 70:
            base = base * 1.02
        else:
            base = base * 0.99
        prices.append(base)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })
    df.set_index('date', inplace=True)

    print(f"\n데이터 생성: {len(df)}개")

    # 3. 전략 설정 (두 가지 형식 테스트)
    strategies = [
        {
            "name": "params 구조 (올바른 형식)",
            "config": {
                "indicators": [
                    {"type": "ma", "params": {"period": 5}},
                    {"type": "ma", "params": {"period": 20}}
                ],
                "buyConditions": [
                    {"indicator": "ma_5", "operator": "cross_above", "value": "ma_20"}
                ],
                "sellConditions": [
                    {"indicator": "ma_5", "operator": "cross_below", "value": "ma_20"}
                ]
            }
        },
        {
            "name": "레거시 형식 (params 없음)",
            "config": {
                "indicators": [
                    {"type": "ma", "period": 5},
                    {"type": "ma", "period": 20}
                ],
                "buyConditions": [
                    {"indicator": "ma_5", "operator": ">", "value": "ma_20"}
                ],
                "sellConditions": [
                    {"indicator": "ma_5", "operator": "<", "value": "ma_20"}
                ]
            }
        }
    ]

    # 4. 각 전략 테스트
    for strategy in strategies:
        print(f"\n" + "="*40)
        print(f"테스트: {strategy['name']}")
        print("="*40)

        try:
            # prepare_data 호출
            prepared_df = engine.prepare_data(df.copy(), strategy['config'])

            # 생성된 컬럼 확인
            indicator_cols = [col for col in prepared_df.columns
                            if col not in ['open', 'high', 'low', 'close', 'volume']]
            print(f"생성된 컬럼: {indicator_cols}")

            # 신호 확인
            if 'signal' in prepared_df.columns:
                buy_count = (prepared_df['signal'] == 1).sum()
                sell_count = (prepared_df['signal'] == -1).sum()
                print(f"✅ 신호 생성: 매수 {buy_count}개, 매도 {sell_count}개")
            else:
                print("⚠️  signal 컬럼이 생성되지 않음")

                # generate_signal 테스트
                signal_count = {'buy': 0, 'sell': 0, 'hold': 0}
                for date in df.index[:50]:  # 처음 50개만 테스트
                    signal = engine.generate_signal(prepared_df, date, strategy['config'])
                    signal_count[signal] += 1

                print(f"generate_signal 결과: buy={signal_count['buy']}, sell={signal_count['sell']}, hold={signal_count['hold']}")

        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()

    return True


def check_core_module():
    """Core 모듈 존재 확인"""
    print("\n" + "="*40)
    print("Core 모듈 확인")
    print("="*40)

    # kiwoom_bridge 경로
    kiwoom_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kiwoom_bridge')
    core_path = os.path.join(kiwoom_path, 'core')

    if os.path.exists(core_path):
        print(f"✅ Core 폴더 존재: {core_path}")

        # 필수 파일 확인
        required_files = ['__init__.py', 'naming.py', 'indicators.py', 'signals.py']
        for file in required_files:
            file_path = os.path.join(core_path, file)
            if os.path.exists(file_path):
                print(f"   ✅ {file}")
            else:
                print(f"   ❌ {file} 없음")
    else:
        print(f"❌ Core 폴더 없음: {core_path}")
        print("   => kiwoom_bridge/core/ 폴더를 생성하고 파일을 업로드하세요")


if __name__ == "__main__":
    # Core 모듈 확인
    check_core_module()

    # 테스트 실행
    success = test_strategy_engine()

    print("\n" + "="*60)
    if success:
        print("테스트 완료")
    else:
        print("테스트 실패")
    print("="*60)