"""
Check Strategy Allocation and Account Balance
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_status():
    print("=" * 80)
    print("🔍 Strategy Allocation & Account Check")
    print("=" * 80)

    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return

    supabase = create_client(supabase_url, supabase_key)

    # 1. Check Account Balance
    print("\n[1] Account Balance (kw_account_balance)")
    response = supabase.table('kw_account_balance').select('*').order('updated_at', desc=True).limit(1).execute()
    if response.data:
        balance = response.data[0]
        print(f"   - Total Asset: {balance.get('total_asset', 0):,.0f} KRW")
        print(f"   - Cash Balance: {balance.get('cash_balance', 0):,.0f} KRW")
        print(f"   - Updated At: {balance.get('updated_at')}")
    else:
        print("   ⚠️ No account balance found")

    # 2. Check Strategies
    print("\n[2] Active Strategies")
    response = supabase.table('strategies').select('*').eq('is_active', True).execute()
    
    if response.data:
        for strategy in response.data:
            print(f"   ℹ️ Strategy Keys: {list(strategy.keys())}")
            print(f"   - ID: {strategy.get('id')}")
            print(f"   - Name: {strategy.get('name')}")
            print(f"   - Allocated Capital: {strategy.get('allocated_capital', 'N/A')}")
            print(f"   - Allocated Percent: {strategy.get('allocated_percent', 'N/A')}")
            print(f"   - Daily Limit: {strategy.get('daily_limit', 'N/A')}")
            print(f"   - Max Stocks: {strategy.get('max_stocks', 'N/A')}")
            print(f"   - Updated At: {strategy.get('updated_at')}")
            print("   ---")
    else:
        print("   ⚠️ No active strategies found")

if __name__ == "__main__":
    check_status()
