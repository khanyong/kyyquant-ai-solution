"""
Core 함수 직접 테스트 - 골든크로스 신호 확인
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

# 2024년 데이터 조회
response = supabase.table('kw_price_daily').select('*').eq(
    'stock_code', '005930'
).gte('trade_date', '2024-01-01').lte('trade_date', '2024-12-31').order('trade_date').execute()

df = pd.DataFrame(response.data)
df['date'] = pd.to_datetime(df['trade_date'])
df = df.set_index('date')
print(f"데이터 로드: {len(df)}일")
print(f"기간: {df.index.min().date()} ~ {df.index.max().date()}")

# 골든크로스 전략 설정
strategy_config = {
    "indicators": [
        {"type": "ma", "params": {"period": 20}},
        {"type": "ma", "params": {"period": 60}}
    ]
}

# 지표 계산
df = compute_indicators(df, strategy_config)
print(f"\n=== 생성된 지표 컬럼 ===")
indicator_cols = [col for col in df.columns if col not in ['open', 'high', 'low', 'close', 'volume', 'trade_date', 'stock_code', 'created_at']]
print(indicator_cols)

# MA 값 확인
if 'ma_20' in df.columns and 'ma_60' in df.columns:
    print(f"\n=== MA 지표 통계 ===")
    print(f"MA20: {df['ma_20'].min():.0f} ~ {df['ma_20'].max():.0f}")
    print(f"MA60: {df['ma_60'].min():.0f} ~ {df['ma_60'].max():.0f}")

    # 수동으로 크로스 찾기 (NaN 제거)
    df['ma20_above'] = (df['ma_20'] > df['ma_60']).fillna(False)
    df['ma20_prev_above'] = df['ma20_above'].shift(1).fillna(False)

    # 골든크로스 찾기: 이전에는 MA20이 MA60 아래 있다가 현재는 위에 있는 경우
    golden_cross = df[(df['ma20_prev_above'] == False) & (df['ma20_above'] == True)]

    print(f"\n=== 수동 계산 골든크로스: {len(golden_cross)}개 ===")
    for idx, row in golden_cross.head(5).iterrows():
        print(f"{idx.date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}, Close={row['close']:.0f}")

# 조건 정규화
buy_conditions = [
    {
        "indicator": "ma_20",
        "operator": "cross_above",
        "value": "ma_60"
    }
]

sell_conditions = [
    {
        "indicator": "ma_20",
        "operator": "cross_below",
        "value": "ma_60"
    }
]

# 조건 정규화
buy_conditions = _normalize_conditions(buy_conditions)
sell_conditions = _normalize_conditions(sell_conditions)
print(f"\n=== 정규화된 조건 ===")
print(f"Buy: {buy_conditions}")
print(f"Sell: {sell_conditions}")

# 신호 평가
buy_signal = evaluate_conditions(df, buy_conditions, 'buy')
sell_signal = evaluate_conditions(df, sell_conditions, 'sell')

df['buy_signal'] = buy_signal
df['sell_signal'] = sell_signal

# 신호 통계
print(f"\n=== 신호 생성 결과 ===")
print(f"Buy 신호: {(buy_signal == 1).sum()}개")
print(f"Sell 신호: {(sell_signal == -1).sum()}개")

# Buy 신호 날짜
buy_dates = df[buy_signal == 1]
if len(buy_dates) > 0:
    print(f"\n=== Buy 신호 발생일 ===")
    for idx, row in buy_dates.head(5).iterrows():
        print(f"{idx.date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}, Close={row['close']:.0f}")

# 2024-07-02 근처 확인
july_data = df.loc['2024-06-28':'2024-07-05']
if len(july_data) > 0:
    print(f"\n=== 2024-07-02 근처 데이터 ===")
    print(july_data[['close', 'ma_20', 'ma_60', 'buy_signal', 'sell_signal']].round(0))