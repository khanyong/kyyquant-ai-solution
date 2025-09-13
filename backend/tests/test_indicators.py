"""
지표 계산 및 조건 평가 테스트
"""
import pandas as pd
import numpy as np
import sys
sys.path.append('.')
from api.backtest_api import BacktestEngine

def test_all_indicators():
    """모든 지표 테스트"""
    
    # 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # 트렌드가 있는 가격 데이터 생성
    trend = np.linspace(100, 120, 100)  # 상승 트렌드
    noise = np.random.randn(100) * 2
    close_prices = trend + noise
    
    data = pd.DataFrame({
        'open': close_prices + np.random.randn(100) * 1,
        'high': close_prices + abs(np.random.randn(100) * 3),
        'low': close_prices - abs(np.random.randn(100) * 3),
        'close': close_prices,
        'volume': 1000000 + np.random.randint(-100000, 100000, 100)
    }, index=dates)
    
    # 고저 관계 보정
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    engine = BacktestEngine()
    
    print("="*50)
    print("지표 계산 테스트")
    print("="*50)
    
    # 1. RSI 테스트
    print("\n1. RSI 지표")
    rsi = engine.calculate_rsi(data['close'], period=14)
    print(f"   - 범위: {rsi.min():.2f} ~ {rsi.max():.2f}")
    print(f"   - 마지막 5개 값: {rsi.tail(5).round(2).tolist()}")
    print(f"   - NaN 개수: {rsi.isna().sum()}")
    print(f"   - 정상 범위(0-100) 체크: {'OK' if (rsi.dropna() >= 0).all() and (rsi.dropna() <= 100).all() else 'FAIL'}")
    
    # 2. MACD 테스트
    print("\n2. MACD 지표")
    macd, signal, hist = engine.calculate_macd(data['close'])
    print(f"   - MACD 마지막 값: {macd.iloc[-1]:.2f}")
    print(f"   - Signal 마지막 값: {signal.iloc[-1]:.2f}")
    print(f"   - Histogram 마지막 값: {hist.iloc[-1]:.2f}")
    print(f"   - NaN 개수: MACD={macd.isna().sum()}, Signal={signal.isna().sum()}")
    print(f"   - 교차 체크: MACD > Signal = {macd.iloc[-1] > signal.iloc[-1]}")
    
    # 3. Stochastic 테스트
    print("\n3. Stochastic 지표")
    stoch_k, stoch_d = engine.calculate_stochastic(
        data['high'], data['low'], data['close'], k_period=14, d_period=3
    )
    print(f"   - %K 범위: {stoch_k.min():.2f} ~ {stoch_k.max():.2f}")
    print(f"   - %D 범위: {stoch_d.min():.2f} ~ {stoch_d.max():.2f}")
    print(f"   - 마지막 %K: {stoch_k.iloc[-1]:.2f}, %D: {stoch_d.iloc[-1]:.2f}")
    print(f"   - NaN 개수: K={stoch_k.isna().sum()}, D={stoch_d.isna().sum()}")
    print(f"   - 정상 범위(0-100) 체크: {'OK' if (stoch_k.dropna() >= 0).all() and (stoch_k.dropna() <= 100).all() else 'FAIL'}")
    
    # 4. Bollinger Bands 테스트
    print("\n4. Bollinger Bands 지표")
    bb_upper, bb_middle, bb_lower = engine.calculate_bollinger(data['close'], period=20, std_dev=2)
    print(f"   - Upper: {bb_upper.iloc[-1]:.2f}")
    print(f"   - Middle: {bb_middle.iloc[-1]:.2f}")
    print(f"   - Lower: {bb_lower.iloc[-1]:.2f}")
    print(f"   - 밴드 폭: {(bb_upper.iloc[-1] - bb_lower.iloc[-1]):.2f}")
    print(f"   - NaN 개수: {bb_upper.isna().sum()}")
    print(f"   - 순서 체크(Upper > Middle > Lower): {'OK' if bb_upper.iloc[-1] > bb_middle.iloc[-1] > bb_lower.iloc[-1] else 'FAIL'}")
    
    # 5. Ichimoku 테스트
    print("\n5. Ichimoku 지표")
    ichimoku_df = engine.calculate_ichimoku(data.copy())
    print(f"   - Tenkan(전환선): {ichimoku_df['ichimoku_tenkan'].iloc[-1]:.2f}")
    print(f"   - Kijun(기준선): {ichimoku_df['ichimoku_kijun'].iloc[-1]:.2f}")
    if 'ichimoku_senkou_a' in ichimoku_df.columns:
        print(f"   - Senkou A: {ichimoku_df['ichimoku_senkou_a'].iloc[-1]:.2f}")
    if 'ichimoku_senkou_b' in ichimoku_df.columns:
        print(f"   - Senkou B: {ichimoku_df['ichimoku_senkou_b'].iloc[-1]:.2f}")
    print(f"   - 컬럼 확인: {[col for col in ichimoku_df.columns if 'ichimoku' in col]}")
    
    print("\n" + "="*50)
    print("조건 평가 테스트")
    print("="*50)
    
    # 테스트용 row 생성
    test_row = pd.Series({
        'close': 110,
        'open': 108,
        'high': 112,
        'low': 107,
        'volume': 1000000,
        'rsi': 65,
        'macd': 2.5,
        'macd_signal': 2.0,
        'stoch_k': 75,
        'stoch_d': 70,
        'bb_upper': 115,
        'bb_middle': 110,
        'bb_lower': 105,
        'ichimoku_tenkan': 109,
        'ichimoku_kijun': 108,
        'ichimoku_senkou_a': 107,
        'ichimoku_senkou_b': 106
    })
    
    # 조건 테스트
    conditions_to_test = [
        {'indicator': 'rsi', 'operator': 'rsi_overbought_70', 'value': 70},
        {'indicator': 'rsi', 'operator': '>', 'value': 60},
        {'indicator': 'macd', 'operator': 'macd_above_signal', 'value': 0},
        {'indicator': 'macd', 'operator': 'cross_above', 'value': 'MACD_SIGNAL'},
        {'indicator': 'macd', 'operator': '>', 'value': 0},
        {'indicator': 'stochastic', 'operator': 'stoch_overbought_80', 'value': 80},
        {'indicator': 'stochastic', 'operator': 'stoch_oversold_20', 'value': 20},
    ]
    
    print("\n조건 평가 결과:")
    for i, cond in enumerate(conditions_to_test, 1):
        try:
            result = engine.evaluate_condition(test_row, cond)
            print(f"{i}. {cond['indicator']} {cond['operator']} {cond['value']}: {result}")
        except Exception as e:
            print(f"{i}. {cond['indicator']} {cond['operator']} {cond['value']}: ERROR - {e}")
    
    print("\n" + "="*50)
    print("테스트 완료!")
    print("="*50)

if __name__ == "__main__":
    try:
        test_all_indicators()
    except Exception as e:
        print(f"테스트 실패: {e}")
        import traceback
        traceback.print_exc()