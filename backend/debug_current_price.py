import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

def check_current_price():
    print("=== Checking kw_price_current ===")
    
    # Fetch a few rows
    res = supabase.table('kw_price_current').select('*').limit(3).execute()
    
    if not res.data:
        print("❌ No data in kw_price_current")
        return

    for row in res.data:
        print(f"Stock: {row['stock_code']} | Price: {row['current_price']} | Time: {row['updated_at']}")

if __name__ == "__main__":
    check_current_price()
