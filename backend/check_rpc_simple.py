
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

async def check():
    print("--- START ---")
    try:
        # Check Monitoring
        res = supabase.table('strategy_monitoring').select('count', count='exact').execute()
        print(f"Monitoring Rows: {res.count}")
        
        # Check RPC
        rpc = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
        data = rpc.data if rpc.data else []
        print(f"RPC Result Count: {len(data)}")
        if data:
            print(f"First Item: {data[0]['stock_name']}")
    except Exception as e:
        print(f"Error: {e}")
    print("--- END ---")

if __name__ == "__main__":
    asyncio.run(check())
