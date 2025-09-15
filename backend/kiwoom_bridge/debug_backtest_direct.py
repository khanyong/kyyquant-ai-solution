"""
백테스트 직접 디버그
DB에서 전략을 가져와 직접 실행
"""

import os
import sys
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from supabase import create_client, Client

# 환경 변수 설정
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://kpnioqijldwmidguzwox.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtwbmlvcWlqbGR3bWlkZ3V6d294Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjY2NzY2NjgsImV4cCI6MjA0MjI1MjY2OH0.u8mE0Zii_TdN7Rwgehs83kYKVLWAuEz8sFYR2daJ4wA')

# Core 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import compute_indicators, evaluate_conditions

def get_strategy_from_db(strategy_id: str):
    """DB에서 전략 가져오기"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    result = supabase.table('strategies').select('*').eq('id', strategy_id).single().execute()

    if result.data:
        print(f"[SUCCESS] Strategy found: {result.data['name']}")
        return result.data
    else:
        print(f"[ERROR] Strategy not found: {strategy_id}")
        return None

def test_strategy_config(config):
    """전략 설정 테스트"""
    print("\n" + "="*60)
    print("전략 설정 분석")
    print("="*60)

    # indicators 확인
    indicators = config.get('indicators', [])
    print(f"\n[Indicators] {len(indicators)}개")
    for ind in indicators:
        print(f"  - Type: {ind.get('type')}, Params: {ind.get('params', {})}")

    # buyConditions 확인
    buy_conditions = config.get('buyConditions', [])
    print(f"\n[Buy Conditions] {len(buy_conditions)}개")
    for cond in buy_conditions:
        print(f"  - {cond.get('indicator')} {cond.get('operator')} {cond.get('value')}")

    # sellConditions 확인
    sell_conditions = config.get('sellConditions', [])
    print(f"\n[Sell Conditions] {len(sell_conditions)}개")
    for cond in sell_conditions:
        print(f"  - {cond.get('indicator')} {cond.get('operator')} {cond.get('value')}")

    return indicators, buy_conditions, sell_conditions

def simulate_backtest(config):
    """간단한 백테스트 시뮬레이션"""
    print("\n" + "="*60)
    print("백테스트 시뮬레이션")
    print("="*60)

    # 테스트 데이터 생성
    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    prices = 70000 + np.cumsum(np.random.randn(100) * 1000)

    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': [1000000] * 100
    })

    print(f"테스트 데이터: {len(df)}일")
    print(f"가격 범위: {prices.min():.0f} ~ {prices.max():.0f}")

    # 지표 계산
    print("\n지표 계산 중...")
    df = compute_indicators(df, config)

    # 계산된 지표 확인
    indicator_cols = [col for col in df.columns if col not in ['date', 'open', 'high', 'low', 'close', 'volume', 'price']]
    print(f"계산된 지표: {indicator_cols}")

    if indicator_cols:
        print("\n지표 값 샘플 (마지막 5일):")
        print(df[['date', 'close'] + indicator_cols].tail(5))

    # 매수/매도 신호 생성
    buy_conditions = config.get('buyConditions', [])
    sell_conditions = config.get('sellConditions', [])

    if buy_conditions:
        print("\n매수 신호 평가 중...")
        buy_signal = evaluate_conditions(df, buy_conditions, 'buy')
        buy_count = (buy_signal == 1).sum()
        print(f"매수 신호: {buy_count}개")

        if buy_count > 0:
            print("매수 신호 발생 시점:")
            print(df[buy_signal == 1][['date', 'close']].head())

    if sell_conditions:
        print("\n매도 신호 평가 중...")
        sell_signal = evaluate_conditions(df, sell_conditions, 'sell')
        sell_count = (sell_signal == -1).sum()
        print(f"매도 신호: {sell_count}개")

        if sell_count > 0:
            print("매도 신호 발생 시점:")
            print(df[sell_signal == -1][['date', 'close']].head())

    return df

def main():
    """메인 실행"""
    strategy_id = '88d01e47-c979-4e80-bef8-746a53f3bbca'

    print("="*60)
    print(f"전략 ID: {strategy_id}")
    print("="*60)

    # 1. DB에서 전략 가져오기
    strategy = get_strategy_from_db(strategy_id)

    if not strategy:
        print("[ERROR] 전략을 찾을 수 없습니다.")
        return

    config = strategy.get('config', {})

    # 2. 전략 설정 분석
    indicators, buy_conditions, sell_conditions = test_strategy_config(config)

    # 3. 문제 진단
    print("\n" + "="*60)
    print("문제 진단")
    print("="*60)

    problems = []

    if not indicators:
        problems.append("❌ indicators가 비어있음")

    if not buy_conditions:
        problems.append("❌ buyConditions가 비어있음")

    if not sell_conditions:
        problems.append("❌ sellConditions가 비어있음")

    # indicators 형식 확인
    for ind in indicators:
        if not ind.get('type'):
            problems.append(f"❌ indicator에 type이 없음: {ind}")
        if not ind.get('params') and not ind.get('period'):
            problems.append(f"⚠️  indicator에 params/period가 없음: {ind}")

    # conditions 형식 확인
    for cond in buy_conditions:
        if not cond.get('indicator'):
            problems.append(f"❌ buyCondition에 indicator가 없음: {cond}")
        if not cond.get('operator'):
            problems.append(f"❌ buyCondition에 operator가 없음: {cond}")

    if problems:
        print("발견된 문제:")
        for problem in problems:
            print(f"  {problem}")
    else:
        print("✅ 전략 설정에 명백한 문제 없음")

    # 4. 백테스트 시뮬레이션
    if indicators and (buy_conditions or sell_conditions):
        simulate_backtest(config)
    else:
        print("\n[WARNING] 지표나 조건이 없어 백테스트를 실행할 수 없습니다.")

    # 5. 올바른 설정 예시
    print("\n" + "="*60)
    print("올바른 설정 예시")
    print("="*60)

    correct_config = {
        "indicators": [
            {"type": "MA", "params": {"period": 20}},
            {"type": "MA", "params": {"period": 60}}
        ],
        "buyConditions": [
            {"indicator": "ma_20", "operator": ">", "value": "ma_60"}
        ],
        "sellConditions": [
            {"indicator": "ma_20", "operator": "<", "value": "ma_60"}
        ]
    }

    print(json.dumps(correct_config, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()