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

def check_status():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Checking Strategy Status ===")
    
    try:
        res = supabase.table('strategies').select('name, is_active, auto_trade_enabled').in_('name', ['TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB']).execute()
        
        if not res.data:
            print("Test strategies NOT FOUND.")
            return
            
        for s in res.data:
            print(f"Strategy: {s['name']}")
            print(f"  - is_active: {s['is_active']}")
            print(f"  - auto_trade_enabled: {s['auto_trade_enabled']}")
            
            if not s['auto_trade_enabled']:
                print("  => CAUSE: Visible on specific panels only if enabled.")

    except Exception as e:
        print(f"Error querying strategies: {e}")

if __name__ == "__main__":
    check_status()
