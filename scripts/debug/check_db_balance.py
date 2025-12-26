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

def check_balance():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Checking kw_account_balance (Latest 5) ===")
    try:
        res = supabase.table('kw_account_balance') \
            .select('updated_at, total_asset, deposit, available_cash') \
            .order('updated_at', desc=True) \
            .limit(5) \
            .execute()
            
        if not res.data:
            print("No balance data found.")
            return

        for row in res.data:
            print(f"Time: {row['updated_at']} | Total Asset: {row['total_asset']:,.0f} | Deposit: {row.get('deposit', 0):,.0f}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_balance()
