"""
간단한 백테스트 테스트 스크립트
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 환경변수 설정
os.environ['SUPABASE_URL'] = os.getenv('SUPABASE_URL', '')
os.environ['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY', '')

from backtest.engine import BacktestEngine

async def test_simple_strategy():
    """간단한 골든크로스 전략 테스트"""

    # 간단한 전략 설정 - 골든크로스/데드크로스
    strategy_config = {
        'name': 'Simple Golden Cross',
        'indicators': [
            {
                'name': 'sma_5',
                'params': {'period': 5},
                'calculation_type': 'builtin',
                'base_indicator': 'sma'
            },
            {
                'name': 'sma_20',
                'params': {'period': 20},
                'calculation_type': 'builtin',
                'base_indicator': 'sma'
            }
        ],
        'buyConditions': [
            {
                'indicator': 'sma_5',  # 5일 이평선
                'operator': 'cross_above',
                'compareTo': 'sma_20'  # 20일 이평선
            }
        ],
        'sellConditions': [
            {
                'indicator': 'sma_5',  # 5일 이평선이
                'operator': 'cross_below',
                'compareTo': 'sma_20'  # 20일 이평선 아래로 내려가면 매도
            },
            {
                'indicator': 'profit_rate',
                'operator': '>',
                'value': 5  # 5% 수익시 매도
            },
            {
                'indicator': 'profit_rate',
                'operator': '<',
                'value': -3  # 3% 손실시 매도
            }
        ]
    }

    # 임시 전략 객체 생성
    strategy = {
        'id': 'test_strategy_1',
        'name': 'Test Golden Cross',
        'config': strategy_config
    }

    # 백테스트 엔진 생성
    engine = BacktestEngine()

    # 날짜 범위 설정
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    print(f"Testing strategy from {start_date} to {end_date}")
    print(f"Stock: 005930 (Samsung Electronics)")
    print("-" * 50)

    try:
        # 테스트용 가짜 가격 데이터 생성
        import pandas as pd
        import numpy as np

        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # 가격 데이터 생성 (트렌드가 있는 랜덤 데이터)
        base_price = 70000
        price_data = []

        for i, date in enumerate(dates):
            # 트렌드 + 노이즈
            trend = np.sin(i * 0.1) * 5000  # 주기적 트렌드
            noise = np.random.randn() * 1000  # 랜덤 노이즈
            close_price = base_price + trend + noise

            price_data.append({
                'date': date,
                'open': close_price * 0.99,
                'high': close_price * 1.01,
                'low': close_price * 0.98,
                'close': close_price,
                'volume': np.random.randint(10000000, 30000000)
            })

        df = pd.DataFrame(price_data)
        df.set_index('date', inplace=True)

        # 엔진의 _run_backtest 메서드를 직접 호출
        price_data_dict = {'005930': df}

        result = await engine._run_backtest(
            strategy=strategy,
            price_data=price_data_dict,
            initial_capital=10000000,
            commission=0.00015,
            slippage=0.001
        )

        # 결과 출력
        print("\n=== Backtest Results ===")
        print(f"Initial Capital: {result['initial_capital']:,.0f} KRW")
        print(f"Final Capital: {result['final_capital']:,.0f} KRW")
        print(f"Total Return: {result['total_return']:,.0f} KRW")
        print(f"Total Return Rate: {result['total_return_rate']:.2f}%")
        print(f"Total Trades: {len(result['trades'])}")

        # 거래 내역 출력
        if result['trades']:
            print("\n=== Trade History ===")
            for trade in result['trades'][:10]:  # 처음 10개만
                print(f"{trade['date'].strftime('%Y-%m-%d')} | {trade['type']:4} | "
                      f"Price: {trade['price']:,.0f} | Qty: {trade['quantity']} | "
                      f"Reason: {trade.get('reason', 'N/A')}")
                if trade['type'] == 'sell' and 'profit_rate' in trade:
                    print(f"  -> Profit: {trade.get('profit', 0):,.0f} KRW ({trade.get('profit_rate', 0):.2f}%)")
        else:
            print("\nNo trades executed!")

    except Exception as e:
        print(f"Error during backtest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_strategy())