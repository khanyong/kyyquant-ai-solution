"""
간단한 전략 테스트 - 거래 발생 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

def test_simple_strategy():
    """단순 전략으로 거래 발생 테스트"""

    print("="*60)
    print("단순 전략 테스트")
    print("="*60)

    # 1. 테스트 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    base_price = 70000
    prices = []

    for i in range(100):
        if i < 30:
            # 하락 추세
            base_price = base_price * 0.995
        elif i < 60:
            # 상승 추세
            base_price = base_price * 1.008
        else:
            # 약간 하락
            base_price = base_price * 0.997

        prices.append(base_price + np.random.randn() * 100)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })

    print(f"데이터 생성: {len(df)}일")
    print(f"가격 범위: {min(prices):.0f} ~ {max(prices):.0f}\n")

    # 2. 간단한 이동평균 계산
    df['ma_5'] = df['close'].rolling(window=5).mean()
    df['ma_20'] = df['close'].rolling(window=20).mean()

    print("이동평균 계산 완료")
    print(df[['date', 'close', 'ma_5', 'ma_20']].tail())

    # 3. 단순 매매 신호 생성
    buy_signals = []
    sell_signals = []
    position = False

    for i in range(20, len(df)):  # MA20이 계산된 시점부터
        if not position and df.iloc[i]['ma_5'] > df.iloc[i]['ma_20']:
            if i > 0 and df.iloc[i-1]['ma_5'] <= df.iloc[i-1]['ma_20']:
                # 골든크로스 발생
                buy_signals.append(i)
                position = True
                print(f"매수 신호: {df.iloc[i]['date'].strftime('%Y-%m-%d')}, 가격: {df.iloc[i]['close']:.0f}")

        elif position and df.iloc[i]['ma_5'] < df.iloc[i]['ma_20']:
            if i > 0 and df.iloc[i-1]['ma_5'] >= df.iloc[i-1]['ma_20']:
                # 데드크로스 발생
                sell_signals.append(i)
                position = False
                print(f"매도 신호: {df.iloc[i]['date'].strftime('%Y-%m-%d')}, 가격: {df.iloc[i]['close']:.0f}")

    print(f"\n총 매수 신호: {len(buy_signals)}개")
    print(f"총 매도 신호: {len(sell_signals)}개")

    # 4. 수익률 계산
    if len(buy_signals) > 0 and len(sell_signals) > 0:
        total_profit = 0
        for i in range(min(len(buy_signals), len(sell_signals))):
            buy_price = df.iloc[buy_signals[i]]['close']
            sell_price = df.iloc[sell_signals[i]]['close']
            profit = (sell_price - buy_price) / buy_price * 100
            total_profit += profit
            print(f"\n거래 {i+1}: 수익률 {profit:.2f}%")

        print(f"\n평균 수익률: {total_profit / min(len(buy_signals), len(sell_signals)):.2f}%")

    # 5. 전략 설정 JSON (올바른 형식)
    strategy_config = {
        "indicators": [
            {"type": "MA", "params": {"period": 5}},
            {"type": "MA", "params": {"period": 20}}
        ],
        "buyConditions": [
            {
                "indicator": "ma_5",
                "operator": ">",
                "value": "ma_20"
            }
        ],
        "sellConditions": [
            {
                "indicator": "ma_5",
                "operator": "<",
                "value": "ma_20"
            }
        ],
        "position_size": 100,
        "initial_capital": 10000000
    }

    print("\n올바른 전략 설정:")
    print(json.dumps(strategy_config, indent=2, ensure_ascii=False))

    return df, buy_signals, sell_signals

if __name__ == "__main__":
    df, buy_signals, sell_signals = test_simple_strategy()

    if len(buy_signals) == 0:
        print("\n⚠️  거래가 발생하지 않음!")
        print("가능한 원인:")
        print("1. 이동평균 기간이 너무 긴 경우")
        print("2. 데이터가 충분하지 않은 경우")
        print("3. 시장 조건이 맞지 않는 경우")
    else:
        print(f"\n✅ 거래 발생 확인: {len(buy_signals)}회")