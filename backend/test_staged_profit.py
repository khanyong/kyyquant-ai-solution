"""단계별 목표 수익률 기능 테스트"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kiwoom_bridge.backtest_engine_advanced import AdvancedBacktestEngine, SignalGenerator

def create_test_data():
    """테스트용 주가 데이터 생성 (상승 추세)"""
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    np.random.seed(42)

    # 강한 상승 추세 데이터 생성 (약 30% 상승)
    base_price = 10000
    prices = []
    for i in range(len(dates)):
        # 전체적으로 상승 추세
        trend = base_price * (1 + 0.003 * i)  # 일 0.3% 상승
        # 일일 변동성 추가
        noise = np.random.normal(0, 30)
        prices.append(trend + noise)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, len(dates))
    })

    # RSI 계산 (간단한 버전)
    df['RSI_14'] = 50 + np.random.normal(0, 15, len(dates))
    df['RSI_14'] = df['RSI_14'].clip(0, 100)

    return df

def test_simple_mode():
    """단일 목표 모드 테스트"""
    print("\n=== 단일 목표 모드 테스트 ===")

    strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [],
        'targetProfit': {
            'mode': 'simple',
            'simple': {
                'enabled': True,
                'value': 5.0,  # 5% 수익 시 전량 매도
                'combineWith': 'OR'
            }
        },
        'stopLoss': {
            'enabled': True,
            'value': 3.0
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy)
    print(f"[OK] 단일 목표 5% 전략")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")
    print(f"   승률: {result['win_rate']:.2f}%")
    print(f"   평균 수익: {result.get('avg_profit', 0):.2f}%")

def test_staged_mode():
    """단계별 목표 모드 테스트"""
    print("\n=== 단계별 목표 모드 테스트 ===")

    strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [],
        'targetProfit': {
            'mode': 'staged',
            'staged': {
                'enabled': True,
                'stages': [
                    {
                        'stage': 1,
                        'targetProfit': 3.0,   # 3% 도달 시
                        'exitRatio': 50,       # 50% 매도
                        'dynamicStopLoss': False
                    },
                    {
                        'stage': 2,
                        'targetProfit': 5.0,   # 5% 도달 시
                        'exitRatio': 30,       # 30% 매도
                        'dynamicStopLoss': True  # 손절선을 3%로 상향
                    },
                    {
                        'stage': 3,
                        'targetProfit': 10.0,  # 10% 도달 시
                        'exitRatio': 20,       # 20% 매도 (남은 전량)
                        'dynamicStopLoss': True  # 손절선을 5%로 상향
                    }
                ],
                'combineWith': 'OR'
            }
        },
        'stopLoss': {
            'enabled': True,
            'value': 3.0
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy)
    print(f"[OK] 단계별 목표 (3% → 50%, 5% → 30%, 10% → 20%)")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")
    print(f"   승률: {result['win_rate']:.2f}%")
    print(f"   평균 수익: {result.get('avg_profit', 0):.2f}%")

def test_dynamic_stop_loss():
    """동적 손절 테스트"""
    print("\n=== 동적 손절 (Break Even) 테스트 ===")

    strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [],
        'targetProfit': {
            'mode': 'staged',
            'staged': {
                'enabled': True,
                'stages': [
                    {
                        'stage': 1,
                        'targetProfit': 3.0,
                        'exitRatio': 30,
                        'dynamicStopLoss': True  # 3% 도달 시 손절을 본전으로
                    },
                    {
                        'stage': 2,
                        'targetProfit': 5.0,
                        'exitRatio': 30,
                        'dynamicStopLoss': True  # 5% 도달 시 손절을 3%로
                    },
                    {
                        'stage': 3,
                        'targetProfit': 8.0,
                        'exitRatio': 40,
                        'dynamicStopLoss': True  # 8% 도달 시 손절을 5%로
                    }
                ],
                'combineWith': 'OR'
            }
        },
        'stopLoss': {
            'enabled': True,
            'value': 2.0,  # 초기 손절 -2%
            'breakEven': True  # 동적 손절 활성화
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy)
    print(f"[OK] 동적 손절 전략")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")
    print(f"   승률: {result['win_rate']:.2f}%")
    print(f"   최대 손실: {result.get('max_loss', 0):.2f}%")

def test_trailing_stop():
    """트레일링 스톱 테스트"""
    print("\n=== 트레일링 스톱 테스트 ===")

    strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [],
        'targetProfit': {
            'mode': 'simple',
            'simple': {
                'enabled': True,
                'value': 15.0,  # 15% 목표
                'combineWith': 'OR'
            }
        },
        'stopLoss': {
            'enabled': True,
            'value': 3.0,
            'trailingStop': {
                'enabled': True,
                'activation': 5.0,  # 5% 수익 시 활성화
                'distance': 2.0     # 최고점 대비 2% 하락 시 매도
            }
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy)
    print(f"[OK] 트레일링 스톱 (5% 수익 후 2% 하락 시 매도)")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")
    print(f"   승률: {result['win_rate']:.2f}%")
    print(f"   평균 보유 기간: {result.get('avg_holding_days', 0):.1f}일")

def test_combined_with_indicators():
    """지표 조건과 결합 테스트"""
    print("\n=== 지표 조건과 AND 결합 테스트 ===")

    # AND 조건: RSI > 70 그리고 5% 수익
    strategy_and = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 35}
        ],
        'sellConditions': [
            {'indicator': 'RSI_14', 'operator': '>', 'value': 70}
        ],
        'targetProfit': {
            'mode': 'simple',
            'simple': {
                'enabled': True,
                'value': 5.0,
                'combineWith': 'AND'  # RSI > 70 AND 수익 5%
            }
        }
    }

    data = create_test_data()
    engine = AdvancedBacktestEngine(initial_capital=1000000)

    result = engine.run(data, strategy_and)
    print(f"[OK] AND 조건 (RSI > 70 그리고 수익 5%)")
    print(f"   총 거래: {result['total_trades']}회")
    print(f"   수익률: {result['total_return']:.2f}%")

    print("\n=== 지표 조건과 OR 결합 테스트 ===")

    # OR 조건: RSI > 65 또는 5% 수익
    strategy_or = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 35}
        ],
        'sellConditions': [
            {'indicator': 'RSI_14', 'operator': '>', 'value': 65}
        ],
        'targetProfit': {
            'mode': 'simple',
            'simple': {
                'enabled': True,
                'value': 5.0,
                'combineWith': 'OR'  # RSI > 65 OR 수익 5%
            }
        }
    }

    engine2 = AdvancedBacktestEngine(initial_capital=1000000)
    result2 = engine2.run(data, strategy_or)
    print(f"[OK] OR 조건 (RSI > 65 또는 수익 5%)")
    print(f"   총 거래: {result2['total_trades']}회")
    print(f"   수익률: {result2['total_return']:.2f}%")

def compare_modes():
    """단일 vs 단계별 모드 비교"""
    print("\n=== 단일 vs 단계별 모드 성능 비교 ===")

    data = create_test_data()

    # 단일 목표 전략
    simple_strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [],
        'targetProfit': {
            'mode': 'simple',
            'simple': {
                'enabled': True,
                'value': 7.0,
                'combineWith': 'OR'
            }
        }
    }

    # 단계별 목표 전략
    staged_strategy = {
        'buyConditions': [
            {'indicator': 'RSI_14', 'operator': '<', 'value': 40}
        ],
        'sellConditions': [],
        'targetProfit': {
            'mode': 'staged',
            'staged': {
                'enabled': True,
                'stages': [
                    {'stage': 1, 'targetProfit': 3.0, 'exitRatio': 40, 'dynamicStopLoss': False},
                    {'stage': 2, 'targetProfit': 5.0, 'exitRatio': 30, 'dynamicStopLoss': True},
                    {'stage': 3, 'targetProfit': 7.0, 'exitRatio': 30, 'dynamicStopLoss': True}
                ],
                'combineWith': 'OR'
            }
        }
    }

    # 단일 목표 실행
    engine1 = AdvancedBacktestEngine(initial_capital=1000000)
    result1 = engine1.run(data, simple_strategy)

    # 단계별 목표 실행
    engine2 = AdvancedBacktestEngine(initial_capital=1000000)
    result2 = engine2.run(data, staged_strategy)

    print("[COMPARE] 비교 결과:")
    print("-" * 60)
    print(f"{'Item':<20} | {'Simple Mode':>15} | {'Staged Mode':>15}")
    print("-" * 60)
    print(f"{'Total Trades':<20} | {result1['total_trades']:>15} | {result2['total_trades']:>15}")
    print(f"{'Total Return (%)':<20} | {result1['total_return']:>14.2f}% | {result2['total_return']:>14.2f}%")
    print(f"{'Win Rate (%)':<20} | {result1['win_rate']:>14.2f}% | {result2['win_rate']:>14.2f}%")
    print(f"{'Max Drawdown (%)':<20} | {result1.get('max_drawdown', 0):>14.2f}% | {result2.get('max_drawdown', 0):>14.2f}%")
    print("-" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("단계별 목표 수익률 기능 테스트 시작")
    print("=" * 60)

    test_simple_mode()
    test_staged_mode()
    test_dynamic_stop_loss()
    test_trailing_stop()
    test_combined_with_indicators()
    compare_modes()

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)