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

def check_filters():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Checking Investment Filters ===")
    
    try:
        res = supabase.table('kw_investment_filters').select('*').execute()
        if not res.data:
            print("No filters found.")
            return
            
        for f in res.data:
            print(f"Filter: {f['name']}")
            print(f"  - Count: {f.get('filtered_stocks_count')}")
            stocks = f.get('filtered_stocks')
            print(f"  - Stocks Data Type: {type(stocks)}")
            print(f"  - Stocks Content: {stocks}")
            if isinstance(stocks, list) and len(stocks) > 0:
                print(f"  - First Item: {stocks[0]} (Type: {type(stocks[0])})")

    except Exception as e:
        print(f"Error querying filters: {e}")

if __name__ == "__main__":
    check_filters()
