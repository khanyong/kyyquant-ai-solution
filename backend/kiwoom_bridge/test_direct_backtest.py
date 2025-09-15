"""
백테스트 엔진 직접 테스트
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Core 모듈 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 모듈 임포트
from backtest_engine_advanced import AdvancedBacktestEngine

def test_direct_backtest():
    """백테스트 엔진 직접 실행"""

    print("="*60)
    print("백테스트 엔진 직접 테스트")
    print("="*60)

    # 1. 테스트 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    prices = []
    base_price = 70000

    # 가격 변동 생성 (확실한 크로스 발생)
    for i in range(100):
        if i < 30:
            base_price = base_price * 0.995  # 하락
        elif i < 60:
            base_price = base_price * 1.01   # 급상승
        else:
            base_price = base_price * 0.997  # 다시 하락

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
    print(f"가격 범위: {min(prices):.0f} ~ {max(prices):.0f}")

    # 2. 초단순 전략 설정
    config = {
        "indicators": [
            {"type": "MA", "params": {"period": 5}},
            {"type": "MA", "params": {"period": 10}}
        ],
        "buyConditions": [
            {"indicator": "ma_5", "operator": ">", "value": "ma_10"}
        ],
        "sellConditions": [
            {"indicator": "ma_5", "operator": "<", "value": "ma_10"}
        ],
        "position_size": 100,
        "stop_loss": None,
        "take_profit": None
    }

    print("\n전략 설정:")
    print(f"매수: MA5 > MA10")
    print(f"매도: MA5 < MA10")

    # 3. 백테스트 엔진 실행
    try:
        engine = AdvancedBacktestEngine(
            initial_capital=10000000,
            commission=0.00015,
            slippage=0.001
        )

        print("\n백테스트 실행 중...")
        result = engine.run(
            data=df,
            strategy_config=config
        )

        # 4. 결과 분석
        print("\n" + "="*40)
        print("백테스트 결과")
        print("="*40)

        if result:
            trades = result.get('trades', [])
            print(f"총 거래 횟수: {len(trades)}")

            if trades:
                print("\n[거래 내역]")
                for i, trade in enumerate(trades[:5], 1):  # 처음 5개만
                    print(f"{i}. {trade['date']}: {trade['action']} @ {trade['price']:.0f}")

                # 수익률 계산
                total_return = result.get('metrics', {}).get('total_return', 0)
                print(f"\n총 수익률: {total_return:.2f}%")
            else:
                print("\n[문제] 거래가 발생하지 않음")

                # 디버그 정보
                debug = result.get('debug', {})
                if debug:
                    print("\n[디버그 정보]")
                    print(f"매수 신호: {debug.get('buy_signals', 0)}개")
                    print(f"매도 신호: {debug.get('sell_signals', 0)}개")
                    print(f"계산된 지표: {debug.get('indicators', [])}")
        else:
            print("[ERROR] 백테스트 실행 실패")

    except Exception as e:
        print(f"\n[EXCEPTION] {e}")
        import traceback
        traceback.print_exc()

    # 5. 수동으로 MA 계산 및 크로스 확인
    print("\n" + "="*40)
    print("수동 MA 계산")
    print("="*40)

    df['ma5'] = df['close'].rolling(window=5).mean()
    df['ma10'] = df['close'].rolling(window=10).mean()

    # 크로스 발생 확인
    df['cross'] = (df['ma5'] > df['ma10']) != (df['ma5'].shift(1) > df['ma10'].shift(1))
    cross_count = df['cross'].sum()

    print(f"MA5/MA10 크로스 발생: {cross_count}회")

    if cross_count > 0:
        print("\n크로스 발생 시점:")
        cross_points = df[df['cross']]
        print(cross_points[['date', 'close', 'ma5', 'ma10']].head())

if __name__ == "__main__":
    test_direct_backtest()