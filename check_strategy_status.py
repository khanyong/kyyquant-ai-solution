import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables manually to avoid encoding errors
import os

env_vars = {}
for encoding in ['utf-8', 'cp949', 'latin-1']:
    try:
        with open('.env', 'r', encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key_part, value_part = line.split('=', 1)
                    env_vars[key_part.strip()] = value_part.strip()
        break
    except UnicodeDecodeError:
        continue

print(f"Loaded {len(env_vars)} environment variables from .env")
# print(f"Keys found: {list(env_vars.keys())}") # Debugging

url = env_vars.get("SUPABASE_URL")
# Try multiple possible key names
key = env_vars.get("SUPABASE_SERVICE_ROLE_KEY") or env_vars.get("SUPABASE_SERVICE_KEY") or env_vars.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env (or failed to read file)")
    # Fallback to os.environ if available
    url = os.environ.get("SUPABASE_URL", url)
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", key)
    
    if not url or not key:
        print("Available keys in .env:", list(env_vars.keys()))
        exit(1)

supabase: Client = create_client(url, key)

async def check_strategy_status():
    print("Fetching Strategy Data...")
    
    # 1. Get all active strategies
    try:
        strategies = supabase.table('strategies').select('*').eq('is_active', True).execute()
        
        if not strategies.data:
            print("No active strategies found.")
            return

        print(f"\nFound {len(strategies.data)} active strategies:")
        
        for strategy in strategies.data:
            s_id = strategy['id']
            s_name = strategy['name']
            position_size = strategy.get('position_size', 0)
            
            print(f"\n[Strategy: {s_name}] ({s_id})")
            print(f"  - Fixed Position Size: {position_size}")
            
            # 2. Get Capital Status
            cap_status = supabase.table('strategy_capital_status').select('*').eq('strategy_id', s_id).execute()
            if cap_status.data:
                cs = cap_status.data[0]
                allocated = cs.get('allocated_capital', 0)
                available = cs.get('available_for_next_order', 0)
                print(f"  - Allocated Capital: {allocated}")
                print(f"  - Available for Next Order: {available}")
            else:
                print("  - No capital status record found!")

            # 3. Check recent orders that might have depleted budget
            orders = supabase.table('orders').select('*').eq('strategy_id', s_id).order('created_at', desc=True).limit(3).execute()
            if orders.data:
                print(f"  - Recent Orders: {len(orders.data)} found")
                for o in orders.data:
                    print(f"    - {o['created_at']} | {o['stock_code']} | {o['order_type']} | Qty: {o['quantity']} | Status: {o['status']}")
            
    except Exception as e:
        print(f"Error executing query: {e}")

    # 4. Call RPC to see calculated position_size
    print("\nfetching buy candidates (RPC)...")
    try:
        rpc_res = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
        if rpc_res.data:
            print(f"Found {len(rpc_res.data)} candidates:")
            for c in rpc_res.data:
                print(f"  - {c['stock_code']} ({c['stock_name']}) | Price: {c['current_price']} | Position Size: {c['position_size']} | Total Avail: {c.get('total_available_budget')} | Count: {c.get('candidate_count')}")
        else:
            print("No candidates returned from RPC.")
    except Exception as e:
        print(f"Error calling RPC: {e}")

if __name__ == "__main__":
    asyncio.run(check_strategy_status())
