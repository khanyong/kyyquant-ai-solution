import os
import sys
from supabase import create_client

def manual_load_env():
    env_paths = ['.env', '.env.development']
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '=' in line:
                        key, val = line.split('=', 1)
                        os.environ[key.strip()] = val.strip()

def insert_indicators():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    # Define indicators to ensure
    indicators_to_add = [
        {
            "name": "MACD",
            "is_active": True,
            "description": "Moving Average Convergence Divergence",
            "calculation_type": "python_code",
            "formula": {
                "code": """
fast = params.get('fast', 12)
slow = params.get('slow', 26)
signal = params.get('signal', 9)

ema_fast = df['close'].ewm(span=fast, min_periods=fast, adjust=False).mean()
ema_slow = df['close'].ewm(span=slow, min_periods=slow, adjust=False).mean()

macd_line = ema_fast - ema_slow
macd_signal = macd_line.ewm(span=signal, min_periods=signal, adjust=False).mean()
macd_hist = macd_line - macd_signal

result = {
    'macd_line': macd_line,
    'macd_signal': macd_signal,
    'macd_hist': macd_hist
}
"""
            },
            "default_params": {"fast": 12, "slow": 26, "signal": 9}
        },
        {
            "name": "Bollinger Bands",
            "is_active": True,
            "description": "Bollinger Bands",
            "calculation_type": "python_code",
            "formula": {
                "code": """
period = params.get('period', 20)
std_dev = params.get('std_dev', 2)

middle = df['close'].rolling(window=period).mean()
std = df['close'].rolling(window=period).std(ddof=0)

upper = middle + (std * std_dev)
lower = middle - (std * std_dev)

result = {
    'bb_upper': upper,
    'bb_middle': middle,
    'bb_lower': lower
}
"""
            },
            "default_params": {"period": 20, "std_dev": 2}
        },
        {
            "name": "close",
            "is_active": True,
            "description": "Closing Price",
            "calculation_type": "python_code",
            "formula": {
                "code": "result = df['close']"
            },
            "default_params": {}
        }
    ]

    print("=== Ensuring Indicators Exist ===")
    
    # Fetch existing
    try:
        res = supabase.table('indicators').select('name').execute()
        existing_names = [row['name'] for row in res.data]
        print(f"Existing indicators: {existing_names}")
        
        for ind in indicators_to_add:
            if ind['name'] in existing_names:
                print(f"Skipping {ind['name']} (already exists)")
            else:
                print(f"Inserting {ind['name']}...")
                try:
                    supabase.table('indicators').insert(ind).execute()
                    print(f"Inserted {ind['name']}")
                except Exception as e:
                    print(f"Error inserting {ind['name']}: {e}")

    except Exception as e:
        print(f"Error checking indicators: {e}")

if __name__ == "__main__":
    insert_indicators()
