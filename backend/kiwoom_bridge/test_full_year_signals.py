"""
전체 연도 신호 테스트
"""
from dotenv import load_dotenv
import os
from supabase import create_client
import pandas as pd
from core.indicators import compute_indicators
from core.signals import evaluate_conditions
from core.naming import _normalize_conditions

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

# 2024년 전체 데이터 조회
response = supabase.table('kw_price_daily').select('*').eq(
    'stock_code', '005930'
).gte('trade_date', '2024-01-01').lte('trade_date', '2024-12-31').order('trade_date').execute()

df = pd.DataFrame(response.data)
df['date'] = pd.to_datetime(df['trade_date'])
df = df.set_index('date')
print(f"데이터 로드: {len(df)}일")

# 골든크로스 전략 설정
strategy_config = {
    "indicators": [
        {"type": "ma", "params": {"period": 20}},
        {"type": "ma", "params": {"period": 60}}
    ]
}

# 지표 계산
df = compute_indicators(df, strategy_config)

# 조건 정규화
buy_conditions = _normalize_conditions([
    {
        "indicator": "ma_20",
        "operator": "cross_above",
        "value": "ma_60"
    }
])

sell_conditions = _normalize_conditions([
    {
        "indicator": "ma_20",
        "operator": "cross_below",
        "value": "ma_60"
    }
])

# 신호 평가
buy_signal = evaluate_conditions(df, buy_conditions, 'buy')
sell_signal = evaluate_conditions(df, sell_conditions, 'sell')

df['buy_signal'] = buy_signal
df['sell_signal'] = sell_signal

print(f"\n=== 신호 생성 결과 ===")
print(f"Buy 신호: {(buy_signal == 1).sum()}개")
print(f"Sell 신호: {(sell_signal == -1).sum()}개")

# 7월 2일 근처 데이터 확인
july_data = df.loc['2024-06-28':'2024-07-05']
print(f"\n=== 7월 2일 근처 데이터 ===")
print(july_data[['close', 'ma_20', 'ma_60', 'buy_signal', 'sell_signal']].round(0))

# 매수 신호 날짜
buy_dates = df[df['buy_signal'] == 1]
if len(buy_dates) > 0:
    print(f"\n=== 매수 신호 발생일 ===")
    for idx, row in buy_dates.iterrows():
        print(f"{idx.date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

# 매도 신호 날짜
sell_dates = df[df['sell_signal'] == -1]
if len(sell_dates) > 0:
    print(f"\n=== 매도 신호 발생일 ===")
    for idx, row in sell_dates.iterrows():
        print(f"{idx.date()}: MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")