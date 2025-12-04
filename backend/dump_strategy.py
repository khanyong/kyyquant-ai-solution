"""
Dump Raw Strategy Data
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

# Add project root to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def dump_raw_strategy():
    print("=" * 80)
    print("🔍 Dump Raw Strategy Data")
    print("=" * 80)

    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return

    supabase = create_client(supabase_url, supabase_key)

    # Get Active Strategy
    response = supabase.table('strategies').select('*').eq('is_active', True).execute()
    
    if response.data:
        for strategy in response.data:
            print(f"\nStrategy: {strategy.get('name')}")
            print("-" * 40)
            print(f"ID: {strategy.get('id')}")
            print(f"Name: {strategy.get('name')}")
            print(f"Allocated Capital: {strategy.get('allocated_capital')}")
            print(f"Allocated Percent: {strategy.get('allocated_percent')}")
            print(f"Is Active: {strategy.get('is_active')}")
            print("-" * 40)
    else:
        print("❌ No active strategy found")

if __name__ == "__main__":
    dump_raw_strategy()
