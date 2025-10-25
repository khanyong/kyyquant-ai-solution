"""
지표 계산 테스트
"""
import os
import sys
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime, timedelta
import asyncio

# 환경 변수 로드
load_dotenv()

from indicators.calculator import IndicatorCalculator
from data.provider import DataProvider


async def test_indicators():
    """지표 계산 테스트"""

    # 1. 데이터 조회
    provider = DataProvider()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)

    print('=' * 70)
    print('Testing indicator calculation for 005930 (Samsung)')
    print('=' * 70)
    print(f'Date range: {start_date.date()} to {end_date.date()}')

    df = await provider.get_historical_data(
        stock_code='005930',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )

    if df is None or len(df) == 0:
        print('[ERROR] No data found')
        return False

    print(f'[OK] Loaded {len(df)} days of data')
    print(f'Columns: {df.columns.tolist()}')

    if 'close' in df.columns:
        print(f'Latest close: {df.iloc[-1]["close"]:.2f}')

    # 2. 지표 계산 테스트
    calc = IndicatorCalculator()
    all_passed = True

    print('\n' + '=' * 70)
    print('Testing MA(20)')
    print('=' * 70)
    try:
        config = {'name': 'ma', 'params': {'period': 20}}
        result = calc.calculate(df.copy(), config, stock_code='005930')
        if result and result.columns and 'ma' in result.columns:
            ma_series = result.columns['ma']
            latest_ma = ma_series.iloc[-1]
            if not pd.isna(latest_ma):
                print(f'[OK] MA(20) = {latest_ma:.2f}')
            else:
                print('[ERROR] MA(20) is NaN')
                all_passed = False
        else:
            print('[ERROR] MA calculation returned invalid result')
            all_passed = False
    except Exception as e:
        print(f'[ERROR] MA calculation failed: {e}')
        all_passed = False

    print('\n' + '=' * 70)
    print('Testing MA(12)')
    print('=' * 70)
    try:
        config = {'name': 'ma', 'params': {'period': 12}}
        result = calc.calculate(df.copy(), config, stock_code='005930')
        if result and result.columns and 'ma' in result.columns:
            ma_series = result.columns['ma']
            latest_ma = ma_series.iloc[-1]
            if not pd.isna(latest_ma):
                print(f'[OK] MA(12) = {latest_ma:.2f}')
            else:
                print('[ERROR] MA(12) is NaN')
                all_passed = False
        else:
            print('[ERROR] MA(12) calculation returned invalid result')
            all_passed = False
    except Exception as e:
        print(f'[ERROR] MA(12) calculation failed: {e}')
        all_passed = False

    print('\n' + '=' * 70)
    print('Testing Bollinger Bands(20, 2)')
    print('=' * 70)
    try:
        config = {'name': 'bollinger', 'params': {'period': 20, 'std_dev': 2}}
        result = calc.calculate(df.copy(), config, stock_code='005930')
        if result and result.columns:
            expected_cols = ['bollinger_upper', 'bollinger_middle', 'bollinger_lower']
            if all(col in result.columns for col in expected_cols):
                upper = result.columns['bollinger_upper'].iloc[-1]
                middle = result.columns['bollinger_middle'].iloc[-1]
                lower = result.columns['bollinger_lower'].iloc[-1]
                if not any(pd.isna(v) for v in [upper, middle, lower]):
                    print(f'[OK] Bollinger Upper  = {upper:.2f}')
                    print(f'[OK] Bollinger Middle = {middle:.2f}')
                    print(f'[OK] Bollinger Lower  = {lower:.2f}')
                    print(f'[OK] Band Width = {upper - lower:.2f}')
                else:
                    print('[ERROR] Bollinger values are NaN')
                    all_passed = False
            else:
                print(f'[ERROR] Missing columns. Got: {list(result.columns.keys())}')
                all_passed = False
        else:
            print('[ERROR] Bollinger calculation returned invalid result')
            all_passed = False
    except Exception as e:
        print(f'[ERROR] Bollinger calculation failed: {e}')
        all_passed = False

    print('\n' + '=' * 70)
    print('Testing RSI(14)')
    print('=' * 70)
    try:
        config = {'name': 'rsi', 'params': {'period': 14}}
        result = calc.calculate(df.copy(), config, stock_code='005930')
        if result and result.columns and 'rsi' in result.columns:
            rsi_series = result.columns['rsi']
            latest_rsi = rsi_series.iloc[-1]
            if not pd.isna(latest_rsi):
                print(f'[OK] RSI(14) = {latest_rsi:.2f}')

                # RSI는 0-100 범위여야 함
                if 0 <= latest_rsi <= 100:
                    print(f'[OK] RSI value is in valid range (0-100)')
                else:
                    print(f'[WARNING] RSI value out of range: {latest_rsi}')
            else:
                print('[ERROR] RSI is NaN')
                all_passed = False
        else:
            print('[ERROR] RSI calculation returned invalid result')
            all_passed = False
    except Exception as e:
        print(f'[ERROR] RSI calculation failed: {e}')
        all_passed = False

    # 3. 전략 조건 시뮬레이션
    print('\n' + '=' * 70)
    print('Strategy Condition Simulation')
    print('=' * 70)

    try:
        current_price = df.iloc[-1]['close']
        ma_20_res = calc.calculate(df.copy(), {'name': 'ma', 'params': {'period': 20}}, stock_code='005930')
        ma_12_res = calc.calculate(df.copy(), {'name': 'ma', 'params': {'period': 12}}, stock_code='005930')
        ma_20_val = ma_20_res.columns['ma'].iloc[-1]
        ma_12_val = ma_12_res.columns['ma'].iloc[-1]

        print(f'\nCurrent Price: {current_price:.2f}')
        print(f'MA(20):        {ma_20_val:.2f}')
        print(f'MA(12):        {ma_12_val:.2f}')

        # "나의 전략 7" 조건 체크
        cond1 = current_price < ma_20_val
        cond2 = current_price < ma_12_val

        print(f'\n[Strategy 1: "나의 전략 7"]')
        print(f'  Condition 1: close({current_price:.2f}) < ma_20({ma_20_val:.2f}) -> {cond1}')
        print(f'  Condition 2: close({current_price:.2f}) < ma_12({ma_12_val:.2f}) -> {cond2}')
        print(f'  Buy Signal: {cond1 and cond2}')

        # "[분할] 볼린저밴드" 조건 체크
        bb_res = calc.calculate(df.copy(), {'name': 'bollinger', 'params': {'period': 20, 'std_dev': 2}}, stock_code='005930')
        rsi_res = calc.calculate(df.copy(), {'name': 'rsi', 'params': {'period': 14}}, stock_code='005930')
        bb_lower = bb_res.columns['bollinger_lower'].iloc[-1]
        rsi_val = rsi_res.columns['rsi'].iloc[-1]

        print(f'\n[Strategy 2: "[분할] 볼린저밴드"]')
        print(f'  Bollinger Lower: {bb_lower:.2f}')
        print(f'  RSI(14):         {rsi_val:.2f}')

        cond1_bb = current_price < bb_lower
        cond2_bb = rsi_val < 45

        print(f'  Condition 1: close({current_price:.2f}) < bollinger_lower({bb_lower:.2f}) -> {cond1_bb}')
        print(f'  Condition 2: rsi({rsi_val:.2f}) < 45 -> {cond2_bb}')
        print(f'  Buy Signal (1st): {cond1_bb and cond2_bb}')

        cond2_bb_2nd = rsi_val < 35
        print(f'  Condition 4: rsi({rsi_val:.2f}) < 35 -> {cond2_bb_2nd}')
        print(f'  Buy Signal (2nd): {cond1_bb and cond2_bb_2nd}')

    except Exception as e:
        print(f'[ERROR] Strategy simulation failed: {e}')

    print('\n' + '=' * 70)
    print('Summary')
    print('=' * 70)
    if all_passed:
        print('[OK] All indicator calculations passed!')
        return True
    else:
        print('[ERROR] Some indicator calculations failed')
        return False


if __name__ == '__main__':
    result = asyncio.run(test_indicators())
    sys.exit(0 if result else 1)
