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

def run_sql_logic():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Running Manual Allocation Fix ===")
    
    # 1. Get a user_id
    user_res = supabase.table('strategies').select('user_id').limit(1).execute()
    if not user_res.data:
        print("No strategies found to get user_id from.")
        return
    user_id = user_res.data[0]['user_id']
    
    print(f"Target User: {user_id}")
    
    # 2. Update/Insert Account Balance
    try:
        supabase.table('kw_account_balance').upsert({
            'user_id': user_id,
            'account_number': 'MANUAL_SYNC',
            'total_asset': 9728340,  # [Updated] User Correction
            'available_cash': 4864170, # 50%
            'deposit': 9728340,
            'updated_at': 'now()'
        }).execute()
        print("✅ Account Balance Updated to 9,728,340 KRW")
    except Exception as e:
        print(f"❌ Balance Update Error: {e}")

    # 3. Update Strategies
    target_alloc = 4864170 # 50% of 9,728,340
    strategies = ['TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB']
    
    for s in strategies:
        try:
            supabase.table('strategies').update({
                'allocated_capital': target_alloc,
                'allocated_percent': 0.5
            }).eq('name', s).execute()
            print(f"✅ Strategy {s} updated to {target_alloc:,} KRW")
        except Exception as e:
            print(f"❌ Strategy {s} Update Error: {e}")

if __name__ == "__main__":
    run_sql_logic()
