import os
import sys
import json
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

def verify_rpc():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Checking RPC Output ===")
    
    try:
        res = supabase.rpc('get_active_strategies_with_universe', {}).execute()
        if not res.data:
            print("RPC returned NO data (Empty List). Strategies might not be active.")
            return
            
        print(f"RPC returned {len(res.data)} rows.")
        
        for item in res.data:
            s_name = item.get('strategy_name')
            f_name = item.get('filter_name')
            stocks = item.get('filtered_stocks')
            
            print(f"\nStrategy: {s_name}")
            print(f"  - Filter: {f_name}")
            
            if stocks is None:
                print("  - Stocks: NULL")
            elif isinstance(stocks, list):
                print(f"  - Stocks Count: {len(stocks)}")
                if len(stocks) > 0:
                    print(f"  - First 3: {stocks[:3]}")
            else:
                print(f"  - Stocks Type: {type(stocks)}")
                print(f"  - Content: {stocks}")

    except Exception as e:
        print(f"RPC Error: {e}")

    print("\n=== Checking Strategy Monitoring (n8n Output) ===")
    try:
        # Count rows in strategy_monitoring
        count = supabase.table('strategy_monitoring').select('*', count='exact', head=True).execute()
        print(f"Total Monitored Items: {count.count}")
        
        # Check breakdown by strategy
        res = supabase.table('strategy_monitoring').select('strategy_id, stock_name').limit(10).execute()
        if res.data:
            print("Sample Data Exists. n8n is likely working.")
        else:
            print("No data in strategy_monitoring. n8n might not have finished or failed.")

    except Exception as e:
        print(f"Error checking monitoring: {e}")

if __name__ == "__main__":
    verify_rpc()
