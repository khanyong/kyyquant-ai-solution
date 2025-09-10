"""
간단한 백테스트 테스트 - 거래가 발생하는지 확인
"""
import asyncio
import pandas as pd
import numpy as np
import sys
import json
sys.path.append('.')
from api.backtest_api import BacktestEngine
from datetime import datetime, timedelta

async def test_simple_backtest():
    """간단한 매수/매도 조건으로 백테스트 테스트"""
    
    engine = BacktestEngine()
    
    # 1. 테스트용 가격 데이터 생성 (더 현실적인 변동성 추가)
    dates = pd.date_range('2024-01-01', periods=60, freq='D')
    
    # 더 현실적인 가격 움직임 생성
    np.random.seed(42)
    
    # 트렌드 + 노이즈로 현실적인 데이터 생성
    # 하락 구간 (처음 20일)
    trend1 = np.linspace(100, 85, 20)
    noise1 = np.random.normal(0, 2, 20)  # 변동성 추가
    prices1 = trend1 + noise1
    
    # 상승 구간 (다음 20일)
    trend2 = np.linspace(85, 105, 20)
    noise2 = np.random.normal(0, 2, 20)
    prices2 = trend2 + noise2
    
    # 하락 구간 (마지막 20일)
    trend3 = np.linspace(105, 90, 20)
    noise3 = np.random.normal(0, 2, 20)
    prices3 = trend3 + noise3
    
    prices = np.concatenate([prices1, prices2, prices3])
    
    test_data = pd.DataFrame({
        'open': prices * 0.99,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'volume': 1000000,
        'trading_value': prices * 1000000,
        'change_rate': np.diff(np.concatenate([[100], prices])) / np.concatenate([[100], prices[:-1]]) * 100
    }, index=dates)
    
    # 필수 컬럼 추가
    test_data['market_cap'] = 1000000000
    test_data['per'] = 10
    test_data['pbr'] = 1
    test_data['roe'] = 10
    test_data['debt_ratio'] = 50
    
    print("=" * 50)
    print("테스트 데이터 생성 완료")
    print("=" * 50)
    print(f"기간: {dates[0].date()} ~ {dates[-1].date()}")
    print(f"가격 범위: {prices.min():.0f} ~ {prices.max():.0f}")
    print(f"데이터 개수: {len(test_data)}개")
    
    # 2. 간단한 전략 설정 (RSI 기반)
    simple_strategy = {
        'name': 'Simple RSI Test',
        'config': {
            'useStageBasedStrategy': False,
            'buyConditions': [
                {
                    'indicator': 'rsi',
                    'operator': '<',
                    'value': 35  # RSI < 35에서 매수 (더 현실적인 값)
                }
            ],
            'sellConditions': [
                {
                    'indicator': 'rsi', 
                    'operator': '>',
                    'value': 65  # RSI > 65에서 매도 (더 현실적인 값)
                }
            ]
        }
    }
    
    print("\n전략 설정:")
    print(f"매수 조건: RSI < 35")
    print(f"매도 조건: RSI > 65")
    
    # 3. RSI 계산 및 확인
    indicators = [{'indicator': 'rsi', 'params': {'period': 14}}]
    test_data_with_rsi = engine.calculate_indicators(test_data.copy(), indicators)
    
    print("\nRSI 값 확인:")
    print(f"RSI 최소값: {test_data_with_rsi['rsi'].min():.2f}")
    print(f"RSI 최대값: {test_data_with_rsi['rsi'].max():.2f}")
    print(f"RSI < 35인 날: {(test_data_with_rsi['rsi'] < 35).sum()}일")
    print(f"RSI > 65인 날: {(test_data_with_rsi['rsi'] > 65).sum()}일")
    
    # RSI 값 샘플 출력
    print("\nRSI 값 샘플 (20일째부터 40일째):")
    for i in range(19, 40, 5):
        if i < len(test_data_with_rsi):
            date = test_data_with_rsi.index[i]
            close = test_data_with_rsi.iloc[i]['close']
            rsi = test_data_with_rsi.iloc[i]['rsi']
            print(f"  {date.date()}: Close={close:.0f}, RSI={rsi:.2f}")
    
    # 4. 백테스트 실행
    price_data = {'TEST001': test_data}
    
    print("\n" + "=" * 50)
    print("백테스트 실행")
    print("=" * 50)
    
    result = await engine.run_backtest(
        strategy=simple_strategy,
        price_data=price_data,
        initial_capital=10000000,
        commission=0.00015,
        slippage=0.001,
        data_interval='1d'
    )
    
    # 5. 결과 분석
    print("\n" + "=" * 50)
    print("백테스트 결과")
    print("=" * 50)
    print(f"총 거래 횟수: {result['total_trades']}")
    print(f"최종 수익률: {result['total_return']:.2f}%")
    print(f"승률: {result['win_rate']:.2f}%")
    
    if result['trades']:
        print("\n거래 내역:")
        for trade in result['trades'][:10]:  # 처음 10개만 출력
            print(f"  {trade['date']}: {trade['action']} @ {trade['price']:.0f}")
    else:
        print("\n*** 거래가 발생하지 않았습니다! ***")
        
        # 조건 평가 직접 테스트
        print("\n조건 평가 직접 테스트:")
        test_row = test_data_with_rsi.iloc[25]  # 25일째 데이터
        print(f"테스트 데이터 (25일째):")
        print(f"  Close: {test_row['close']:.0f}")
        print(f"  RSI: {test_row['rsi']:.2f}")
        
        buy_condition = {'indicator': 'rsi', 'operator': '<', 'value': 35}
        result = engine.evaluate_condition(test_row, buy_condition)
        print(f"  매수 조건 평가 (RSI < 35): {result}")
    
    return result

if __name__ == "__main__":
    result = asyncio.run(test_simple_backtest())