"""
UI 설정 상세 테스트 - 더 긴 기간, 완화된 매수 조건
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

async def test_with_relaxed_conditions():
    """
    완화된 조건으로 테스트하여 동적 손절선 동작 확인
    """
    print("\n" + "="*80)
    print("UI 전략 테스트 - 완화된 매수 조건")
    print("="*80)

    engine = BacktestEngine()

    strategy_config = {
        'name': 'UI Config - Relaxed',
        'config': {
            'indicators': [
                {'name': 'rsi', 'params': {'period': 14}},
                {'name': 'sma', 'params': {'period': 20}}
            ],
            'buyConditions': [
                {'left': 'rsi', 'operator': '<', 'right': 45}  # 더 완화
            ],
            'sellConditions': [
                {'left': 'rsi', 'operator': '>', 'right': 75}
            ],
            'targetProfit': {
                'mode': 'staged',
                'staged': {
                    'enabled': True,
                    'stages': [
                        {
                            'stage': 1,
                            'targetProfit': 3,
                            'exitRatio': 50,
                            'dynamicStopLoss': True
                        },
                        {
                            'stage': 2,
                            'targetProfit': 5,
                            'exitRatio': 30,
                            'dynamicStopLoss': True
                        },
                        {
                            'stage': 3,
                            'targetProfit': 10,
                            'exitRatio': 20,
                            'dynamicStopLoss': True
                        }
                    ],
                    'combineWith': 'OR'
                }
            },
            'stopLoss': {
                'enabled': True,
                'value': 3
            },
            'position_size': 0.3
        }
    }

    # 더 긴 기간
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    results = await engine.run_with_config(
        strategy_config=strategy_config['config'],
        stock_codes=['005930'],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    print(f"\n✅ 총 거래 횟수: {results['total_trades']}")
    print(f"✅ 승률: {results['win_rate']:.2f}%")
    print(f"✅ 최종 수익률: {results['total_return']:.2f}%")

    # 매도 분석
    all_trades = results['trades']
    sell_trades = [t for t in all_trades if t['type'] == 'sell']

    stage_1 = [t for t in sell_trades if 'stage_1' in t.get('reason', '')]
    stage_2 = [t for t in sell_trades if 'stage_2' in t.get('reason', '')]
    stage_3 = [t for t in sell_trades if 'stage_3' in t.get('reason', '')]
    stop_loss = [t for t in sell_trades if 'stop_loss' in t.get('reason', '')]
    signal = [t for t in sell_trades if 'Signal' in t.get('reason', '') or ('stage' not in t.get('reason', '') and 'stop_loss' not in t.get('reason', ''))]

    print(f"\n📊 매도 이유별 분석:")
    print(f"  ├─ 1단계 목표 (3% → 50%): {len(stage_1)}건")
    print(f"  ├─ 2단계 목표 (5% → 30%): {len(stage_2)}건")
    print(f"  ├─ 3단계 목표 (10% → 20%): {len(stage_3)}건")
    print(f"  ├─ 손절 (동적 포함): {len(stop_loss)}건")
    print(f"  └─ 시그널 매도: {len(signal)}건")

    # 매도 상세 분석
    print(f"\n📋 매도 거래 상세:")
    for i, trade in enumerate(sell_trades[:20], 1):  # 최대 20건
        print(f"\n  [{i}] {trade['date']}")
        print(f"      수익률: {trade['profit_rate']:.2f}%")
        print(f"      매도비율: {trade.get('exit_ratio', 100)}%")
        print(f"      수량: {trade['quantity']:,}주")
        print(f"      이유: {trade['reason']}")
        print(f"      손익: {trade['profit']:,.0f}원")

    # 동적 손절선 효과 분석
    print(f"\n🔍 동적 손절선 효과 분석:")
    if stop_loss:
        for trade in stop_loss:
            print(f"  - {trade['date']}: {trade['profit_rate']:.2f}% 손절")
            print(f"    (손절 이유: {trade['reason']})")

    return results


async def test_simple_vs_staged():
    """
    단순 목표 vs 단계별 목표 비교
    """
    print("\n" + "="*80)
    print("비교 테스트: 단순 목표 vs 단계별 목표")
    print("="*80)

    engine = BacktestEngine()

    # 단순 목표 (5%)
    simple_config = {
        'indicators': [{'name': 'rsi', 'params': {'period': 14}}],
        'buyConditions': [{'left': 'rsi', 'operator': '<', 'right': 45}],
        'sellConditions': [{'left': 'rsi', 'operator': '>', 'right': 75}],
        'targetProfit': {
            'mode': 'simple',
            'simple': {
                'enabled': True,
                'value': 5.0,
                'combineWith': 'OR'
            }
        },
        'stopLoss': {'enabled': True, 'value': 3},
        'position_size': 0.3
    }

    # 단계별 목표
    staged_config = {
        'indicators': [{'name': 'rsi', 'params': {'period': 14}}],
        'buyConditions': [{'left': 'rsi', 'operator': '<', 'right': 45}],
        'sellConditions': [{'left': 'rsi', 'operator': '>', 'right': 75}],
        'targetProfit': {
            'mode': 'staged',
            'staged': {
                'enabled': True,
                'stages': [
                    {'stage': 1, 'targetProfit': 3, 'exitRatio': 50, 'dynamicStopLoss': True},
                    {'stage': 2, 'targetProfit': 5, 'exitRatio': 30, 'dynamicStopLoss': True},
                    {'stage': 3, 'targetProfit': 10, 'exitRatio': 20, 'dynamicStopLoss': True}
                ],
                'combineWith': 'OR'
            }
        },
        'stopLoss': {'enabled': True, 'value': 3},
        'position_size': 0.3
    }

    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # 단순 목표 실행
    print("\n📌 단순 목표 (5% 익절) 실행 중...")
    simple_results = await engine.run_with_config(
        strategy_config=simple_config,
        stock_codes=['005930'],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    # 단계별 목표 실행
    print("\n📌 단계별 목표 (3%/5%/10%) 실행 중...")
    staged_results = await engine.run_with_config(
        strategy_config=staged_config,
        stock_codes=['005930'],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    # 결과 비교
    print(f"\n📊 결과 비교:")
    print(f"\n  단순 목표 (5%):")
    print(f"    - 거래 횟수: {simple_results['total_trades']}건")
    print(f"    - 승률: {simple_results['win_rate']:.2f}%")
    print(f"    - 수익률: {simple_results['total_return']:.2f}%")

    print(f"\n  단계별 목표 (3%/5%/10% + 동적 손절):")
    print(f"    - 거래 횟수: {staged_results['total_trades']}건")
    print(f"    - 승률: {staged_results['win_rate']:.2f}%")
    print(f"    - 수익률: {staged_results['total_return']:.2f}%")

    return simple_results, staged_results


async def main():
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║              UI 설정 상세 테스트 - 동적 손절선 포함                        ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")

    # 완화된 조건 테스트
    await test_with_relaxed_conditions()

    # 단순 vs 단계별 비교
    await test_simple_vs_staged()

    print("\n" + "="*80)
    print("✅ 모든 테스트 완료")
    print("="*80)


if __name__ == '__main__':
    asyncio.run(main())
