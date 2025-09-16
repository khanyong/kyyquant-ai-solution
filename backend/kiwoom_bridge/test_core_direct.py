"""
Core 모듈 직접 테스트 - 골든크로스 신호 확인
"""
import sys
sys.path.append('.')

from dotenv import load_dotenv
import os
from supabase import create_client
import pandas as pd
from core.indicators import compute_indicators
from core.signals import evaluate_conditions
from core.naming import _normalize_conditions
from datetime import datetime

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

# 1년 전체 데이터 조회 (2024-09-14 ~ 2025-09-12)
response = supabase.table('kw_price_daily').select('*').eq(
    'stock_code', '005930'
).gte('trade_date', '2024-09-14').lte('trade_date', '2025-09-12').order('trade_date').execute()

df = pd.DataFrame(response.data)
df['date'] = pd.to_datetime(df['trade_date'])
df = df.set_index('date')
print(f"데이터 로드: {len(df)}일")

# 골든크로스 전략 설정
strategy_config = {
    "indicators": [
        {"type": "ma", "params": {"period": 20}},
        {"type": "ma", "params": {"period": 60}}
    ],
    "buyConditions": [
        {
            "indicator": "ma_20",
            "operator": "cross_above",
            "value": "ma_60"
        }
    ],
    "sellConditions": [
        {
            "indicator": "ma_20",
            "operator": "cross_below",
            "value": "ma_60"
        }
    ]
}

# 지표 계산
df_with_signals = compute_indicators(df, strategy_config)

# 조건 정규화
buy_conditions = _normalize_conditions(strategy_config['buyConditions'])
sell_conditions = _normalize_conditions(strategy_config['sellConditions'])

print(f"\n=== 정규화된 조건 ===")
print(f"Buy: {buy_conditions}")
print(f"Sell: {sell_conditions}")

# 신호 평가
buy_signal = evaluate_conditions(df_with_signals, buy_conditions, 'buy')
sell_signal = evaluate_conditions(df_with_signals, sell_conditions, 'sell')

df_with_signals['buy_signal'] = buy_signal
df_with_signals['sell_signal'] = sell_signal

# 지표 확인
print(f"\n=== 생성된 컬럼 ===")
print([col for col in df_with_signals.columns if 'ma' in col.lower()])

# MA 지표 확인
if 'ma_20' in df_with_signals.columns and 'ma_60' in df_with_signals.columns:
    print(f"\nMA20 범위: {df_with_signals['ma_20'].min():.0f} ~ {df_with_signals['ma_20'].max():.0f}")
    print(f"MA60 범위: {df_with_signals['ma_60'].min():.0f} ~ {df_with_signals['ma_60'].max():.0f}")

    # 크로스 지점 찾기 (NaN 처리)
    df_with_signals = df_with_signals.dropna(subset=['ma_20', 'ma_60'])
    df_with_signals['ma20_above'] = df_with_signals['ma_20'] > df_with_signals['ma_60']
    df_with_signals['ma20_prev_above'] = df_with_signals['ma20_above'].shift(1).fillna(False)

    # 골든크로스 찾기
    golden_cross = df_with_signals[
        (~df_with_signals['ma20_prev_above']) & (df_with_signals['ma20_above'])
    ]
    print(f"\n=== 수동 계산 골든크로스: {len(golden_cross)}개 ===")
    for idx, row in golden_cross.iterrows():
        print(f"{idx.date()}: ma_20={row['ma_20']:.0f} > ma_60={row['ma_60']:.0f}")

# 신호 확인
print(f"\n=== Core 생성 신호 ===")
print(f"buy 신호 수: {(df_with_signals['buy_signal'] == 1).sum()}")
print(f"sell 신호 수: {(df_with_signals['sell_signal'] == -1).sum()}")

# buy 신호가 있는 날짜 출력
buy_signals = df_with_signals[df_with_signals['buy_signal'] == 1]
if len(buy_signals) > 0:
    print(f"\n=== Buy 신호 발생일 ===")
    for idx, row in buy_signals.iterrows():
        print(f"{idx.date()}: ma_20={row['ma_20']:.0f}, ma_60={row['ma_60']:.0f}")
else:
    print("\nCore가 buy 신호를 생성하지 못했습니다.")