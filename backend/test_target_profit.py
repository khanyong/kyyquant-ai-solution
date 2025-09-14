"""목표 수익률 기능 테스트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kiwoom_bridge.backtest_engine_advanced import AdvancedBacktestEngine, SignalGenerator

def create_test_data():
    """테스트용 주가 데이터 생성"""
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)

    # 상승 추세 데이터 생성
    base_price = 10000
    prices = []
    for i in range(len(dates)):
        # 전체적으로 상승 추세 (약 20% 상승)
        trend = base_price * (1 + 0.002 * i)
        # 일일 변동성 추가
        noise = np.random.normal(0, 50)
        prices.append(trend + noise)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, len(dates))
    })

    # RSI 계산 (간단한 버전)
    df['RSI_14'] = 50 + np.random.normal(0, 20, len(dates))
    df['RSI_14'] = df['RSI_14'].clip(0, 100)

    return df

def test_backward_compatibility():
    """기존 전략 하위 호환성 테스트"""
    print("\n=== 하위 호환성 테스트 ===")

    # 기존 전략 (targetProfit 없음)
    old_strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 30}
        ],
        'sellConditions': [
            {'indicator': 'RSI_14', 'operator': '>', 'value': 70}
        ]
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    try:
        result = engine.run(data, old_strategy)
        print("✅ 기존 전략 실행 성공")
        print(f"   총 거래: {result['total_trades']}회")
        print(f"   수익률: {result['total_return']:.2f}%")
    except Exception as e:
        print(f"❌ 기존 전략 실행 실패: {e}")

def test_target_profit_only():
    """목표 수익률만 있는 전략 테스트"""
    print("\n=== 목표 수익률 전략 테스트 ===")

    # 목표 수익률만 설정 (지표 조건 없음)
    strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [],  # 지표 조건 없음
        'targetProfit': {
            'enabled': True,
            'value': 5.0,  # 5% 수익 시 매도
            'combineWith': 'OR'
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy)
    print(f"✅ 목표 수익률 5% 전략")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")
    print(f"   승률: {result['win_rate']:.2f}%")

def test_combined_strategy():
    """지표 + 목표 수익률 결합 전략 테스트"""
    print("\n=== 결합 전략 테스트 (OR) ===")

    # RSI > 70 OR 수익률 3% 시 매도
    strategy_or = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 35}
        ],
        'sellConditions': [
            {'indicator': 'RSI_14', 'operator': '>', 'value': 70}
        ],
        'targetProfit': {
            'enabled': True,
            'value': 3.0,  # 3% 수익
            'combineWith': 'OR'
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy_or)
    print(f"✅ OR 조건 (RSI>70 또는 수익 3%)")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")
    print(f"   승률: {result['win_rate']:.2f}%")

    print("\n=== 결합 전략 테스트 (AND) ===")

    # RSI > 65 AND 수익률 3% 시 매도
    strategy_and = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 35}
        ],
        'sellConditions': [
            {'indicator': 'RSI_14', 'operator': '>', 'value': 65}
        ],
        'targetProfit': {
            'enabled': True,
            'value': 3.0,  # 3% 수익
            'combineWith': 'AND'
        }
    }

    engine2 = AdvancedBacktestEngine(initial_capital=1000000)
    result2 = engine2.run(data, strategy_and)
    print(f"✅ AND 조건 (RSI>65 그리고 수익 3%)")
    print(f"   총 거래: {result2['total_trades']}회")
    print(f"   수익률: {result2['total_return']:.2f}%")
    print(f"   승률: {result2['win_rate']:.2f}%")

def test_stop_loss():
    """손절 기능 테스트"""
    print("\n=== 손절 기능 테스트 ===")

    strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [
            {'indicator': 'RSI_14', 'operator': '>', 'value': 70}
        ],
        'targetProfit': {
            'enabled': True,
            'value': 5.0,
            'combineWith': 'OR'
        },
        'stopLoss': {
            'enabled': True,
            'value': 2.0  # -2% 손절
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy)
    print(f"✅ 목표 수익 5%, 손절 -2%")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")
    print(f"   승률: {result['win_rate']:.2f}%")

if __name__ == "__main__":
    print("=" * 50)
    print("목표 수익률 기능 테스트 시작")
    print("=" * 50)

    test_backward_compatibility()
    test_target_profit_only()
    test_combined_strategy()
    test_stop_loss()

    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("=" * 50)