
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

async def check_balance():
    print("--- Checking Balance ---")
    try:
        # Check Account Balance
        res = supabase.table('kw_account_balance').select('*').limit(1).execute()
        if res.data:
            b = res.data[0]
            print(f"Total Asset: {b.get('total_asset')}")
            print(f"Order Cash (Deposit): {b.get('order_cash')}")
            print(f"Updated At: {b.get('updated_at')}")
        else:
            print("No balance record found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_balance())
