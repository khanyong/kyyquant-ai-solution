
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from datetime import datetime

# Load Env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url:
    print("No Supabase URL")
    exit(1)

supabase = create_client(url, key)

async def dry_run_verification():
    print("Fetching Active Strategies...")
    rpc_resp = supabase.rpc('get_active_strategies_with_universe').execute()
    data = rpc_resp.data
    
    print(f"Found {len(data)} active strategies.")
    
    for strategy in data:
        s_id = strategy['strategy_id']
        s_name = strategy['strategy_name']
        universes = strategy.get('universes', [])
        
        target_stocks = []
        
        # 1. Top level
        if strategy.get('filtered_stocks'):
             for s in strategy['filtered_stocks']:
                 target_stocks.append(s['stock_code'] if isinstance(s, dict) else s)
                 
        # 2. Universes
        for u in universes:
            u_name = u.get('universe_name')
            f_stocks = u.get('filtered_stocks') or []
            print(f"  - Universe '{u_name}' has {len(f_stocks)} stocks.")
            for s in f_stocks:
                 target_stocks.append(s['stock_code'] if isinstance(s, dict) else s)
                 
        unique_stocks = list(set(target_stocks))
        print(f"[Strategy: {s_name}] ID: {s_id}")
        print(f"  - Total Unique Targets: {len(unique_stocks)}")
        
        if unique_stocks:
            print(f"  - Sample Targets: {unique_stocks[:3]}")
        else:
            print("  - No targets found.")
            
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(dry_run_verification())
