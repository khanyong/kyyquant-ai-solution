"""
2024년 삼성전자 MA 크로스 확인
"""
from dotenv import load_dotenv
import os
from supabase import create_client
import pandas as pd
import numpy as np

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

# MA 계산
df['MA20'] = df['close'].rolling(window=20).mean()
df['MA60'] = df['close'].rolling(window=60).mean()

# 크로스 찾기
df['MA20_prev'] = df['MA20'].shift(1)
df['MA60_prev'] = df['MA60'].shift(1)

# 골든크로스 (MA20이 MA60을 상향돌파)
golden_cross = df[(df['MA20_prev'] <= df['MA60_prev']) & (df['MA20'] > df['MA60'])]
print(f"=== 골든크로스 발생일 ({len(golden_cross)}개) ===")
for idx, row in golden_cross.iterrows():
    print(f"{idx.date()}: MA20={row['MA20']:.0f} > MA60={row['MA60']:.0f}")

# 데드크로스 (MA20이 MA60을 하향돌파)
dead_cross = df[(df['MA20_prev'] >= df['MA60_prev']) & (df['MA20'] < df['MA60'])]
print(f"\n=== 데드크로스 발생일 ({len(dead_cross)}개) ===")
for idx, row in dead_cross.iterrows():
    print(f"{idx.date()}: MA20={row['MA20']:.0f} < MA60={row['MA60']:.0f}")

# MA 차이 확인
df['MA_diff'] = df['MA20'] - df['MA60']
print(f"\n=== MA20-MA60 차이 통계 ===")
print(f"평균: {df['MA_diff'].mean():.0f}")
print(f"최대: {df['MA_diff'].max():.0f}")
print(f"최소: {df['MA_diff'].min():.0f}")

# 최근 데이터
print(f"\n=== 최근 10일 데이터 ===")
print(df[['close', 'MA20', 'MA60', 'MA_diff']].tail(10).round(0))