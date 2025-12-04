"""
Fix Strategy Allocation
Manually updates the allocated_capital for the active strategy.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def fix_allocation():
    print("=" * 80)
    print("🔧 Fix Strategy Allocation")
    print("=" * 80)

    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return

    supabase = create_client(supabase_url, supabase_key)

    # 1. Get Active Strategy
    response = supabase.table('strategies').select('*').eq('is_active', True).execute()
    
    if not response.data:
        print("❌ No active strategy found")
        return

    strategy = response.data[0]
    print(f"Found Strategy: {strategy['name']} (ID: {strategy['id']})")
    print(f"Current Allocation: {strategy.get('allocated_capital')}")
    print(f"Current Percent: {strategy.get('allocated_percent')}")

    # 2. Ask for new allocation
    # For automation, we'll set a default or ask user to edit this script.
    # Let's set it to 10,000,000 KRW (10 million) as a safe default for mock trading, 
    # or calculate based on total asset if cash is 0.
    
    # Check total asset
    bal_res = supabase.table('kw_account_balance').select('total_asset').order('updated_at', desc=True).limit(1).execute()
    total_asset = bal_res.data[0]['total_asset'] if bal_res.data else 0
    
    print(f"Total Asset: {total_asset:,.0f} KRW")
    
    new_allocation = 10000000 # Default 10M
    if total_asset > 0:
        new_allocation = total_asset * 0.9 # 90% of total asset
        
    print(f"Setting Allocation to: {new_allocation:,.0f} KRW")
    
    # 3. Update
    update_res = supabase.table('strategies').update({
        'allocated_capital': new_allocation,
        'allocated_percent': 0.9 # Ensure percent is also set
    }).eq('id', strategy['id']).execute()
    
    if update_res.data:
        print("✅ Allocation updated successfully")
    else:
        print("❌ Failed to update allocation")

if __name__ == "__main__":
    fix_allocation()
