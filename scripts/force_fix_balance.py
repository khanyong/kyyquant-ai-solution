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

def fix_balance_force():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    supabase = create_client(url, key)
    
    print("=== Force Updating Balance ===")
    
    try:
        # We know the account_number is 'MANUAL_SYNC' from previous script
        supabase.table('kw_account_balance').update({
            'total_asset': 9728340,
            'deposit': 9728340,
            'available_cash': 4864170
        }).eq('account_number', 'MANUAL_SYNC').execute()
        print("✅ Account Balance Force Updated to 9,728,340 KRW")
    except Exception as e:
        print(f"❌ Force Update Error: {e}")

if __name__ == "__main__":
    fix_balance_force()
