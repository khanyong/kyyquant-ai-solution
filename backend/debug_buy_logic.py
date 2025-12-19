import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def debug_buy_candidates():
    print("=== Debugging Buy Candidates Logic ===")
    
    # 1. Check Active Strategies
    print("\n[1] Checking Active Strategies...")
    strategies = supabase.table('strategies').select('*').eq('is_active', True).eq('auto_trade_enabled', True).execute()
    
    if not strategies.data:
        print("❌ No active strategies found!")
        return
        
    for s in strategies.data:
        print(f"  - Strategy: {s['name']} (ID: {s['id']})")
        print(f"    Capital: {s['allocated_capital']}, Percent: {s['allocated_percent']}")

    strategy_ids = [s['id'] for s in strategies.data]
    
    # 2. Check Monitoring Table
    print("\n[2] Checking Strategy Monitoring Table (Top 5 by Score)...")
    # Fetch top candidates regardless of time
    monitor = supabase.table('strategy_monitoring')\
        .select('*')\
        .in_('strategy_id', strategy_ids)\
        .order('condition_match_score', desc=True)\
        .limit(5)\
        .execute()
        
    if not monitor.data:
        print("❌ No monitoring data found for active strategies.")
    else:
        for m in monitor.data:
            print(f"  - Stock: {m['stock_name']} ({m['stock_code']})")
            print(f"    Score: {m['condition_match_score']}")
            print(f"    Updated At: {m['updated_at']}")
            print(f"    Is Held: {m['is_held']}")
            
            # Check for stale data
            updated_at = datetime.fromisoformat(m['updated_at'].replace('Z', '+00:00'))
            now = datetime.now(updated_at.tzinfo)
            diff_minutes = (now - updated_at).total_seconds() / 60
            print(f"    Age: {diff_minutes:.1f} minutes ago")

    # 3. Call RPC directly
    print("\n[3] Calling get_buy_candidates RPC directly...")
    try:
        rpc = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
        print(f"  RPC Result Count: {len(rpc.data) if rpc.data else 0}")
        if rpc.data:
            print(f"  Data: {rpc.data}")
    except Exception as e:
        print(f"  RPC Failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_buy_candidates())
