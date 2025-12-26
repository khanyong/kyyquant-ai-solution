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

def apply_fix():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Updating Strategy Configs ===")
    
    # 1. MACD Strategy
    macd_config = {
        "indicators": [
            {
                "id": "macd_1",
                "name": "MACD",
                "params": {"fast": 12, "slow": 26, "signal": 9}
            }
        ],
        "buyConditions": [
            {
                "indicator": "MACD",
                "compareTo": "MACD_SIGNAL",
                "operator": ">",
                "value": 0
            }
        ],
        "sellConditions": [
            {
                "indicator": "MACD",
                "compareTo": "MACD_SIGNAL",
                "operator": "<",
                "value": 0
            }
        ],
        "useStageBasedStrategy": False
    }
    
    print("Updating TEST_STRATEGY_A_MACD...")
    try:
        res = supabase.table('strategies').update({'config': macd_config}).eq('name', 'TEST_STRATEGY_A_MACD').execute()
        print(f"Update Result: {len(res.data)} rows updated.")
    except Exception as e:
        print(f"Error updating MACD: {e}")

    # 2. BB Strategy
    bb_config = {
        "indicators": [
            {
                "id": "bb_1",
                "name": "Bollinger Bands",
                "params": {"period": 20, "std_dev": 2}
            }
        ],
        "buyConditions": [
            {
                "indicator": "close",
                "compareTo": "BB_UPPER",
                "operator": "<",
                "value": 0
            }
        ],
        "sellConditions": [
            {
                "indicator": "close",
                "compareTo": "BB_MIDDLE",
                "operator": ">",
                "value": 0
            }
        ],
        "useStageBasedStrategy": False
    }
    
    print("Updating TEST_STRATEGY_B_BB...")
    try:
        res = supabase.table('strategies').update({'config': bb_config}).eq('name', 'TEST_STRATEGY_B_BB').execute()
        print(f"Update Result: {len(res.data)} rows updated.")
    except Exception as e:
        print(f"Error updating BB: {e}")

if __name__ == "__main__":
    apply_fix()
