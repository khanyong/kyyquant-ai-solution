import os
import sys
# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')
from supabase import create_client

def manual_load_env():
    env_path = '.env.development'
    if not os.path.exists(env_path):
        env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

def check_universe():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Checking Investment Universe Size ===")
    
    # 1. Total Stocks in Price Table (Approximation of Universe)
    try:
        # Check KOSPI
        # Note: kw_price_current might not have 'market' column directly, checking schema often needed.
        # Assuming we can inspect first few to see formatting or if there is a 'market_type'
        
        # Let's count all
        count = supabase.table('kw_price_current').select('*', count='exact', head=True).execute()
        print(f"Total Stocks Monitored (kw_price_current): {count.count}")
        
        # Get one row to inspect columns
        sample = supabase.table('kw_price_current').select('*').limit(1).execute()
        if sample.data:
            print(f"Sample Row Keys: {list(sample.data[0].keys())}")
            print(f"Sample Row: {sample.data[0]}")
            
    except Exception as e:
        print(f"Error querying db: {e}")

if __name__ == "__main__":
    check_universe()
