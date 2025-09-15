"""
간단한 백테스트 테스트
지표 계산과 신호 생성을 단계별로 확인
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_data():
    """명확한 골든크로스 패턴을 가진 테스트 데이터 생성"""
    dates = pd.date_range('2024-01-01', periods=100)

    # 초기 하락 -> 상승 -> 하락 패턴
    prices = []
    base = 50000

    for i in range(100):
        if i < 30:
            # 하락 구간
            base = base * 0.99
        elif i < 70:
            # 상승 구간
            base = base * 1.01
        else:
            # 하락 구간
            base = base * 0.995
        prices.append(base)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })

    return df

def test_ma_cross():
    """MA 교차 테스트"""
    print("="*60)
    print("MA 교차 테스트")
    print("="*60)

    df = create_test_data()

    # 수동으로 MA 계산
    df['ma_20'] = df['close'].rolling(window=20).mean()
    df['ma_60'] = df['close'].rolling(window=60).mean()

    print("\n마지막 10개 데이터:")
    print(df[['date', 'close', 'ma_20', 'ma_60']].tail(10))

    # 교차점 찾기
    df['ma_20_prev'] = df['ma_20'].shift(1)
    df['ma_60_prev'] = df['ma_60'].shift(1)

    # 골든크로스: MA20이 MA60을 상향 돌파
    df['golden_cross'] = (
        (df['ma_20'] > df['ma_60']) &
        (df['ma_20_prev'] <= df['ma_60_prev'])
    )

    # 데드크로스: MA20이 MA60을 하향 돌파
    df['dead_cross'] = (
        (df['ma_20'] < df['ma_60']) &
        (df['ma_20_prev'] >= df['ma_60_prev'])
    )

    golden_crosses = df[df['golden_cross']]
    dead_crosses = df[df['dead_cross']]

    print(f"\n골든크로스: {len(golden_crosses)}개")
    for _, row in golden_crosses.iterrows():
        print(f"  {row['date']}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

    print(f"\n데드크로스: {len(dead_crosses)}개")
    for _, row in dead_crosses.iterrows():
        print(f"  {row['date']}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

    return df

def test_with_core():
    """Core 모듈로 테스트"""
    print("\n" + "="*60)
    print("Core 모듈 테스트")
    print("="*60)

    try:
        from core import compute_indicators, evaluate_conditions

        df = create_test_data()

        # Golden Cross 전략 설정
        indicators = [
            {"type": "ma", "params": {"period": 20}},
            {"type": "ma", "params": {"period": 60}}
        ]

        buy_conditions = [
            {"indicator": "ma_20", "operator": "cross_above", "value": "ma_60"}
        ]

        sell_conditions = [
            {"indicator": "ma_20", "operator": "cross_below", "value": "ma_60"}
        ]

        print("\n지표 계산...")
        df_with_ind = compute_indicators(df, indicators)

        # 생성된 컬럼 확인
        new_cols = [col for col in df_with_ind.columns if col not in df.columns]
        print(f"생성된 컬럼: {new_cols}")

        if 'ma_20' in df_with_ind.columns and 'ma_60' in df_with_ind.columns:
            print("\n마지막 10개 데이터:")
            print(df_with_ind[['date', 'close', 'ma_20', 'ma_60']].tail(10))

        print("\n신호 평가...")
        df_final = evaluate_conditions(df_with_ind, buy_conditions, sell_conditions)

        buy_signals = df_final['buy_signal'].sum()
        sell_signals = df_final['sell_signal'].sum()

        print(f"\n신호 개수:")
        print(f"  매수: {buy_signals}")
        print(f"  매도: {sell_signals}")

        if buy_signals > 0:
            print("\n매수 신호:")
            for _, row in df_final[df_final['buy_signal']].iterrows():
                print(f"  {row['date']}: close={row['close']:.0f}, MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

        if sell_signals > 0:
            print("\n매도 신호:")
            for _, row in df_final[df_final['sell_signal']].iterrows():
                print(f"  {row['date']}: close={row['close']:.0f}, MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

        # cross_above 동작 확인
        if buy_signals == 0 and sell_signals == 0:
            print("\n⚠️ 신호가 생성되지 않음!")
            print("\ncross_above 로직 테스트:")

            # 수동으로 cross_above 확인
            df_test = df_with_ind.copy()
            df_test['ma_20_prev'] = df_test['ma_20'].shift(1)
            df_test['ma_60_prev'] = df_test['ma_60'].shift(1)

            # 현재 MA20 > MA60 AND 이전 MA20 <= MA60
            df_test['manual_cross_above'] = (
                (df_test['ma_20'] > df_test['ma_60']) &
                (df_test['ma_20_prev'] <= df_test['ma_60_prev'])
            )

            manual_crosses = df_test[df_test['manual_cross_above']]
            print(f"수동 계산 cross_above: {len(manual_crosses)}개")

            if len(manual_crosses) > 0:
                print("Core 모듈의 cross_above 로직에 문제가 있을 수 있습니다.")

    except ImportError as e:
        print(f"❌ Core 모듈 로드 실패: {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

def test_backtest_engine():
    """백테스트 엔진 테스트"""
    print("\n" + "="*60)
    print("백테스트 엔진 테스트")
    print("="*60)

    try:
        from backtest_engine_advanced import AdvancedBacktestEngine

        df = create_test_data()

        # Golden Cross 전략
        strategy_config = {
            "templateId": "golden-cross",
            "indicators": [
                {"type": "ma", "params": {"period": 20}},
                {"type": "ma", "params": {"period": 60}}
            ],
            "buyConditions": [
                {"indicator": "ma_20", "operator": "cross_above", "value": "ma_60"}
            ],
            "sellConditions": [
                {"indicator": "ma_20", "operator": "cross_below", "value": "ma_60"}
            ]
        }

        engine = AdvancedBacktestEngine(
            initial_capital=10000000,
            commission=0.00015,
            slippage=0.001
        )

        print("백테스트 실행...")
        result = engine.run(df, strategy_config)

        print(f"\n결과:")
        print(f"  총 거래: {result['total_trades']}")
        print(f"  매수: {result.get('buy_count', 0)}")
        print(f"  매도: {result.get('sell_count', 0)}")
        print(f"  수익률: {result['total_return']:.2f}%")

        if result['trades']:
            print(f"\n거래 내역:")
            for trade in result['trades'][:5]:
                print(f"  {trade}")

    except ImportError as e:
        print(f"❌ 백테스트 엔진 로드 실패: {e}")
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 1. 수동 MA 교차 테스트
    test_ma_cross()

    # 2. Core 모듈 테스트
    test_with_core()

    # 3. 백테스트 엔진 테스트
    test_backtest_engine()

    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)