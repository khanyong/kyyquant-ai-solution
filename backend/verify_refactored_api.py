import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.strategy import check_strategy_signal, StrategySignalRequest

# Mocking Supabase and Kiwoom interactions might be hard without real environment.
# We will use the REAL environment variables currently set (assuming .env is loaded or env vars present)
# If env vars are missing, we might need to load them.

from dotenv import load_dotenv
load_dotenv()

async def test_api():
    print("Testing refactored check_strategy_signal...")
    
    # Needs a valid strategy ID and stock code
    # We can fetch one from DB or usage a known one.
    # We will try to fetch from DB first.
    
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        print("Error: Supabase credentials not found.")
        return

    supabase = create_client(url, key)
    
    # Get a strategy
    strategies = supabase.table('strategies').select('id').eq('is_active', True).limit(1).execute()
    if not strategies.data:
        print("No active strategy found to test.")
        # Try inactive
        strategies = supabase.table('strategies').select('id').limit(1).execute()
        
    if not strategies.data:
        print("No strategy found at all.")
        return
        
    strategy_id = strategies.data[0]['id']
    stock_code = "000080" # HiteJinro (Verified updated)
    
    # Check if this strategy handles this stock? Not strictly required for the API test unless logic fails.
    # We just need ANY stock that has data.
    
    req = StrategySignalRequest(
        strategy_id=strategy_id,
        stock_code=stock_code,
        current_price=60000 # Mock current price
    )
    
    print(f"Calling API for strategy {strategy_id} and stock {stock_code}...")
    try:
        response = await check_strategy_signal(req)
        print("\nSUCCESS: API returned response.")
        print(f"Signal: {response.signal_type}")
        print(f"Strength: {response.signal_strength}")
        print(f"Indicators: {list(response.indicators.keys())}")
        print(f"Debug Info: {response.debug_info}")
        
        # Verify it used BacktestEngine results
        if 'engine_result' in response.debug_info:
             print("Verified: Result contains 'engine_result' from BacktestEngine.")
        else:
             print("Warning: 'engine_result' missing from debug_info.")
             
    except Exception as e:
        print(f"\nFAILED: API call raised exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api())
