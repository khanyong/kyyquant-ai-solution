import os
import asyncio
from supabase import create_client, Client
from datetime import datetime, timedelta

# Load environment variables manually
env_vars = {}
cwd = os.getcwd()
print(f"Current Working Directory: {cwd}")

files_to_try = ['.env.development', '.env']
loaded_file = None

for fname in files_to_try:
    fpath = os.path.join(cwd, fname)
    if os.path.exists(fpath):
        print(f"Found env file: {fpath}")
        loaded_file = fpath
        break

if not loaded_file:
    print("No .env file found in CWD.")
else:
    for encoding in ['utf-8', 'cp949', 'latin-1']:
        try:
            with open(loaded_file, 'r', encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key_part, value_part = line.split('=', 1)
                        env_vars[key_part.strip()] = value_part.strip()
            print(f"Successfully loaded env from {loaded_file}")
            break
        except UnicodeDecodeError:
            continue

print(f"Loaded {len(env_vars)} keys: {list(env_vars.keys())}")

url = env_vars.get("SUPABASE_URL") or env_vars.get("VITE_SUPABASE_URL")
key = env_vars.get("SUPABASE_SERVICE_ROLE_KEY") or env_vars.get("SUPABASE_SERVICE_KEY") or env_vars.get("SUPABASE_KEY") or env_vars.get("VITE_SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: credentials not found")
    print(f"URL: {url}")
    print(f"KEY: {bool(key)}")
    exit(1)

supabase: Client = create_client(url, key)

async def verify_liquidation():
    print("=== Emergency Liquidation Verification ===")
    
    # 1. Check Strategy Halt Status
    print("\n[1. Check Strategy Status]")
    strategies = supabase.table('strategies').select('*').eq('is_active', True).execute()
    if not strategies.data:
        print("✅ SUCCESS: All strategies are HALTED (No active strategies found).")
    else:
        print(f"❌ WARNING: Found {len(strategies.data)} ACTIVE strategies! (Halt failed?)")
        for s in strategies.data:
            print(f"  - Active Strategy: {s['name']} ({s['id']})")

    # 2. Check Recent Sell Orders
    print("\n[2. Check Recent Sell Orders (Last 30 mins)]")
    time_limit = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
    orders = supabase.table('orders')\
        .select('*')\
        .eq('order_type', 'sell')\
        .gt('created_at', time_limit)\
        .order('created_at', desc=True)\
        .execute()
        
    if orders.data:
        print(f"✅ SUCCESS: Found {len(orders.data)} SELL orders.")
        for o in orders.data:
            print(f"  - Order: {o['stock_code']} | Status: {o['status']} | Time: {o['created_at']}")
    else:
        print("⚠️ NOTE: No recent SELL orders found. (Maybe portfolio was already empty?)")

    # 3. Check Current Portfolio
    print("\n[3. Check Current Portfolio]")
    portfolio = supabase.table('kw_portfolio').select('*').gt('quantity', 0).execute()
    if not portfolio.data:
        print("✅ SUCCESS: Portfolio is EMPTY.")
    else:
        print(f"❌ WARNING: Portfolio still contains {len(portfolio.data)} holdings!")
        for p in portfolio.data:
            print(f"  - Holding: {p['stock_code']} ({p['stock_name']}) | Qty: {p['quantity']}")

if __name__ == "__main__":
    asyncio.run(verify_liquidation())
