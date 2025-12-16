import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.strategy import check_strategy_signal, StrategySignalRequest
from dotenv import load_dotenv

load_dotenv()

async def test_crash():
    print("Testing stock 023800 for crash...")
    
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        print("Error: Supabase credentials not found.")
        return

    supabase = create_client(url, key)
    strategies = supabase.table('strategies').select('id').eq('is_active', True).limit(1).execute()
    
    if not strategies.data:
        # try inactive
        strategies = supabase.table('strategies').select('id').limit(1).execute()

    if not strategies.data:
        print("No strategy found.")
        return

    strategy_id = strategies.data[0]['id']
    stock_code = "023800" 
    
    req = StrategySignalRequest(
        strategy_id=strategy_id,
        stock_code=stock_code,
        current_price=None # Force fallback logic
    )
    
    try:
        response = await check_strategy_signal(req)
        print("SUCCESS: 023800 processed correctly.")
        print(response)
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crash())
