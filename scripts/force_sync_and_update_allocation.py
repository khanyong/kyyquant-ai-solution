import asyncio
from pathlib import Path
from datetime import datetime
import os
import sys

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / 'backend'
sys.path.append(str(backend_dir))

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from supabase import create_client

# Import Kiwoom Client
try:
    from api.kiwoom_client import get_kiwoom_client, KiwoomAPIClient
except ImportError:
    print("❌ Failed to import Kiwoom Client. Run from project root.")
    sys.exit(1)

def manual_load_env():
    # Load base first, then specific overrides
    env_paths = ['.env', '.env.development']
    loaded_any = False
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            print(f"[Env Loader] Found {env_path}, parsing...")
            try:
                with open(env_path, 'r', encoding='utf-8-sig', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'): continue
                        if '=' in line:
                            key, val = line.split('=', 1)
                            key = key.strip()
                            val = val.strip()
                            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                val = val[1:-1]
                            os.environ[key] = val
                loaded_any = True
                print(f"[Env Loader] Loaded {env_path}")
            except Exception as e:
                print(f"[Env Loader] Error reading {env_path}: {e}")
    
    if not loaded_any:
        print("[Env Loader] ⚠️ No .env files found!")


async def main():
    print("=== 🔄 Force Sync & Allocation Fix (Dual Mode Strategy) ===")
    
    # 1. Load Env
    manual_load_env()

    # 2. Define Sync Logic as Reusable Function
    async def try_sync(is_demo_mode: bool):
        mode_str = "MOCK" if is_demo_mode else "REAL"
        print(f"\n[Sync Attempt] Trying {mode_str} Mode...")
        
        # Reset/Force Env
        os.environ['KIWOOM_IS_DEMO'] = 'true' if is_demo_mode else 'false'
        
        # Re-import or Re-instantiate Client
        # We need to ensure TokenManager uses fresh config
        try:
            # Reload module to be safe? Or just rely on new instance reading os.getenv
            from api.kiwoom_client import KiwoomAPIClient
            client = KiwoomAPIClient() # New instance reads new IS_DEMO
            
            # Explicitly force is_demo in instance (just in case)
            client.is_demo = is_demo_mode
            client.base_url = "https://mockapi.kiwoom.com" if is_demo_mode else "https://api.kiwoom.com"
            print(f"  -> Client Configured for {client.base_url}")
            
            balance_info = client.get_account_balance()
            
            if balance_info and balance_info.get('summary'):
                return balance_info
            
            print(f"  -> {mode_str} Mode failed to return valid summary.")
            return None
            
        except Exception as e:
            print(f"  -> {mode_str} Mode Error: {e}")
            return None

    # 3. Execution Strategy: Try Configured First, then Toggle
    preferred_mode = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'
    
    print(f"[Strategy] Preferred Mode from Env: {'MOCK' if preferred_mode else 'REAL'}")
    
    result = await try_sync(preferred_mode)
    
    if not result:
        print(f"⚠️ Preferred mode failed. Switching to {'REAL' if preferred_mode else 'MOCK'}...")
        result = await try_sync(not preferred_mode)

    if not result:
        print("❌ Both MOCK and REAL modes failed. Check credentials.")
        return

    # 4. Process Success
    summary = result['summary']
    total_asset = float(summary.get('total_assets', 0))
    cash = float(summary.get('withdrawable_amount', 0)) # Or available_cash equivalent
    
    if total_asset == 0:
         total_asset = float(summary.get('deposit', 0))
         
    print(f"✅ Real Balance: {total_asset:,.0f} KRW (Withdrawal: {cash:,.0f})")

    # 5. DB Updates
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    supabase = create_client(url, key)
    
    # Get User ID
    user_data = supabase.table('strategies').select('user_id').limit(1).execute()
    user_id = user_data.data[0]['user_id'] if user_data.data else None
    
    if user_id:
        acc = result['account_no']
        print(f"[Sync] Updating kw_account_balance for user {user_id}...")
        supabase.table('kw_account_balance').insert({
            'user_id': user_id,
            'account_number': acc,
            'total_asset': int(total_asset),
            'available_cash': int(cash),
            'deposit': int(float(summary.get('deposit', 0))),
            'updated_at': datetime.now().isoformat()
        }).execute()

    # Update Allocation
    target_allocation = int(total_asset * 0.5)
    print(f"[Allocation] Target (50%): {target_allocation:,.0f} KRW")
    
    strategies = ['TEST_STRATEGY_A_MACD', 'TEST_STRATEGY_B_BB']
    
    for s_name in strategies:
        try:
            res = supabase.table('strategies').update({
                'allocated_capital': target_allocation,
                'allocated_percent': 0.5
            }).eq('name', s_name).execute()
            print(f"  ✅ Updated {s_name}: {target_allocation:,.0f}")
        except Exception as e:
            print(f"  ❌ Error updating {s_name}: {e}")

    print("\n🎉 Success! Refresh Frontend.")

if __name__ == "__main__":
    asyncio.run(main())
