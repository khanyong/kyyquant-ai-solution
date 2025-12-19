import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
from api.kiwoom_client import get_kiwoom_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
kiwoom = get_kiwoom_client()

async def sync_account():
    print("=== Syncing Account Balance & Holdings ===")
    
    # 1. Fetch from Kiwoom
    print("[1] Fetching from Kiwoom API...")
    data = kiwoom.get_account_balance()
    
    # Handle both new and old return formats gracefully
    if isinstance(data, list):
         print("  Warning: Received list format (using legacy mode). Summary will be empty.")
         holdings = data
         summary = {}
    elif isinstance(data, dict):
         holdings = data.get('holdings', [])
         summary = data.get('summary', {})
    else:
         print("  Error: Unknown return format.")
         return

    print(f"  Holdings Found: {len(holdings)}")
    if summary:
         print(f"  Summary: Assets={summary.get('total_assets')}, Cash={summary.get('withdrawable_amount')}")

    # 1.5 Get User ID
    user_id = None
    TARGET_USER_ID = 'f912da32-897f-4dbb-9242-3a438e9733a8'
    
    try:
        res = supabase.table('profiles').select('id').eq('id', TARGET_USER_ID).execute()
        if res.data:
            user_id = TARGET_USER_ID
            print(f"  Found Target User ID: {user_id}")
    except Exception:
        pass

    if not user_id:
        try:
             # Fallback to profiles table (as per user instruction)
             res = supabase.table('profiles').select('id').limit(1).execute()
             if res.data:
                 user_id = res.data[0]['id']
                 print(f"  Found User ID from profiles: {user_id}")
        except Exception as e:
            print(f"  Warning: Could not fetch from profiles table: {e}")

    if not user_id:
        print("  Error: No User ID found in orders or profiles table. Cannot sync data.")
        return
        
    print(f"  Syncing for User ID: {user_id}")

    # 2. Update Supabase 'portfolio'
    print("\n[2] Updating Portfolio in DB...")
    
    for h in holdings:
        # Schema for 'portfolio' table:
        # user_id, stock_code, quantity, avg_price, current_price, profit_loss, profit_loss_rate
        
        # [FIX] Strip 'A' prefix from Kiwoom stock codes
        raw_code = h['stock_code']
        stock_code = raw_code[1:] if raw_code.startswith('A') else raw_code
        
        pf_data = {
            'user_id': user_id,
            'stock_code': stock_code,
            'quantity': h['quantity'],
            'avg_price': h['average_price'],
            'current_price': h['current_price'],
            'profit_loss': h['profit_loss'],
            'profit_loss_rate': h['profit_loss_rate'],
            'updated_at': 'now()'
        }
        
        try:
           # Check if stock exists in 'stocks' table to prevent FK violation
           # cache check or just upsert?
           # Upserting into 'stocks' is safer.
           stock_name = h.get('stock_name', 'Unknown')
           stock_data = {'code': stock_code, 'name': stock_name}
           try:
                # Use ignore_duplicates=True equivalent via upsert on conflict do nothing?
                # supabase upsert creates if not exists.
                supabase.table('stocks').upsert(stock_data).execute()
           except Exception as e_stock:
                print(f"  Warning: Failed to ensure stock {stock_code} exists: {e_stock}")

           # Upsert into portfolio
           # Unique constraint is (user_id, stock_code)
           # print(f"DEBUG Data: {pf_data}") # Commented out debug
           res = supabase.table('portfolio').upsert(pf_data, on_conflict='user_id, stock_code').execute()
           print(f"  Upserted {h['stock_name']}: {res.data}")
               
        except Exception as e:
            print(f"  Failed to update portfolio for {h['stock_name']}: {e}")

    # 3. Update Account Balance
    if summary:
        print("\n[3] Updating Account Balance...")
        bal_data = {
            'user_id': user_id,
            'total_assets': summary.get('total_assets', 0),
            'available_cash': summary.get('withdrawable_amount', 0), # Using buyable amount as cash
            'total_evaluation': summary.get('total_evaluation_amount', 0),
            'total_profit_loss': summary.get('total_evaluation_profit_loss', 0),
            'total_profit_loss_rate': summary.get('total_earning_rate', 0),
            'updated_at': 'now()'
        }
        
        try:
            res = supabase.table('account_balance').upsert(bal_data, on_conflict='user_id').execute()
            print(f"  Balance Updated: {res.data}")
        except Exception as e:
            print(f"  Failed to update account balance: {e}")


if __name__ == "__main__":
    asyncio.run(sync_account())
