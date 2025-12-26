import os
import sys
import json
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

def insert_macd():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    macd_indicator = {
        "name": "macd",
        "display_name": "MACD",
        "description": "Moving Average Convergence Divergence",
        "category": "momentum",
        "calculation_type": "python_code",
        "formula": {
            "code": """
fast = int(params.get('fast', 12))
slow = int(params.get('slow', 26))
signal = int(params.get('signal', 9))

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
        "default_params": {"fast": 12, "slow": 26, "signal": 9},
        "required_data": ["close"],
        "output_columns": ["macd_line", "macd_signal", "macd_hist"],
        "is_active": True
    }

    print("=== Inserting 'macd' Indicator ===")
    
    # Check if exists
    try:
        res = supabase.table('indicators').select('id').eq('name', 'macd').execute()
        if res.data:
            print("MACD already exists. Updating...")
            supabase.table('indicators').update(macd_indicator).eq('name', 'macd').execute()
            print("Updated MACD.")
        else:
            print("Inserting MACD...")
            supabase.table('indicators').insert(macd_indicator).execute()
            print("Inserted MACD.")

    except Exception as e:
        print(f"Error inserting MACD: {e}")

    # Bollinger Bands
    bb_indicator = {
        "name": "bollinger",
        "display_name": "Bollinger Bands",
        "description": "Bollinger Bands",
        "category": "volatility",
        "calculation_type": "python_code",
        "formula": {
            "code": """
period = int(params.get('period', 20))
std_dev = float(params.get('std_dev', 2.0))

middle = df['close'].rolling(window=period, min_periods=period).mean()
std = df['close'].rolling(window=period, min_periods=period).std(ddof=0)

upper = middle + (std * std_dev)
lower = middle - (std * std_dev)

result = {
    'bollinger_upper': upper,
    'bollinger_middle': middle,
    'bollinger_lower': lower
}
"""
        },
        "default_params": {"period": 20, "std_dev": 2.0},
        "required_data": ["close"],
        "output_columns": ["bollinger_upper", "bollinger_middle", "bollinger_lower"],
        "is_active": True
    }

    print("=== Inserting 'bollinger' Indicator ===")
    try:
        res = supabase.table('indicators').select('id').eq('name', 'bollinger').execute()
        if res.data:
            print("Bollinger already exists. Updating...")
            supabase.table('indicators').update(bb_indicator).eq('name', 'bollinger').execute()
            print("Updated Bollinger.")
        else:
            print("Inserting Bollinger...")
            supabase.table('indicators').insert(bb_indicator).execute()
            print("Inserted Bollinger.")
            
    except Exception as e:
        print(f"Error inserting Bollinger: {e}")

if __name__ == "__main__":
    insert_macd()
