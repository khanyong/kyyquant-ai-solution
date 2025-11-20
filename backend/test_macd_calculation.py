"""
MACD 계산 직접 테스트
"""

from supabase import create_client
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv('.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, key)

# 1. MACD 지표 정의 가져오기
print("Step 1: Fetching MACD indicator definition...")
result = supabase.table('indicators').select('*').eq('name', 'macd').execute()

if not result.data:
    print("[ERROR] MACD indicator not found in database")
    exit(1)

indicator = result.data[0]
print(f"[OK] Found indicator: {indicator['name']}")
print(f"  Output columns: {indicator['output_columns']}")

formula = indicator['formula']
if isinstance(formula, str):
    import json
    formula = json.loads(formula)

code = formula.get('code', '')
print(f"\nCode:\n{code}\n")

# 2. 테스트 데이터 생성
print("Step 2: Creating test data...")
dates = pd.date_range('2024-01-01', periods=100, freq='D')
df = pd.DataFrame({
    'close': np.random.randn(100).cumsum() + 100
}, index=dates)

print(f"[OK] Test data created: {len(df)} rows")
print(f"  Columns: {list(df.columns)}")

# 3. MACD 코드 실행
print("\nStep 3: Executing MACD code...")

# 네임스페이스 준비
namespace = {
    'df': df.copy(),
    'pd': pd,
    'np': np,
    'params': {'fast': 12, 'slow': 26, 'signal': 9}
}

try:
    exec(code, namespace)

    result = namespace.get('result')

    if result is None:
        print("[ERROR] result is None")
        print(f"Namespace keys: {list(namespace.keys())}")
    elif isinstance(result, dict):
        print("[OK] result is dict")
        print(f"  Keys: {list(result.keys())}")
        for key, series in result.items():
            if isinstance(series, pd.Series):
                print(f"  {key}: {len(series)} values, first={series.iloc[0]:.4f}, last={series.iloc[-1]:.4f}")
            else:
                print(f"  {key}: type={type(series)}")
    else:
        print(f"[ERROR] result is wrong type: {type(result)}")

except Exception as e:
    print(f"[ERROR] Execution failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Test complete!")