import os
import asyncio
import json
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

def check_universe():
    print("=== Checking Strategy Universes ===")
    
    # 1. Call RPC used by n8n
    print("[1] RPC: get_active_strategies_with_universe")
    rpc = supabase.rpc('get_active_strategies_with_universe').execute()
    
    for s in rpc.data:
        stocks = s.get('filtered_stocks', [])
        count = len(stocks) if stocks else 0
        print(f"  Strategy: {s['strategy_name']}")
        print(f"    - Filtered Stocks Count: {count}")
        if count < 10:
            print(f"    - Stocks: {stocks}")

if __name__ == "__main__":
    check_universe()
