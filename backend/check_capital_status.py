"""
Check Strategy Capital Status
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def check_capital_status():
    print("=" * 80)
    print("🔍 Checking strategy_capital_status")
    print("=" * 80)

    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return

    supabase = create_client(supabase_url, supabase_key)

    # Check strategy_capital_status
    print("\n[1] strategy_capital_status Table/View")
    try:
        response = supabase.table('strategy_capital_status').select('*').execute()
        
        if response.data:
            for row in response.data:
                print(f"   - Strategy: {row.get('strategy_name')} (ID: {row.get('strategy_id')})")
                print(f"   - Allocated Capital: {row.get('allocated_capital')}")
                print(f"   - Allocated Percent: {row.get('allocated_percent')}")
                print("   ---")
        else:
            print("   ⚠️ No data found in strategy_capital_status")
            
    except Exception as e:
        print(f"❌ Error querying strategy_capital_status: {e}")

if __name__ == "__main__":
    check_capital_status()
