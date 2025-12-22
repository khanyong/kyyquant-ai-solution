import os
import sys
from dotenv import load_dotenv
from supabase import create_client
import chardet

# Load Environment Variables (Try multiple files)
for env_file in ['.env.local', '.env.development', '.env']:
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"Loaded {env_file}")
        break

url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    sys.exit(1)

supabase = create_client(url, key)

print("\n--- Strategy Capital Status Inspection ---")

try:
    # 1. Check Strategies Table
    print("\n[Strategy Table (Top 5)]")
    strategies = supabase.table('strategies').select('id, name, is_active, allocated_capital, position_size').limit(10).execute()
    
    for s in strategies.data:
        print(f"Name: {s['name']}")
        print(f"  ID: {s['id']}")
        print(f"  Active: {s['is_active']}")
        print(f"  Allocated Capital: {s.get('allocated_capital', '0')}")
        print(f"  Position Size: {s.get('position_size', '0')}")
        print("-" * 30)

    # 2. Check Strategy Capital Status View
    print("\n[Strategy Capital Status View]")
    # Try fetching from view
    try:
        status_view = supabase.table('strategy_capital_status').select('*').execute()
        for s in status_view.data:
             # Find name
             st_name = next((x['name'] for x in strategies.data if x['id'] == s['strategy_id']), "Unknown")
             print(f"Strategy: {st_name}")
             print(f"  Total Allocated: {s.get('total_allocated', 0)}")
             print(f"  Used: {s.get('active_investment_amount', 0)}")
             print(f"  Available: {s.get('available_for_next_order', 0)}")
             print("-" * 30)
    except Exception as e:
        print(f"Could not access strategy_capital_status view: {e}")

except Exception as e:
    print(f"Error accessing database: {e}")
