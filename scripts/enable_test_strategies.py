import os
import sys
# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')
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

def enable_strategies():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Enabling Test Strategies ===")
    
    strategies = ['TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB']
    
    for s_name in strategies:
        try:
            supabase.table('strategies').update({'auto_trade_enabled': True}).eq('name', s_name).execute()
            print(f"✅ Enabled auto_trade for: {s_name}")
        except Exception as e:
            print(f"Error updating {s_name}: {e}")

if __name__ == "__main__":
    enable_strategies()
