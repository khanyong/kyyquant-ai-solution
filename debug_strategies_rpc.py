
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: Missing Supabase Credentials")
    exit(1)

supabase = create_client(url, key)

print("Checking 'strategies' table...")
res = supabase.table('strategies').select('id, name, is_active, user_id').execute()
print(f"Total Strategies: {len(res.data)}")
for s in res.data:
    print(f"- {s['name']} (ID: {s['id']}) Active: {s['is_active']} User: {s['user_id']}")

print("\nChecking 'strategy_universes'...")
res_u = supabase.table('strategy_universes').select('*').execute()
print(f"Total Linked Universes: {len(res_u.data)}")
for u in res_u.data:
    print(f"- Link Strategy {u['strategy_id']} -> Filter {u['investment_filter_id']} (Active: {u['is_active']})")

print("\nChecking RPC 'get_active_strategies_with_universe'...")
try:
    res_rpc = supabase.rpc('get_active_strategies_with_universe').execute()
    print(f"RPC Result Count: {len(res_rpc.data)}")
    print(res_rpc.data)
except Exception as e:
    print(f"RPC Error: {e}")
