"""
최대낙폭(MDD) 계산 검증 테스트
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 환경변수 설정
os.environ['SUPABASE_URL'] = os.getenv('SUPABASE_URL', '')
os.environ['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY', '')
os.environ['ENFORCE_DB_INDICATORS'] = 'false'  # 개발 모드

from backtest.engine import BacktestEngine

async def test_mdd_calculation():
    """MDD 계산 검증"""

    # 간단한 전략 설정
    strategy_config = {
        'name': 'MDD Test Strategy',
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
                'indicator': 'sma_5',
                'operator': 'cross_above',
                'compareTo': 'sma_20'
            }
        ],
        'sellConditions': [
            {
                'indicator': 'sma_5',
                'operator': 'cross_below',
                'compareTo': 'sma_20'
            }
        ]
    }

    strategy = {
        'id': 'test_mdd',
        'name': 'MDD Test',
        'config': strategy_config
    }

    engine = BacktestEngine()

    # 날짜 범위
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

    print("=" * 60)
    print("MDD (최대낙폭) 계산 검증 테스트")
    print("=" * 60)
    print(f"기간: {start_date} ~ {end_date}")
    print()

    # 테스트용 가격 데이터 생성 (의도적으로 큰 하락 구간 포함)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    base_price = 100000
    price_data = []

    for i, date in enumerate(dates):
        # Day 0-10: 상승 (+20%)
        if i < 10:
            price = base_price * (1 + i * 0.02)
        # Day 10-20: 급락 (-30%)
        elif i < 20:
            peak_price = base_price * 1.20
            price = peak_price * (1 - (i - 10) * 0.03)
        # Day 20-30: 회복 (+10%)
        elif i < 30:
            low_price = base_price * 1.20 * 0.70
            price = low_price * (1 + (i - 20) * 0.01)
        # Day 30+: 안정
        else:
            price = base_price * 1.00

        price_data.append({
            'date': date,
            'open': price * 0.99,
            'high': price * 1.01,
            'low': price * 0.98,
            'close': price,
            'volume': np.random.randint(10000000, 30000000)
        })

    df = pd.DataFrame(price_data)
    df.set_index('date', inplace=True)

    price_data_dict = {'005930': df}

    result = await engine._run_backtest(
        strategy=strategy,
        price_data=price_data_dict,
        initial_capital=10000000,
        commission=0.00015,
        slippage=0.001
    )

    # 결과에서 MDD 정보 추출
    print("\n=== 백테스트 결과 ===")
    print(f"초기 자본금: {result['initial_capital']:,.0f}원")
    print(f"최종 자본금: {result['final_capital']:,.0f}원")
    print(f"총 수익률: {result['total_return_rate']:.2f}%")
    print(f"총 거래: {len(result['trades'])}회")
    print()

    # daily_values에서 MDD 수동 계산
    daily_values = result.get('daily_values', [])

    if daily_values:
        print("=== MDD 계산 검증 ===")

        # 백엔드에서 계산한 MDD 추출 (prepare_results 메서드에서 계산됨)
        # 백엔드 MDD는 prepare_results에서 계산되므로, 직접 계산해야 함

        # 수동 MDD 계산
        max_drawdown_manual = 0
        peak_value = daily_values[0].get('total_value', result['initial_capital'])

        print(f"\n일별 자산 가치 변화:")
        print(f"{'날짜':<12} {'자산가치':>15} {'최고점':>15} {'낙폭(%)':>10}")
        print("-" * 60)

        for i, dv in enumerate(daily_values[:20]):  # 처음 20일만 출력
            value = dv.get('total_value', 0)
            peak_value = max(peak_value, value)

            if peak_value > 0:
                drawdown = (peak_value - value) / peak_value * 100
                max_drawdown_manual = max(max_drawdown_manual, drawdown)
            else:
                drawdown = 0

            date_str = str(dv.get('date', ''))[:10]
            print(f"{date_str:<12} {value:>15,.0f} {peak_value:>15,.0f} {drawdown:>9.2f}%")

        if len(daily_values) > 20:
            print(f"... ({len(daily_values) - 20}개 행 생략)")

        print()
        print(f"✓ 수동 계산 MDD: {max_drawdown_manual:.2f}%")

        # prepare_results에서 계산된 MDD를 가져오려면 전체 결과를 호출해야 함
        final_result = engine._prepare_results(result, strategy['id'], start_date, end_date)
        backend_mdd = final_result.get('max_drawdown', 0)

        print(f"✓ 백엔드 계산 MDD: {backend_mdd:.2f}%")
        print()

        # 비교
        diff = abs(max_drawdown_manual - backend_mdd)
        if diff < 0.01:
            print("✅ MDD 계산 일치: 백엔드와 수동 계산이 동일합니다!")
        else:
            print(f"⚠️  MDD 계산 불일치: 차이 = {diff:.2f}%")
            print("   → 백엔드 계산식을 확인해야 합니다.")
    else:
        print("❌ daily_values 데이터가 없습니다.")

    print()
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_mdd_calculation())
