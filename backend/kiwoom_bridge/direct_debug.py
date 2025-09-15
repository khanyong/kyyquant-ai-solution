"""
직접 디버깅 - 실제 백테스트 과정 추적
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def direct_test():
    """가장 단순한 직접 테스트"""

    print("="*60)
    print("직접 백테스트 디버깅")
    print("="*60)

    # 1. 단순 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100)
    prices = []
    base = 50000

    # 명확한 추세 생성
    for i in range(100):
        if i < 30:
            base = base * 0.99  # 하락
        elif i < 70:
            base = base * 1.01  # 상승
        else:
            base = base * 0.99  # 하락
        prices.append(base)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })

    print(f"데이터: {len(df)}개 행")
    print(f"가격 범위: {min(prices):.0f} ~ {max(prices):.0f}")

    # 2. 가장 단순한 전략 - 이동평균 교차
    print("\n" + "="*40)
    print("전략: 5일/20일 이동평균 교차")
    print("="*40)

    # 수동으로 이동평균 계산
    df['ma_5'] = df['close'].rolling(window=5).mean()
    df['ma_20'] = df['close'].rolling(window=20).mean()

    print("\n이동평균 샘플 (20~30행):")
    print(df[['date', 'close', 'ma_5', 'ma_20']][20:30])

    # 3. 수동으로 신호 생성
    print("\n" + "="*40)
    print("신호 생성 (수동)")
    print("="*40)

    # 교차 찾기
    df['ma5_above'] = df['ma_5'] > df['ma_20']
    df['cross'] = df['ma5_above'] != df['ma5_above'].shift(1)

    # 골든크로스 (상향 교차)
    df['golden_cross'] = df['cross'] & df['ma5_above']
    # 데드크로스 (하향 교차)
    df['dead_cross'] = df['cross'] & ~df['ma5_above']

    golden_count = df['golden_cross'].sum()
    dead_count = df['dead_cross'].sum()

    print(f"골든크로스: {golden_count}개")
    print(f"데드크로스: {dead_count}개")

    if golden_count > 0:
        print("\n골든크로스 시점:")
        print(df[df['golden_cross']][['date', 'close', 'ma_5', 'ma_20']])

    if dead_count > 0:
        print("\n데드크로스 시점:")
        print(df[df['dead_cross']][['date', 'close', 'ma_5', 'ma_20']])

    # 4. 백테스트 시뮬레이션
    print("\n" + "="*40)
    print("백테스트 시뮬레이션")
    print("="*40)

    trades = []
    position = None
    capital = 10000000

    for i in range(len(df)):
        row = df.iloc[i]

        # 매수 신호
        if row['golden_cross'] and position is None:
            position = {
                'entry_price': row['close'],
                'entry_date': row['date'],
                'quantity': int(capital * 0.1 / row['close'])
            }
            trades.append({
                'date': row['date'],
                'action': 'BUY',
                'price': row['close']
            })
            print(f"[매수] {row['date'].date()}: {row['close']:.0f}원")

        # 매도 신호
        elif row['dead_cross'] and position is not None:
            profit_pct = ((row['close'] - position['entry_price']) / position['entry_price']) * 100
            trades.append({
                'date': row['date'],
                'action': 'SELL',
                'price': row['close'],
                'profit_pct': profit_pct
            })
            print(f"[매도] {row['date'].date()}: {row['close']:.0f}원 (수익률: {profit_pct:.2f}%)")
            position = None

    print(f"\n총 거래: {len(trades)}회")

    # 5. Core 모듈 테스트
    print("\n" + "="*40)
    print("Core 모듈 테스트")
    print("="*40)

    try:
        from core import compute_indicators, evaluate_conditions

        # 새 데이터프레임
        df2 = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [1000000] * 100
        })

        # 전략 설정
        config = {
            'indicators': [
                {'type': 'MA', 'params': {'period': 5}},
                {'type': 'MA', 'params': {'period': 20}}
            ]
        }

        # 지표 계산
        df2 = compute_indicators(df2, config)
        print(f"Core 지표 계산 후 컬럼: {list(df2.columns)}")

        # 조건 평가
        buy_conditions = [
            {'indicator': 'ma_5', 'operator': 'cross_above', 'value': 'ma_20'}
        ]
        sell_conditions = [
            {'indicator': 'ma_5', 'operator': 'cross_below', 'value': 'ma_20'}
        ]

        buy_signal = evaluate_conditions(df2, buy_conditions, 'buy')
        sell_signal = evaluate_conditions(df2, sell_conditions, 'sell')

        print(f"Core 매수 신호: {buy_signal.sum()}개")
        print(f"Core 매도 신호: {abs(sell_signal.sum())}개")

        if buy_signal.sum() == 0:
            print("\n[문제] Core 모듈에서도 신호가 생성되지 않음!")

            # 조건 직접 확인
            ma5_above = df2['ma_5'] > df2['ma_20']
            cross = ma5_above != ma5_above.shift(1)
            manual_buy = cross & ma5_above

            print(f"수동 계산 매수 신호: {manual_buy.sum()}개")

            if manual_buy.sum() > 0:
                print("=> cross_above 로직에 문제가 있음")
            else:
                print("=> 데이터에 교차가 없음")

    except ImportError as e:
        print(f"Core 모듈 임포트 실패: {e}")
    except Exception as e:
        print(f"Core 모듈 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

    # 6. 실제 백테스트 엔진 테스트
    print("\n" + "="*40)
    print("백테스트 엔진 테스트")
    print("="*40)

    try:
        from backtest_engine_advanced import AdvancedBacktestEngine

        engine = AdvancedBacktestEngine()

        # 단순 전략
        strategy = {
            'indicators': [
                {'type': 'MA', 'params': {'period': 5}},
                {'type': 'MA', 'params': {'period': 20}}
            ],
            'buyConditions': [
                {'indicator': 'close', 'operator': '>', 'value': 'ma_20'}
            ],
            'sellConditions': [
                {'indicator': 'close', 'operator': '<', 'value': 'ma_20'}
            ]
        }

        df3 = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [1000000] * 100
        })

        result = engine.run(df3, strategy)

        print(f"엔진 결과:")
        print(f"  총 거래: {result.get('total_trades', 0)}")
        print(f"  매수: {result.get('buy_count', 0)}")
        print(f"  매도: {result.get('sell_count', 0)}")

        if result.get('total_trades', 0) == 0:
            print("\n[문제] 백테스트 엔진에서도 거래가 발생하지 않음!")

    except Exception as e:
        print(f"백테스트 엔진 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

    return df


def check_imports():
    """모듈 임포트 상태 확인"""
    print("\n" + "="*40)
    print("모듈 임포트 확인")
    print("="*40)

    modules = [
        'core',
        'core.indicators',
        'core.signals',
        'core.naming',
        'backtest_engine_advanced',
        'strategy_engine'
    ]

    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")


if __name__ == "__main__":
    # 임포트 확인
    check_imports()

    # 직접 테스트
    df = direct_test()

    print("\n" + "="*60)
    print("디버깅 완료")
    print("="*60)
    print("\n가능한 원인:")
    print("1. cross_above/cross_below 연산자가 제대로 작동하지 않음")
    print("2. 지표 컬럼명이 여전히 일치하지 않음")
    print("3. 백테스트 엔진의 포지션 관리 로직 문제")
    print("4. 신호 생성 후 실제 거래 실행 조건 문제")