"""
신호 컬럼 확인 테스트
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

# 2024년 7월 근처 데이터만 조회
response = supabase.table('kw_price_daily').select('*').eq(
    'stock_code', '005930'
).gte('trade_date', '2024-06-25').lte('trade_date', '2024-07-10').order('trade_date').execute()

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

# 결과 출력
print("\n=== 7월 2일 근처 데이터 ===")
cols = ['close', 'ma_20', 'ma_60', 'buy_signal', 'sell_signal']
print(df[cols].round(0))

# 매수 신호 확인
buy_dates = df[df['buy_signal'] == 1]
if len(buy_dates) > 0:
    print(f"\n=== 매수 신호 발생 ===")
    for idx, row in buy_dates.iterrows():
        print(f"{idx.date()}: buy_signal={row['buy_signal']}, MA20={row['ma_20']:.0f}, MA60={row['ma_60']:.0f}")

# buy_signal 타입 확인
print(f"\n=== buy_signal 컬럼 정보 ===")
print(f"dtype: {df['buy_signal'].dtype}")
print(f"unique values: {df['buy_signal'].unique()}")
print(f"sum: {df['buy_signal'].sum()}")

# 7월 2일 확인
if '2024-07-02' in df.index.strftime('%Y-%m-%d'):
    july2 = df.loc['2024-07-02']
    print(f"\n=== 2024-07-02 상세 ===")
    print(f"buy_signal 값: {july2['buy_signal']} (type: {type(july2['buy_signal'])})")
    print(f"sell_signal 값: {july2['sell_signal']} (type: {type(july2['sell_signal'])})")
    print(f"MA20 > MA60: {july2['ma_20'] > july2['ma_60']}")