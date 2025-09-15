"""
로컬에서 전략 테스트
Supabase 데이터를 직접 확인하고 백테스트 실행
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

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

def test_strategy_from_supabase():
    """Supabase에서 전략을 가져와 테스트"""

    print("="*60)
    print("Supabase 전략 테스트")
    print("="*60)

    # 1. Golden Cross 전략 가져오기
    response = supabase.table('strategies').select("*").eq('name', '골든크로스 전략').execute()

    if not response.data:
        print("❌ 골든크로스 전략을 찾을 수 없음")
        # 대체 전략 시도
        response = supabase.table('strategies').select("*").limit(1).execute()
        if not response.data:
            print("❌ 전략이 없음")
            return

    strategy = response.data[0]
    config = strategy.get('config', {})

    print(f"\n📊 전략: {strategy.get('name')}")
    print(f"Template ID: {config.get('templateId')}")

    # 2. Config 상세 출력
    print("\n📋 Config 내용:")
    print(json.dumps(config, indent=2, ensure_ascii=False))

    # 3. indicators 확인
    indicators = config.get('indicators', [])
    print(f"\n🔍 Indicators ({len(indicators)}개):")
    for ind in indicators:
        print(f"  - {ind}")

    if not indicators:
        print("  ⚠️ indicators가 비어있음!")

    # 4. 조건 확인
    buy_conditions = config.get('buyConditions', [])
    sell_conditions = config.get('sellConditions', [])

    print(f"\n📈 매수 조건 ({len(buy_conditions)}개):")
    for cond in buy_conditions:
        print(f"  - {cond}")

    print(f"\n📉 매도 조건 ({len(sell_conditions)}개):")
    for cond in sell_conditions:
        print(f"  - {cond}")

    # 5. 테스트 데이터로 백테스트
    print("\n" + "="*60)
    print("백테스트 실행")
    print("="*60)

    # 테스트 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100)
    prices = []
    base = 50000

    # 명확한 패턴 생성
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

    print(f"테스트 데이터: {len(df)}일")
    print(f"가격 범위: {df['close'].min():.0f} ~ {df['close'].max():.0f}")

    # 6. Core 모듈로 실행
    try:
        from core import compute_indicators, evaluate_conditions, _normalize_conditions

        print("\n✅ Core 모듈 사용")

        # 지표 계산
        df_with_ind = compute_indicators(df, indicators)

        # 생성된 컬럼
        new_cols = [col for col in df_with_ind.columns if col not in df.columns]
        print(f"\n생성된 지표 컬럼: {new_cols}")

        if new_cols:
            print("\n지표 값 샘플:")
            print(df_with_ind[['close'] + new_cols].tail(5))

        # 조건 정규화
        norm_buy = _normalize_conditions(buy_conditions)
        norm_sell = _normalize_conditions(sell_conditions)

        print(f"\n정규화된 매수 조건: {norm_buy}")
        print(f"정규화된 매도 조건: {norm_sell}")

        # 신호 평가
        df_final = evaluate_conditions(df_with_ind, norm_buy, norm_sell)

        buy_signals = df_final['buy_signal'].sum()
        sell_signals = df_final['sell_signal'].sum()

        print(f"\n📊 신호 생성 결과:")
        print(f"  매수 신호: {buy_signals}개")
        print(f"  매도 신호: {sell_signals}개")

        if buy_signals > 0:
            print("\n매수 신호 날짜:")
            for idx, row in df_final[df_final['buy_signal']].iterrows():
                print(f"  - {row['date']}: close={row['close']:.0f}")

        if sell_signals > 0:
            print("\n매도 신호 날짜:")
            for idx, row in df_final[df_final['sell_signal']].iterrows():
                print(f"  - {row['date']}: close={row['close']:.0f}")

    except ImportError as e:
        print(f"\n❌ Core 모듈 로드 실패: {e}")
    except Exception as e:
        print(f"\n❌ 실행 오류: {e}")
        import traceback
        traceback.print_exc()

def check_all_strategies():
    """모든 전략의 indicators 상태 확인"""

    print("\n" + "="*60)
    print("모든 전략 상태 확인")
    print("="*60)

    response = supabase.table('strategies').select("*").execute()

    if not response.data:
        print("❌ 전략이 없음")
        return

    strategies = response.data
    print(f"\n총 {len(strategies)}개 전략")

    # 통계
    with_indicators = 0
    without_indicators = 0

    for strategy in strategies:
        config = strategy.get('config', {})
        indicators = config.get('indicators', [])

        if indicators and len(indicators) > 0:
            with_indicators += 1
        else:
            without_indicators += 1
            print(f"\n⚠️ {strategy.get('name')}: indicators 비어있음")
            print(f"   Template: {config.get('templateId')}")

    print(f"\n📊 통계:")
    print(f"  indicators 있음: {with_indicators}개")
    print(f"  indicators 없음: {without_indicators}개")

    if without_indicators > 0:
        print("\n⚠️ SQL 수정이 제대로 적용되지 않았습니다.")
        print("   fix_strategies.sql을 다시 실행하세요.")

if __name__ == "__main__":
    # 1. 특정 전략 테스트
    test_strategy_from_supabase()

    # 2. 모든 전략 상태 확인
    check_all_strategies()