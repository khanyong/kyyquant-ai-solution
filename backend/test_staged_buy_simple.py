"""
간단한 분할 매수 테스트 - 완화된 조건
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

async def test_simple_staged():
    """완화된 조건으로 분할 매수 테스트"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║              간단한 분할 매수 테스트 (완화된 조건)                         ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")

    engine = BacktestEngine()

    # 매우 완화된 조건의 분할 매수
    strategy_config = {
        'indicators': [{'name': 'rsi', 'params': {'period': 14}}],
        'useStageBasedStrategy': True,
        'buyStageStrategy': {
            'stages': [
                {
                    'stage': 1,
                    'enabled': True,
                    'positionPercent': 50,  # 50% 투자
                    'passAllRequired': True,
                    'conditions': [
                        {'left': 'rsi', 'operator': '<', 'right': 45}  # 매우 완화
                    ]
                },
                {
                    'stage': 2,
                    'enabled': True,
                    'positionPercent': 30,  # 남은 자금의 30%
                    'passAllRequired': True,
                    'conditions': [
                        {'left': 'rsi', 'operator': '<', 'right': 40}
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
                        {'left': 'rsi', 'operator': '>', 'right': 65}  # 완화
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

    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    results = await engine.run_with_config(
        strategy_config=strategy_config,
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

    # 매수/매도 거래 분석
    buy_trades = [t for t in results['trades'] if t['type'] == 'buy']
    sell_trades = [t for t in results['trades'] if t['type'] == 'sell']

    stage_1_buys = [t for t in buy_trades if 'stage_1' in t.get('reason', '')]
    stage_2_buys = [t for t in buy_trades if 'stage_2' in t.get('reason', '')]

    print(f"\n📊 매수 거래 분석:")
    print(f"  ├─ 1단계 매수 (RSI < 45, 50% 투자): {len(stage_1_buys)}건")
    print(f"  └─ 2단계 매수 (RSI < 40, 30% 추가): {len(stage_2_buys)}건")
    print(f"  총 매수: {len(buy_trades)}건")

    print(f"\n📋 전체 거래 내역:")
    all_trades = sorted(results['trades'], key=lambda x: x['date'])
    for i, trade in enumerate(all_trades[:15], 1):  # 최대 15건
        print(f"\n  [{i}] {trade['date']} - {trade['type'].upper()}")
        print(f"      금액: {trade['amount']:,.0f}원")
        print(f"      수량: {trade['quantity']:,}주")
        print(f"      가격: {trade['price']:,.0f}원")
        print(f"      이유: {trade['reason']}")
        if trade['type'] == 'sell':
            print(f"      수익률: {trade['profit_rate']:.2f}%")
            print(f"      매도비율: {trade.get('exit_ratio', 100)}%")

    # 분할 매수 효과 분석
    if len(buy_trades) > 1:
        print(f"\n💡 분할 매수 효과 분석:")
        total_buy_amount = sum(t['amount'] + t['commission'] for t in buy_trades)
        print(f"   총 투자금: {total_buy_amount:,.0f}원")

        if stage_1_buys and stage_2_buys:
            stage1_amount = sum(t['amount'] + t['commission'] for t in stage_1_buys)
            stage2_amount = sum(t['amount'] + t['commission'] for t in stage_2_buys)
            print(f"   1단계 투자: {stage1_amount:,.0f}원 ({stage1_amount/10000000*100:.1f}%)")
            print(f"   2단계 투자: {stage2_amount:,.0f}원 ({stage2_amount/10000000*100:.1f}%)")

            # 평단가 효과
            if stage_2_buys:
                avg_stage1_price = sum(t['price'] for t in stage_1_buys) / len(stage_1_buys)
                avg_stage2_price = sum(t['price'] for t in stage_2_buys) / len(stage_2_buys)
                print(f"\n   평단가 효과:")
                print(f"   1단계 평균가: {avg_stage1_price:,.0f}원")
                print(f"   2단계 평균가: {avg_stage2_price:,.0f}원")
                if avg_stage2_price < avg_stage1_price:
                    print(f"   ✅ 하락 시 추가 매수로 평단가 하락 ({(avg_stage1_price-avg_stage2_price)/avg_stage1_price*100:.1f}%)")

    return results


if __name__ == '__main__':
    asyncio.run(test_simple_staged())
