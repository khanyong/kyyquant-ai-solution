
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def debug_database():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        print("Missing Supabase credentials")
        return

    supabase = create_client(url, key)
    
    target_code = "005930" # Samsung Electronics

    try:
        print(f"\n--- Checking kw_stock_master for {target_code} ---")
        resp = supabase.table("kw_stock_master").select("*").eq("stock_code", target_code).execute()
        if resp.data:
            item = resp.data[0]
            print(f"Code: {item.get('stock_code')}")
            print(f"Name: {item.get('stock_name')}")
            if item.get('stock_code') == item.get('stock_name'):
                print("⚠ WARNING: Name equals Code in Master Table!")
        else:
            print("No data in Master Table")

        print(f"\n--- Checking kw_price_current for {target_code} ---")
        resp = supabase.table("kw_price_current").select("*").eq("stock_code", target_code).execute()
        if resp.data:
            item = resp.data[0]
            print(f"Code: {item.get('stock_code')}")
            print(f"Name: {item.get('stock_name')}")
            if item.get('stock_code') == item.get('stock_name'):
                print("⚠ WARNING: Name equals Code in Current Price Table!")
        else:
            print("No data in Current Price Table")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_database())
