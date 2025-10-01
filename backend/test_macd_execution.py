"""
Test MACD code execution locally
"""

import pandas as pd
import numpy as np

# Create test data
dates = pd.date_range('2024-01-01', periods=100, freq='D')
df = pd.DataFrame({
    'close': np.random.randn(100).cumsum() + 100
}, index=dates)

print(f"Test data created: {len(df)} rows")
print(f"Columns: {list(df.columns)}")

# MACD code from Supabase
code = '''exp1 = df["close"].ewm(span=params.get("fast", 12), adjust=False).mean()
exp2 = df["close"].ewm(span=params.get("slow", 26), adjust=False).mean()
macd = exp1 - exp2
macd_signal = macd.ewm(span=params.get("signal", 9), adjust=False).mean()
macd_hist = macd - macd_signal
result = {"macd": macd, "macd_signal": macd_signal, "macd_hist": macd_hist}'''

print(f"\nCode to execute:\n{code}\n")

# Set up namespace
namespace = {
    'df': df.copy(),
    'pd': pd,
    'np': np,
    'params': {'fast': 12, 'slow': 26, 'signal': 9}
}

print(f"Params: {namespace['params']}")

# Execute
try:
    exec(code, namespace)

    result = namespace.get('result')

    print(f"\nResult type: {type(result)}")

    if result is None:
        print("[ERROR] Result is None!")
        print(f"Namespace keys: {list(namespace.keys())}")
    elif isinstance(result, dict):
        print(f"[OK] Result is dict with keys: {list(result.keys())}")
        for key, series in result.items():
            if isinstance(series, pd.Series):
                print(f"  {key}: {len(series)} values, first={series.iloc[0]:.4f}, last={series.iloc[-1]:.4f}")
    else:
        print(f"[ERROR] Result has unexpected type: {type(result)}")

except Exception as e:
    print(f"[ERROR] Execution failed: {e}")
    import traceback
    traceback.print_exc()