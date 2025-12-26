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

def fix_user_ids():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Fixing Missing User IDs ===")
    
    # 1. Get the valid User ID (known from previous steps, or query one that exists)
    # We know 169b... is valid. But let's find one dynamically to be safe.
    valid_uid = None
    res = supabase.table('kw_account_balance').select('user_id').limit(1).execute()
    if res.data:
        valid_uid = res.data[0]['user_id']
    
    if not valid_uid:
        print("❌ Could not find any valid user_id in kw_account_balance. Using hardcoded fallback.")
        valid_uid = "169b7101-19fd-4aa3-a63f-2d610b86ce9e"
    
    print(f"Using User ID: {valid_uid}")
    
    # 2. Update Test Strategies
    strategies = ['TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB']
    
    for s_name in strategies:
        try:
            # Check current user_id
            check = supabase.table('strategies').select('user_id').eq('name', s_name).execute()
            current_uid = check.data[0].get('user_id') if check.data else None
            
            if current_uid is None:
                print(f"Strategy {s_name} has NO User ID. Updating...")
                supabase.table('strategies').update({'user_id': valid_uid}).eq('name', s_name).execute()
                print(f"✅ Updated {s_name} with User ID.")
            else:
                print(f"Strategy {s_name} already has User ID: {current_uid}")
                
        except Exception as e:
            print(f"Error updating {s_name}: {e}")

if __name__ == "__main__":
    fix_user_ids()
