"""
지표 컬럼명 매핑 및 백테스트 테스트
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv('../.env')

from backtest.engine import BacktestEngine
from datetime import datetime

async def test_indicator_name_resolution():
    """지표 이름 해석 테스트"""
    print("=" * 60)
    print("지표 이름 해석 테스트")
    print("=" * 60)

    engine = BacktestEngine()

    # 테스트 데이터 생성
    import pandas as pd
    import numpy as np

    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'high': 102 + np.cumsum(np.random.randn(100) * 0.5),
        'low': 98 + np.cumsum(np.random.randn(100) * 0.5),
        'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'volume': np.random.randint(1000000, 5000000, 100),
        # 계산된 지표들
        'macd': np.random.randn(100) * 2,
        'macd_signal': np.random.randn(100) * 2,
        'macd_hist': np.random.randn(100) * 1,
        'rsi': np.random.uniform(20, 80, 100),
        'sma_20': 100 + np.cumsum(np.random.randn(100) * 0.3),
        'sma_60': 100 + np.cumsum(np.random.randn(100) * 0.2),
    }, index=dates)

    row = df.iloc[50]

    # 테스트 케이스
    test_cases = [
        ('macd', 'macd'),
        ('macd_12_26', 'macd'),
        ('macd_signal', 'macd_signal'),
        ('macd_signal_12_26_9', 'macd_signal'),
        ('rsi', 'rsi'),
        ('rsi_14', 'rsi'),
        ('sma_20', 'sma_20'),
        ('sma_60', 'sma_60'),
        ('nonexistent', None),
    ]

    print("\n테스트 결과:")
    for input_name, expected in test_cases:
        result = engine._resolve_indicator_name(row, input_name)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} {input_name:30} -> {result} (expected: {expected})")

    print("\n" + "=" * 60)

async def test_operand_resolution():
    """피연산자 해석 테스트"""
    print("\n" + "=" * 60)
    print("피연산자 해석 테스트")
    print("=" * 60)

    engine = BacktestEngine()

    import pandas as pd
    import numpy as np

    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'macd': np.random.randn(100) * 2,
        'rsi': np.random.uniform(20, 80, 100),
    }, index=dates)

    row = df.iloc[50]

    test_cases = [
        (0, ('const', 0)),
        (30, ('const', 30)),
        (70.5, ('const', 70.5)),
        ("0", ('const', 0)),
        ("30", ('const', 30)),
        ("70.5", ('const', 70.5)),
        ("macd", ('column', 'macd')),
        ("rsi", ('column', 'rsi')),
        ("macd_12_26", ('column', 'macd')),
    ]

    print("\n테스트 결과:")
    for input_val, expected in test_cases:
        result = engine._resolve_operand(row, input_val)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"{status} {str(input_val):20} -> {result} (expected: {expected})")

    print("\n" + "=" * 60)

async def test_simple_backtest():
    """간단한 백테스트 테스트"""
    print("\n" + "=" * 60)
    print("백테스트 테스트 (MACD 전략)")
    print("=" * 60)

    try:
        engine = BacktestEngine()

        # MACD 전략으로 테스트
        result = await engine.run(
            strategy_id='82b9e26e-e115-4d43-a81b-1fa1f444acd0',
            stock_codes=['005930'],
            start_date='2024-01-01',
            end_date='2024-12-31',
            initial_capital=10000000
        )

        print(f"\n백테스트 결과:")
        print(f"  총 거래 횟수: {result.get('total_trades', 0)}")
        print(f"  승률: {result.get('win_rate', 0):.2f}%")
        print(f"  총 수익률: {result.get('total_return_rate', 0):.2f}%")
        print(f"  최대 낙폭: {result.get('max_drawdown', 0):.2f}%")

        if result.get('total_trades', 0) > 0:
            print("\n[SUCCESS] 거래가 발생했습니다!")
        else:
            print("\n[FAIL] 거래가 0회입니다. 조건을 확인하세요.")

    except Exception as e:
        print(f"\n[ERROR] 에러 발생: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)

async def main():
    """메인 테스트"""
    await test_indicator_name_resolution()
    await test_operand_resolution()
    await test_simple_backtest()

if __name__ == '__main__':
    asyncio.run(main())