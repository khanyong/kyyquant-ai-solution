"""
동적 손절선 기능 테스트 - UI 이미지에 표시된 전략 그대로 테스트
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

async def test_ui_exact_config():
    """
    UI 이미지 그대로 테스트:
    - 1단계: 3% → 50% 매도, 손절→본전
    - 2단계: 5% → 30% 매도, 손절→1단계가
    - 3단계: 10% → 20% 매도, 손절→2단계가
    - 손절 라인: -3%
    """
    print("\n" + "="*80)
    print("UI 이미지 전략 테스트: 동적 손절선 포함")
    print("="*80)

    engine = BacktestEngine()

    # UI 이미지에 표시된 정확한 설정
    strategy_config = {
        'name': 'UI Exact Config Test',
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
                        {
                            'stage': 1,
                            'targetProfit': 3,
                            'exitRatio': 50,
                            'dynamicStopLoss': True  # 손절→본전
                        },
                        {
                            'stage': 2,
                            'targetProfit': 5,
                            'exitRatio': 30,
                            'dynamicStopLoss': True  # 손절→1단계가
                        },
                        {
                            'stage': 3,
                            'targetProfit': 10,
                            'exitRatio': 20,
                            'dynamicStopLoss': True  # 손절→2단계가
                        }
                    ],
                    'combineWith': 'OR'
                }
            },
            'stopLoss': {
                'enabled': True,
                'value': 3  # UI에서 절대값 3% (실제로는 -3%)
            },
            'position_size': 0.3
        }
    }

    # 백테스트 실행
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 더 긴 기간

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
    stage_1_exits = [t for t in results['trades'] if t['type'] == 'sell' and 'stage_1' in t.get('reason', '')]
    stage_2_exits = [t for t in results['trades'] if t['type'] == 'sell' and 'stage_2' in t.get('reason', '')]
    stage_3_exits = [t for t in results['trades'] if t['type'] == 'sell' and 'stage_3' in t.get('reason', '')]
    stop_loss_exits = [t for t in results['trades'] if t['type'] == 'sell' and 'stop_loss' in t.get('reason', '')]
    signal_exits = [t for t in results['trades'] if t['type'] == 'sell' and 'Signal' in t.get('reason', '')]

    print(f"\n📊 매도 이유별 분류:")
    print(f"  - 1단계 목표 (3% → 50% 매도): {len(stage_1_exits)}건")
    print(f"  - 2단계 목표 (5% → 30% 매도): {len(stage_2_exits)}건")
    print(f"  - 3단계 목표 (10% → 20% 매도): {len(stage_3_exits)}건")
    print(f"  - 손절 (-3% 또는 동적): {len(stop_loss_exits)}건")
    print(f"  - 시그널: {len(signal_exits)}건")

    # 상세 거래 내역
    print(f"\n📋 거래 상세 내역:")
    for i, trade in enumerate(results['trades'], 1):
        if trade['type'] == 'sell':
            print(f"\n  매도 {i}:")
            print(f"    날짜: {trade['date']}")
            print(f"    수익률: {trade['profit_rate']:.2f}%")
            print(f"    매도 비율: {trade.get('exit_ratio', 100)}%")
            print(f"    이유: {trade['reason']}")
            print(f"    수익: {trade['profit']:,.0f}원")

    return results


async def test_dynamic_stop_scenarios():
    """
    시나리오별 동적 손절선 동작 확인
    """
    print("\n" + "="*80)
    print("동적 손절선 시나리오 테스트")
    print("="*80)

    # 시나리오: 4% 상승 후 2%로 하락 (1단계 도달 후 본전 손절 테스트)
    print("\n📌 시나리오 1: 4% 상승 후 2%로 하락")
    print("   예상: 1단계(3%) 도달 → 손절선 0%로 이동 → 2%에서 청산 안됨")

    # 시나리오: 6% 상승 후 2%로 하락 (2단계 도달 후 1단계가 손절)
    print("\n📌 시나리오 2: 6% 상승 후 2%로 하락")
    print("   예상: 2단계(5%) 도달 → 손절선 3%로 이동 → 2%에서 손절 청산됨")

    # 실제 백테스트로 확인
    engine = BacktestEngine()
    strategy_config = {
        'name': 'Dynamic Stop Test',
        'config': {
            'indicators': [
                {'name': 'rsi', 'params': {'period': 14}}
            ],
            'buyConditions': [
                {'left': 'rsi', 'operator': '<', 'right': 50}
            ],
            'sellConditions': [
                {'left': 'rsi', 'operator': '>', 'right': 80}  # 거의 안 발생
            ],
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
            'stopLoss': {
                'enabled': True,
                'value': 3
            },
            'position_size': 0.3
        }
    }

    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    results = await engine.run_with_config(
        strategy_config=strategy_config['config'],
        stock_codes=['005930'],
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=10000000,
        commission=0.0015,
        slippage=0.001
    )

    print(f"\n✅ 결과:")
    print(f"   총 거래: {results['total_trades']}건")
    print(f"   승률: {results['win_rate']:.2f}%")
    print(f"   수익률: {results['total_return']:.2f}%")

    return results


async def main():
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                  동적 손절선 기능 테스트                                   ║")
    print("║         (UI 이미지에 표시된 전략 그대로 구현 확인)                        ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")

    # UI 정확한 설정 테스트
    await test_ui_exact_config()

    # 동적 손절 시나리오 테스트
    await test_dynamic_stop_scenarios()

    print("\n" + "="*80)
    print("✅ 모든 테스트 완료")
    print("="*80)
    print("\n💡 확인 포인트:")
    print("   1. 단계별 목표 도달 시 부분 매도 실행")
    print("   2. 1단계 도달 후 손절선이 본전(0%)으로 이동")
    print("   3. 2단계 도달 후 손절선이 1단계가(3%)로 이동")
    print("   4. 3단계 도달 후 손절선이 2단계가(5%)로 이동")


if __name__ == '__main__':
    asyncio.run(main())
