"""
분할 매수 (Staged Buy) 기능 테스트
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

async def test_staged_buy_basic():
    """
    기본 분할 매수 테스트
    - 1단계: RSI < 35, 50% 투자
    - 2단계: RSI < 30, 30% 추가 투자 (총 65%)
    - 3단계: RSI < 25, 20% 추가 투자 (총 78%)
    """
    print("\n" + "="*80)
    print("기본 분할 매수 테스트")
    print("="*80)

    engine = BacktestEngine()

    # 분할 매수 전략
    strategy_config = {
        'name': 'Staged Buy Test',
        'config': {
            'indicators': [
                {'name': 'rsi', 'params': {'period': 14}}
            ],
            'useStageBasedStrategy': True,
            'buyStageStrategy': {
                'stages': [
                    {
                        'stage': 1,
                        'enabled': True,
                        'positionPercent': 50,  # 50% 투자
                        'passAllRequired': True,
                        'conditions': [
                            {'left': 'rsi', 'operator': '<', 'right': 35}
                        ]
                    },
                    {
                        'stage': 2,
                        'enabled': True,
                        'positionPercent': 30,  # 남은 금액의 30%
                        'passAllRequired': True,
                        'conditions': [
                            {'left': 'rsi', 'operator': '<', 'right': 30}
                        ]
                    },
                    {
                        'stage': 3,
                        'enabled': True,
                        'positionPercent': 20,  # 남은 금액의 20%
                        'passAllRequired': True,
                        'conditions': [
                            {'left': 'rsi', 'operator': '<', 'right': 25}
                        ]
                    }
                ]
            },
            'sellStageStrategy': {
                'stages': [
                    {
                        'stage': 1,
                        'enabled': True,
                        'positionPercent': 100,
                        'passAllRequired': False,
                        'conditions': [
                            {'left': 'rsi', 'operator': '>', 'right': 70}
                        ]
                    }
                ]
            },
            'targetProfit': {
                'mode': 'staged',
                'staged': {
                    'enabled': True,
                    'stages': [
                        {'stage': 1, 'targetProfit': 3, 'exitRatio': 50, 'dynamicStopLoss': True},
                        {'stage': 2, 'targetProfit': 5, 'exitRatio': 30, 'dynamicStopLoss': True},
                        {'stage': 3, 'targetProfit': 10, 'exitRatio': 20, 'dynamicStopLoss': True}
                    ]
                }
            },
            'stopLoss': {
                'enabled': True,
                'value': 3
            }
        }
    }

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

    # 매수 거래 분석
    buy_trades = [t for t in results['trades'] if t['type'] == 'buy']
    stage_1_buys = [t for t in buy_trades if 'stage_1' in t.get('reason', '')]
    stage_2_buys = [t for t in buy_trades if 'stage_2' in t.get('reason', '')]
    stage_3_buys = [t for t in buy_trades if 'stage_3' in t.get('reason', '')]

    print(f"\n📊 매수 분석:")
    print(f"  ├─ 1단계 매수 (RSI < 35, 50%): {len(stage_1_buys)}건")
    print(f"  ├─ 2단계 매수 (RSI < 30, 30%): {len(stage_2_buys)}건")
    print(f"  └─ 3단계 매수 (RSI < 25, 20%): {len(stage_3_buys)}건")

    # 매수 상세 내역
    print(f"\n📋 매수 거래 상세:")
    for i, trade in enumerate(buy_trades[:10], 1):
        print(f"\n  [{i}] {trade['date']}")
        print(f"      금액: {trade['amount']:,.0f}원")
        print(f"      수량: {trade['quantity']:,}주")
        print(f"      이유: {trade['reason']}")

    return results


async def test_comparison_single_vs_staged():
    """
    단일 매수 vs 분할 매수 비교
    """
    print("\n" + "="*80)
    print("비교 테스트: 단일 매수 vs 분할 매수")
    print("="*80)

    engine = BacktestEngine()

    # 단일 매수 전략
    single_config = {
        'indicators': [{'name': 'rsi', 'params': {'period': 14}}],
        'buyConditions': [{'left': 'rsi', 'operator': '<', 'right': 30}],
        'sellConditions': [{'left': 'rsi', 'operator': '>', 'right': 70}],
        'targetProfit': {
            'mode': 'simple',
            'simple': {'enabled': True, 'value': 5.0}
        },
        'stopLoss': {'enabled': True, 'value': 3},
        'position_size': 0.5  # 50% 일괄 투자
    }

    # 분할 매수 전략
    staged_config = {
        'indicators': [{'name': 'rsi', 'params': {'period': 14}}],
        'useStageBasedStrategy': True,
        'buyStageStrategy': {
            'stages': [
                {
                    'stage': 1,
                    'enabled': True,
                    'positionPercent': 30,
                    'passAllRequired': True,
                    'conditions': [{'left': 'rsi', 'operator': '<', 'right': 35}]
                },
                {
                    'stage': 2,
                    'enabled': True,
                    'positionPercent': 50,
                    'passAllRequired': True,
                    'conditions': [{'left': 'rsi', 'operator': '<', 'right': 28}]
                }
            ]
        },
        'sellStageStrategy': {
            'stages': [
                {
                    'stage': 1,
                    'enabled': True,
                    'positionPercent': 100,
                    'passAllRequired': False,
                    'conditions': [{'left': 'rsi', 'operator': '>', 'right': 70}]
                }
            ]
        },
        'targetProfit': {
            'mode': 'simple',
            'simple': {'enabled': True, 'value': 5.0}
        },
        'stopLoss': {'enabled': True, 'value': 3}
    }

    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # 단일 매수 실행
    print("\n📌 단일 매수 전략 실행 중...")
    single_results = await engine.run_with_config(
        strategy_config=single_config,
        stock_codes=['005930'],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    # 분할 매수 실행
    print("\n📌 분할 매수 전략 실행 중...")
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
    print(f"\n  단일 매수 (RSI < 30, 50% 일괄):")
    print(f"    - 거래 횟수: {single_results['total_trades']}건")
    print(f"    - 승률: {single_results['win_rate']:.2f}%")
    print(f"    - 수익률: {single_results['total_return']:.2f}%")

    print(f"\n  분할 매수 (1단계 30% + 2단계 50%):")
    print(f"    - 거래 횟수: {staged_results['total_trades']}건")
    print(f"    - 승률: {staged_results['win_rate']:.2f}%")
    print(f"    - 수익률: {staged_results['total_return']:.2f}%")

    # 분할 매수 평단가 효과 분석
    staged_buys = [t for t in staged_results['trades'] if t['type'] == 'buy']
    if len(staged_buys) > 1:
        print(f"\n💡 분할 매수 효과:")
        print(f"   총 {len(staged_buys)}회 매수로 평단가 최적화")

    return single_results, staged_results


async def main():
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    분할 매수 (Staged Buy) 기능 테스트                      ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")

    # 기본 분할 매수 테스트
    await test_staged_buy_basic()

    # 단일 vs 분할 비교
    await test_comparison_single_vs_staged()

    print("\n" + "="*80)
    print("✅ 모든 테스트 완료")
    print("="*80)
    print("\n💡 확인 포인트:")
    print("   1. 여러 단계의 매수가 순차적으로 실행됨")
    print("   2. 각 단계별 투자 비율이 정확히 적용됨")
    print("   3. 1단계 50% → 2단계 30%(남은 금액의) = 총 65% 투자")
    print("   4. 평단가가 동적으로 계산됨")


if __name__ == '__main__':
    asyncio.run(main())
