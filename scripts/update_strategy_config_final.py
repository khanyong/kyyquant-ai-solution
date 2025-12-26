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

def update_strategies():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    # 1. MACD Strategy
    macd_config = {
        "indicators": [
            {
                "id": "macd_1",
                "name": "macd",  # Changed from MACD to macd
                "params": {"fast": 12, "slow": 26, "signal": 9}
            }
        ],
        "buyConditions": [
            {
                "left": {"type": "indicator", "id": "macd_1", "key": "macd_hist"},
                "operator": ">",
                "right": {"type": "constant", "value": 0}
            }
        ],
        "sellConditions": [
            {
                "left": {"type": "indicator", "id": "macd_1", "key": "macd_hist"},
                "operator": "<",
                "right": {"type": "constant", "value": 0}
            }
        ]
    }

    print("Updating TEST_STRATEGY_A_MACD config...")
    try:
        supabase.table('strategies').update({'config': macd_config}).eq('name', 'TEST_STRATEGY_A_MACD').execute()
        print("Updated TEST_STRATEGY_A_MACD")
    except Exception as e:
        print(f"Error updating MACD strategy: {e}")

    # 2. Bollinger Strategy
    bb_config = {
        "indicators": [
            {
                "id": "bb_1",
                "name": "bollinger", # Changed from Bollinger Bands to bollinger
                "params": {"period": 20, "std_dev": 2} # Changed default_params to params to match usage
            }
        ],
        "buyConditions": [
            {
                "left": {"type": "price", "key": "close"},
                "operator": "<",
                "right": {"type": "indicator", "id": "bb_1", "key": "bollinger_lower"} # Changed bb_lower to bollinger_lower (from output_columns)
            }
        ],
        "sellConditions": [
            {
                "left": {"type": "price", "key": "close"},
                "operator": ">",
                "right": {"type": "indicator", "id": "bb_1", "key": "bollinger_upper"} # Changed bb_upper to bollinger_upper
            }
        ]
    }

    print("Updating TEST_STRATEGY_B_BB config...")
    try:
        supabase.table('strategies').update({'config': bb_config}).eq('name', 'TEST_STRATEGY_B_BB').execute()
        print("Updated TEST_STRATEGY_B_BB")
    except Exception as e:
        print(f"Error updating BB strategy: {e}")

if __name__ == "__main__":
    update_strategies()
