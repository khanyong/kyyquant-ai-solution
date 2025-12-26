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

def verify_mapping():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Strategy - Universe Mapping ===")
    
    # RPC is the best way to see the effective linkage
    try:
        res = supabase.rpc('get_active_strategies_with_universe', {}).execute()
        
        for s in res.data:
            print(f"\nStrategy: {s.get('strategy_name')} ({s.get('strategy_id')})")
            
            # Check Top-Level Filter
            f_name = s.get('filter_name')
            f_id = s.get('filter_id')
            f_stocks = s.get('filtered_stocks')
            stock_count = len(f_stocks) if f_stocks else 0
            
            print(f"  -> Linked Filter (Universe): '{f_name}'")
            print(f"     - ID: {f_id}")
            print(f"     - Stock Count: {stock_count}")
            
            # Check Nested Universes (if any)
            if s.get('universes'):
                print(f"     - [Nested Universes Found: {len(s.get('universes'))}]")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_mapping()
