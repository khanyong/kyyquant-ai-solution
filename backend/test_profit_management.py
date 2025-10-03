"""
백테스트 엔진의 목표수익률 및 손절 기능 테스트
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
from dotenv import load_dotenv
load_dotenv()

from backtest.engine import BacktestEngine
from datetime import datetime, timedelta
import asyncio

async def test_simple_target_profit():
    """테스트 1: 단순 목표 수익률 (5% 익절)"""
    print("\n" + "="*80)
    print("테스트 1: 단순 목표 수익률 (5% 익절)")
    print("="*80)

    engine = BacktestEngine()

    # 전략 설정
    strategy_config = {
        'name': 'Test Target Profit',
        'config': {
            'indicators': [
                {'name': 'rsi', 'params': {'period': 14}}
            ],
            'buyConditions': [
                {'left': 'rsi', 'operator': '<', 'right': 30}
            ],
            'sellConditions': [
                {'left': 'rsi', 'operator': '>', 'right': 70}
            ],
            'targetProfit': {
                'mode': 'simple',
                'simple': {
                    'enabled': True,
                    'value': 5.0,  # 5% 익절
                    'combineWith': 'OR'
                }
            },
            'stopLoss': {
                'enabled': False
            },
            'position_size': 0.3
        }
    }

    # 백테스트 실행
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    results = await engine.run_with_config(
        strategy_config=strategy_config['config'],
        stock_codes=['005930'],  # 삼성전자
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    print(f"\n✅ 총 거래 횟수: {results['total_trades']}")
    print(f"✅ 승률: {results['win_rate']:.2f}%")
    print(f"✅ 최종 수익률: {results['total_return']:.2f}%")

    # 익절로 매도된 거래 확인
    target_profit_trades = [t for t in results['trades'] if t['type'] == 'sell' and 'target_profit' in t.get('reason', '')]
    print(f"\n📊 목표수익률 도달 매도: {len(target_profit_trades)}건")

    for i, trade in enumerate(target_profit_trades[:3], 1):
        print(f"  {i}. 날짜: {trade['date']}, 수익률: {trade['profit_rate']:.2f}%, 이유: {trade['reason']}")

    return results


async def test_stop_loss():
    """테스트 2: 손절 (-3%)"""
    print("\n" + "="*80)
    print("테스트 2: 손절 (-3%)")
    print("="*80)

    engine = BacktestEngine()

    # 전략 설정
    strategy_config = {
        'name': 'Test Stop Loss',
        'config': {
            'indicators': [
                {'name': 'rsi', 'params': {'period': 14}}
            ],
            'buyConditions': [
                {'left': 'rsi', 'operator': '<', 'right': 50}
            ],
            'sellConditions': [
                {'left': 'rsi', 'operator': '>', 'right': 70}
            ],
            'targetProfit': {
                'mode': 'simple',
                'simple': {
                    'enabled': False
                }
            },
            'stopLoss': {
                'enabled': True,
                'value': -3.0  # -3% 손절
            },
            'position_size': 0.3
        }
    }

    # 백테스트 실행
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    results = await engine.run_with_config(
        strategy_config=strategy_config['config'],
        stock_codes=['005930'],  # 삼성전자
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    print(f"\n✅ 총 거래 횟수: {results['total_trades']}")
    print(f"✅ 승률: {results['win_rate']:.2f}%")
    print(f"✅ 최종 수익률: {results['total_return']:.2f}%")

    # 손절로 매도된 거래 확인
    stop_loss_trades = [t for t in results['trades'] if t['type'] == 'sell' and 'stop_loss' in t.get('reason', '')]
    print(f"\n📊 손절 매도: {len(stop_loss_trades)}건")

    for i, trade in enumerate(stop_loss_trades[:3], 1):
        print(f"  {i}. 날짜: {trade['date']}, 수익률: {trade['profit_rate']:.2f}%, 이유: {trade['reason']}")

    return results


async def test_staged_profit():
    """테스트 3: 단계별 목표 수익률"""
    print("\n" + "="*80)
    print("테스트 3: 단계별 목표 수익률 (3%/50%, 5%/30%, 10%/20%)")
    print("="*80)

    engine = BacktestEngine()

    # 전략 설정
    strategy_config = {
        'name': 'Test Staged Profit',
        'config': {
            'indicators': [
                {'name': 'rsi', 'params': {'period': 14}}
            ],
            'buyConditions': [
                {'left': 'rsi', 'operator': '<', 'right': 30}
            ],
            'sellConditions': [
                {'left': 'rsi', 'operator': '>', 'right': 70}
            ],
            'targetProfit': {
                'mode': 'staged',
                'staged': {
                    'enabled': True,
                    'stages': [
                        {'stage': 1, 'targetProfit': 3, 'exitRatio': 50},
                        {'stage': 2, 'targetProfit': 5, 'exitRatio': 30},
                        {'stage': 3, 'targetProfit': 10, 'exitRatio': 20}
                    ],
                    'combineWith': 'OR'
                }
            },
            'stopLoss': {
                'enabled': True,
                'value': -5.0
            },
            'position_size': 0.3
        }
    }

    # 백테스트 실행
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    results = await engine.run_with_config(
        strategy_config=strategy_config['config'],
        stock_codes=['005930'],  # 삼성전자
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    print(f"\n✅ 총 거래 횟수: {results['total_trades']}")
    print(f"✅ 승률: {results['win_rate']:.2f}%")
    print(f"✅ 최종 수익률: {results['total_return']:.2f}%")

    # 단계별 매도 확인
    stage_trades = [t for t in results['trades'] if t['type'] == 'sell' and 'stage_' in t.get('reason', '')]
    print(f"\n📊 단계별 목표 도달 매도: {len(stage_trades)}건")

    for i, trade in enumerate(stage_trades[:5], 1):
        print(f"  {i}. 날짜: {trade['date']}, 수익률: {trade['profit_rate']:.2f}%, 매도비율: {trade.get('exit_ratio', 100)}%, 이유: {trade['reason']}")

    return results


async def test_combined():
    """테스트 4: 목표수익률 + 손절 조합"""
    print("\n" + "="*80)
    print("테스트 4: 목표수익률(5%) + 손절(-3%) 조합")
    print("="*80)

    engine = BacktestEngine()

    # 전략 설정
    strategy_config = {
        'name': 'Test Combined',
        'config': {
            'indicators': [
                {'name': 'rsi', 'params': {'period': 14}}
            ],
            'buyConditions': [
                {'left': 'rsi', 'operator': '<', 'right': 40}
            ],
            'sellConditions': [
                {'left': 'rsi', 'operator': '>', 'right': 70}
            ],
            'targetProfit': {
                'mode': 'simple',
                'simple': {
                    'enabled': True,
                    'value': 5.0,
                    'combineWith': 'OR'
                }
            },
            'stopLoss': {
                'enabled': True,
                'value': -3.0
            },
            'position_size': 0.3
        }
    }

    # 백테스트 실행
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    results = await engine.run_with_config(
        strategy_config=strategy_config['config'],
        stock_codes=['005930'],  # 삼성전자
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    print(f"\n✅ 총 거래 횟수: {results['total_trades']}")
    print(f"✅ 승률: {results['win_rate']:.2f}%")
    print(f"✅ 최종 수익률: {results['total_return']:.2f}%")

    # 매도 이유별 분류
    target_profit_trades = [t for t in results['trades'] if t['type'] == 'sell' and 'target_profit' in t.get('reason', '')]
    stop_loss_trades = [t for t in results['trades'] if t['type'] == 'sell' and 'stop_loss' in t.get('reason', '')]
    signal_trades = [t for t in results['trades'] if t['type'] == 'sell' and 'Signal' in t.get('reason', '')]

    print(f"\n📊 매도 이유별 분류:")
    print(f"  - 목표수익률 도달: {len(target_profit_trades)}건")
    print(f"  - 손절: {len(stop_loss_trades)}건")
    print(f"  - 시그널: {len(signal_trades)}건")

    return results


async def main():
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║          백테스트 엔진 - 목표수익률 및 손절 기능 테스트                    ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")

    # 모든 테스트 실행
    await test_simple_target_profit()
    await test_stop_loss()
    await test_staged_profit()
    await test_combined()

    print("\n" + "="*80)
    print("✅ 모든 테스트 완료")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(main())
