import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def inspect_strategy():
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)
    
    # Fetch active strategy
    print("Fetching active strategies...")
    response = supabase.table('strategies').select('*').eq('is_active', True).execute()
    
    if not response.data:
        print("No active strategies found.")
        return

    for strategy in response.data:
        print(f"\n[Strategy: {strategy.get('name')}]")
        print(f"ID: {strategy.get('id')}")
        
        # Check config
        config = strategy.get('config') or strategy
        print("--- Buy Conditions ---")
        if config.get('useStageBasedStrategy'):
             print(json.dumps(config.get('buyStageStrategy'), indent=2))
        else:
             print(json.dumps(config.get('buyConditions'), indent=2))
             print(json.dumps(config.get('entry_conditions'), indent=2)) # check both schemas
             
        # Check timeframe assumption (?) - usually implicit in data
        # Check universe
        print(f"Universe Size: {len(strategy.get('filtered_stocks') or [])}")

if __name__ == "__main__":
    asyncio.run(inspect_strategy())
