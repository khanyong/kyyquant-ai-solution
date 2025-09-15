"""
실제 Supabase 전략으로 백테스트 테스트
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
import yfinance as yf

# 환경변수 로드
load_dotenv()

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Supabase 연결
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("❌ Supabase 환경변수가 설정되지 않음")
    exit(1)

supabase = create_client(url, key)

def get_real_stock_data(symbol='005930.KS', period='6mo'):
    """실제 주식 데이터 가져오기 (삼성전자)"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        # 컬럼명 정리
        df = df.reset_index()
        df.columns = [col.lower() for col in df.columns]
        df = df.rename(columns={'date': 'date'})

        print(f"실제 데이터 로드: {symbol}")
        print(f"기간: {df['date'].min()} ~ {df['date'].max()}")
        print(f"데이터 개수: {len(df)}개")

        return df
    except Exception as e:
        print(f"❌ 실제 데이터 로드 실패: {e}")
        return None

def test_with_real_data():
    """실제 데이터로 테스트"""

    print("="*60)
    print("실제 주식 데이터로 백테스트 테스트")
    print("="*60)

    # 1. Supabase에서 골든크로스 전략 가져오기
    response = supabase.table('strategies').select("*").execute()

    golden_cross_strategy = None
    for strategy in response.data:
        if strategy.get('config', {}).get('templateId') == 'golden-cross':
            golden_cross_strategy = strategy
            break

    if not golden_cross_strategy:
        print("❌ 골든크로스 전략을 찾을 수 없음")
        return

    config = golden_cross_strategy['config']
    print(f"\n📊 전략: {golden_cross_strategy['name']}")
    print(f"Config: {json.dumps(config, indent=2, ensure_ascii=False)}")

    # 2. 실제 주식 데이터 가져오기
    df = get_real_stock_data('005930.KS', '6mo')  # 삼성전자 6개월

    if df is None:
        # 대체 데이터 생성
        print("\n대체 데이터 생성...")
        dates = pd.date_range(end=datetime.now(), periods=120)
        prices = []
        base = 70000

        # 교차가 확실히 발생하도록
        for i in range(120):
            if i < 40:
                base = base * 0.995  # 하락
            elif i < 80:
                base = base * 1.01   # 상승
            else:
                base = base * 0.995  # 하락
            prices.append(base)

        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [10000000] * 120
        })

    # 3. Core 모듈로 테스트
    try:
        from core import compute_indicators, evaluate_conditions

        print("\n🔧 지표 계산...")
        df_with_ind = compute_indicators(df, config)

        # 생성된 컬럼 확인
        new_cols = [col for col in df_with_ind.columns if col not in df.columns]
        print(f"생성된 컬럼: {new_cols}")

        # MA 값 확인
        if 'ma_20' in df_with_ind.columns and 'ma_60' in df_with_ind.columns:
            print("\nMA 값 (마지막 10개):")
            print(df_with_ind[['date', 'close', 'ma_20', 'ma_60']].tail(10))

            # 교차 수동 확인
            df_test = df_with_ind.copy()
            df_test['ma_20_prev'] = df_test['ma_20'].shift(1)
            df_test['ma_60_prev'] = df_test['ma_60'].shift(1)

            df_test['golden_cross'] = (
                (df_test['ma_20'] > df_test['ma_60']) &
                (df_test['ma_20_prev'] <= df_test['ma_60_prev'])
            )

            df_test['dead_cross'] = (
                (df_test['ma_20'] < df_test['ma_60']) &
                (df_test['ma_20_prev'] >= df_test['ma_60_prev'])
            )

            golden_count = df_test['golden_cross'].sum()
            dead_count = df_test['dead_cross'].sum()

            print(f"\n수동 교차 확인:")
            print(f"  골든크로스: {golden_count}개")
            print(f"  데드크로스: {dead_count}개")

        # 신호 평가
        print("\n🔧 신호 평가...")
        buy_conditions = config.get('buyConditions', [])
        sell_conditions = config.get('sellConditions', [])

        print(f"매수 조건: {buy_conditions}")
        print(f"매도 조건: {sell_conditions}")

        df_final = evaluate_conditions(df_with_ind, buy_conditions, sell_conditions)

        buy_signals = (df_final['buy_signal'] == 1).sum()
        sell_signals = (df_final['sell_signal'] == -1).sum()

        print(f"\n📊 신호 결과:")
        print(f"  매수 신호: {buy_signals}개")
        print(f"  매도 신호: {sell_signals}개")

        if buy_signals > 0:
            print("\n매수 신호 위치:")
            for _, row in df_final[df_final['buy_signal'] == 1].head(3).iterrows():
                print(f"  {row['date']}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

        # 4. 백테스트 엔진 테스트
        print("\n" + "="*60)
        print("백테스트 엔진 테스트")
        print("="*60)

        from backtest_engine_advanced import AdvancedBacktestEngine

        engine = AdvancedBacktestEngine(
            initial_capital=10000000,
            commission=0.00015,
            slippage=0.001
        )

        result = engine.run(df, config)

        print(f"\n백테스트 결과:")
        print(f"  총 거래: {result['total_trades']}")
        print(f"  매수: {result.get('buy_count', 0)}")
        print(f"  매도: {result.get('sell_count', 0)}")
        print(f"  수익률: {result['total_return']:.2f}%")

    except Exception as e:
        print(f"\n❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_real_data()