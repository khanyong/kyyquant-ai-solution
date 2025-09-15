"""
백테스트 디버깅 스크립트
거래가 0회인 문제를 상세히 추적
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Supabase 연결
from supabase import create_client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Supabase 환경변수가 설정되지 않음")
    exit(1)

supabase = create_client(url, key)

def get_strategy_from_supabase(strategy_name="골든크로스 전략"):
    """Supabase에서 전략 가져오기"""
    response = supabase.table('strategies').select("*").eq('name', strategy_name).execute()

    if response.data:
        strategy = response.data[0]
        print(f"\n📊 전략: {strategy['name']}")
        print(f"Config: {json.dumps(strategy['config'], indent=2, ensure_ascii=False)}")
        return strategy['config']
    else:
        print(f"❌ '{strategy_name}' 전략을 찾을 수 없음")
        return None

def test_backtest_with_strategy():
    """실제 Supabase 전략으로 백테스트 실행"""

    print("="*60)
    print("백테스트 디버깅 시작")
    print("="*60)

    # 1. Supabase에서 전략 가져오기
    strategy_config = get_strategy_from_supabase("골든크로스 전략")

    if not strategy_config:
        # 대체 전략 시도
        strategy_config = get_strategy_from_supabase("RSI 반전 전략")

    if not strategy_config:
        print("❌ 전략을 찾을 수 없음")
        return

    # 2. 테스트 데이터 생성
    print("\n📈 테스트 데이터 생성...")
    dates = pd.date_range('2024-01-01', periods=100)
    prices = []
    base = 50000

    # 명확한 골든크로스/데드크로스 패턴 생성
    for i in range(100):
        if i < 30:
            base = base * 0.98  # 하락
        elif i < 70:
            base = base * 1.02  # 상승
        else:
            base = base * 0.99  # 소폭 하락
        prices.append(base)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': [1000000] * 100
    })

    print(f"데이터 shape: {df.shape}")
    print(f"가격 범위: {df['close'].min():.0f} ~ {df['close'].max():.0f}")

    # 3. Core 모듈 임포트 및 실행
    try:
        from core import compute_indicators, evaluate_conditions, _normalize_conditions
        print("\n✅ Core 모듈 로드 성공")

        # 3-1. 지표 계산
        print("\n🔧 지표 계산 중...")
        print(f"indicators 배열: {strategy_config.get('indicators', [])}")

        df_with_indicators = compute_indicators(df, strategy_config.get('indicators', []))

        # 생성된 컬럼 확인
        indicator_cols = [col for col in df_with_indicators.columns
                         if col not in ['date', 'open', 'high', 'low', 'close', 'volume']]
        print(f"\n생성된 지표 컬럼: {indicator_cols}")

        if indicator_cols:
            print("\n지표 값 샘플 (마지막 5개):")
            print(df_with_indicators[['close'] + indicator_cols].tail())

        # 3-2. 조건 정규화
        print("\n🔧 조건 정규화...")
        buy_conditions = _normalize_conditions(strategy_config.get('buyConditions', []))
        sell_conditions = _normalize_conditions(strategy_config.get('sellConditions', []))

        print(f"정규화된 매수 조건: {buy_conditions}")
        print(f"정규화된 매도 조건: {sell_conditions}")

        # 3-3. 신호 평가
        print("\n🔧 신호 평가...")
        df_with_signals = evaluate_conditions(
            df_with_indicators,
            buy_conditions,
            sell_conditions
        )

        # 신호 확인
        buy_signals = df_with_signals['buy_signal'].sum()
        sell_signals = df_with_signals['sell_signal'].sum()

        print(f"\n📊 신호 생성 결과:")
        print(f"  매수 신호: {buy_signals}개")
        print(f"  매도 신호: {sell_signals}개")

        if buy_signals > 0:
            print("\n매수 신호 위치:")
            buy_dates = df_with_signals[df_with_signals['buy_signal']]['date']
            for date in buy_dates:
                print(f"  - {date}")

        if sell_signals > 0:
            print("\n매도 신호 위치:")
            sell_dates = df_with_signals[df_with_signals['sell_signal']]['date']
            for date in sell_dates:
                print(f"  - {date}")

        # 3-4. signal 컬럼 확인
        if 'signal' in df_with_signals.columns:
            total_signals = (df_with_signals['signal'] != 0).sum()
            print(f"\n전체 signal 컬럼: {total_signals}개")

        # 4. 백테스트 엔진 테스트
        try:
            from backtest_engine_advanced import AdvancedBacktestEngine

            print("\n📊 백테스트 엔진 실행...")
            engine = AdvancedBacktestEngine(
                initial_capital=10000000,
                commission=0.00015,
                slippage=0.001
            )

            # 백테스트 실행
            result = engine.run(df_with_signals, strategy_config)

            print(f"\n📈 백테스트 결과:")
            print(f"  총 수익률: {result['total_return']:.2f}%")
            print(f"  총 거래 수: {result['total_trades']}")
            print(f"  매수 횟수: {result.get('buy_count', 0)}")
            print(f"  매도 횟수: {result.get('sell_count', 0)}")

            if result['trades']:
                print(f"\n거래 내역 (처음 3개):")
                for trade in result['trades'][:3]:
                    print(f"  {trade}")

        except ImportError as e:
            print(f"\n❌ 백테스트 엔진 로드 실패: {e}")

    except ImportError as e:
        print(f"\n❌ Core 모듈 로드 실패: {e}")

        # Legacy 방식 테스트
        print("\n🔧 Legacy 방식으로 테스트...")
        try:
            from backtest_api import Strategy
            import asyncio

            result = asyncio.run(Strategy.execute_strategy(df, strategy_config))

            if 'signal' in result.columns:
                buy_count = (result['signal'] == 1).sum()
                sell_count = (result['signal'] == -1).sum()
                print(f"\nLegacy 신호: 매수 {buy_count}, 매도 {sell_count}")

        except Exception as e:
            print(f"❌ Legacy 방식도 실패: {e}")

def check_column_names():
    """생성되는 컬럼명 확인"""
    print("\n" + "="*60)
    print("컬럼명 매칭 테스트")
    print("="*60)

    # MA 지표 테스트
    test_cases = [
        {"indicator": "ma_20", "expected_column": "ma_20"},
        {"indicator": "MA_20", "expected_column": "ma_20"},
        {"indicator": "ma_60", "expected_column": "ma_60"},
        {"indicator": "rsi_14", "expected_column": "rsi_14"},
        {"indicator": "RSI_14", "expected_column": "rsi_14"},
    ]

    for test in test_cases:
        # 정규화
        normalized = test['indicator'].lower()
        print(f"{test['indicator']} → {normalized} (예상: {test['expected_column']})")

        if normalized == test['expected_column']:
            print("  ✅ 매칭 성공")
        else:
            print("  ❌ 매칭 실패")

if __name__ == "__main__":
    # 1. Supabase 전략으로 백테스트
    test_backtest_with_strategy()

    # 2. 컬럼명 매칭 테스트
    check_column_names()

    print("\n" + "="*60)
    print("디버깅 완료")
    print("="*60)