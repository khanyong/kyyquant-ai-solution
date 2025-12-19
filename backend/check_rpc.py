
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_monitoring():
    print("=== Checking Strategy Monitoring & Candidates ===")
    
    # 1. Check strategy_monitoring count
    try:
        count = supabase.table('strategy_monitoring').select('*', count='exact').execute()
        print(f"\n[strategy_monitoring] Total rows: {count.count}")
        if count.count > 0:
            sample = supabase.table('strategy_monitoring').select('*').limit(3).execute()
            print("Sample Rows:", json.dumps(sample.data, indent=2, default=str))
    except Exception as e:
        print(f"Error checking monitoring: {e}")

    # 2. Call get_buy_candidates RPC
    print("\n[RPC] Calling get_buy_candidates...")
    try:
        # Assuming parameters, usually min_score
        params = {"min_score": 0} 
        rpc_result = supabase.rpc('get_buy_candidates', params).execute()
        print(f"Result count: {len(rpc_result.data) if rpc_result.data else 0}")
        if rpc_result.data:
            print(json.dumps(rpc_result.data[:2], indent=2, default=str))
        else:
            print("RPC returned empty list.")
    except Exception as e:
        print(f"Error calling RPC: {e}")

if __name__ == "__main__":
    asyncio.run(check_monitoring())
