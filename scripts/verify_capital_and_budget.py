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
                        # Remove quotes if present
                        val = val.strip("'").strip('"')
                        os.environ[key.strip()] = val

def verify_budget():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Strategy Capital Status Verification ===")
    
    # 1. Query strategy_capital_status View
    # Note: If view is not directly exposed to API, we might need to query 'strategies' and calculate,
    # or query the view if enabled. Let's try querying the view.
    try:
        res = supabase.table('strategy_capital_status').select('*').execute()
        if not res.data:
            # Fallback: Query strategies directly if view is empty/inaccessible
            print("[Info] View empty or inaccessible. Querying 'strategies' table directly.")
            res = supabase.table('strategies').select('id, name, allocated_capital, allocated_percent').execute()
            
        data = res.data
        if not data:
            print("No strategies found.")
            return
            
        for s in data:
            name = s.get('strategy_name') or s.get('name')
            alloc = s.get('allocated_capital')
            pct = s.get('allocated_percent')
            remaining = s.get('remaining_capital') # Might be None if querying strategies table
            
            print(f"  - Allocated: {alloc:,} KRW (Target: {pct*100}%)")
            
            # Check user_id in table
            uid = s.get('user_id')
            print(f"  - Table User ID: {uid}")

            if remaining is not None:
                print(f"  - Remaining Budget: {remaining:,} KRW")
            else:
                # If querying 'strategies' table, we assume remaining = allocated for new strategies
                # But we should check orders.
                print(f"  - (View not used) Assumed Budget: {alloc:,} KRW (Minus active orders)")

    except Exception as e:
        print(f"Error querying view: {e}")
        # Fallback to strategies
        try:
             res = supabase.table('strategies').select('name, allocated_capital, user_id').execute() # Added user_id
             for s in res.data:
                 print(f"Strategy: {s['name']}, Allocated: {s.get('allocated_capital')}, UserID: {s.get('user_id')}")
        except:
            pass

    print("\n=== Buy Candidates Budget Check ===")
    # 2. Check get_buy_candidates RPC to see if it 'sees' these strategies
    # This RPC usually requires no args or simple args.
    try:
        # Note: RPC might fail if it needs args.
        # usually it is `get_buy_candidates` or similar. 
        # But we previously looked at `get_active_strategies_with_universe`. 
        # Let's check `get_active_strategies_with_universe` output for 'allocated_capital'.
        rpc_res = supabase.rpc('get_active_strategies_with_universe', {}).execute()
        if rpc_res.data:
            print(f"Active Strategies for Trading: {len(rpc_res.data)}")
            for s in rpc_res.data:
                 print(f"  - {s['strategy_name']}: Cap {s['allocated_capital']}")
                 if 'user_id' in s:
                     print(f"    [OK] user_id present: {s['user_id']}")
                 else:
                     print(f"    [FAIL] user_id MISSING!")
        else:
            print("No Active Strategies returned by RPC.")

    except Exception as e:
        print(f"RPC Error: {e}")

if __name__ == "__main__":
    verify_budget()
