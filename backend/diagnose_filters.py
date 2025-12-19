import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def diagnose_filters():
    print("=== Diagnosing Filters ===")
    
    # 1. Get Active Strategy ID
    strategies = supabase.table('strategies').select('id').eq('name', 'kyy_short_term_v01').execute()
    if not strategies.data:
        print("Strategy not found")
        return
    strategy_id = strategies.data[0]['id']
    print(f"Strategy ID: {strategy_id}")
    
    # 2. Check Capital Status (View)
    print("\n[2] Checking Strategy Capital Status (View)...")
    cap_status = supabase.table('strategy_capital_status').select('*').eq('strategy_id', strategy_id).execute()
    if cap_status.data:
        print(f"  Available for Next Order: {cap_status.data[0]['available_for_next_order']}")
    else:
        print("  ❌ No capital status found for this strategy.")

    # 3. Check Monitoring Rows (is_near_entry)
    print("\n[3] Checking Monitoring Rows (is_near_entry)...")
    monitor = supabase.table('strategy_monitoring')\
        .select('stock_name, condition_match_score, is_near_entry')\
        .eq('strategy_id', strategy_id)\
        .gte('condition_match_score', 80)\
        .execute()
        
    for m in monitor.data:
        print(f"  {m['stock_name']}: Score={m['condition_match_score']}, NearEntry={m['is_near_entry']}")

    # 4. Check Recent Orders
    print("\n[4] Checking Recent Orders...")
    orders = supabase.table('orders')\
        .select('stock_name, created_at')\
        .eq('strategy_id', strategy_id)\
        .order('created_at', desc=True)\
        .limit(5)\
        .execute()
        
    for o in orders.data:
        print(f"  Order: {o['stock_name']} at {o['created_at']}")

if __name__ == "__main__":
    asyncio.run(diagnose_filters())
