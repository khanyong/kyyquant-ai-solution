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

def check_history():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    target_code = '191600'
    print(f"=== Checking History for {target_code} ===")
    
    try:
        # Check Master info for name
        m_res = supabase.table('kw_stock_master').select('stock_name').eq('stock_code', target_code).execute()
        name = m_res.data[0]['stock_name'] if m_res.data else "Unknown"
        print(f"Stock Name: {name}")
        
        # Count daily price rows
        res = supabase.table('kw_price_daily').select('*', count='exact', head=True).eq('stock_code', target_code).execute()
        count = res.count
        print(f"Total Daily Rows: {count}")
        
        if count < 20:
             print("=> CONCLUSION: This is a newly listed stock or has data gaps.")
             # Get first and last date
             d_res = supabase.table('kw_price_daily').select('trade_date').eq('stock_code', target_code).order('trade_date', desc=False).execute()
             if d_res.data:
                 print(f"   Date Range: {d_res.data[0]['trade_date']} ~ {d_res.data[-1]['trade_date']}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_history()
