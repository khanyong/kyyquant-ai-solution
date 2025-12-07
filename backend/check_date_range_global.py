
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

supabase = create_client(url, key)

def get_date_range():
    print("Checking date range for 'kw_price_daily'...")
    
    # Get overall min date (ordering ascending)
    # Note: We limit to 1. We assume trade_date is YYYYMMDD or YYYY-MM-DD.
    # The user mentioned 2018-08-07.
    
    try:
        min_res = supabase.table('kw_price_daily').select('trade_date').order('trade_date', desc=False).limit(1).execute()
        max_res = supabase.table('kw_price_daily').select('trade_date').order('trade_date', desc=True).limit(1).execute()
        
        if min_res.data and max_res.data:
            min_date = min_res.data[0]['trade_date']
            max_date = max_res.data[0]['trade_date']
            print(f"Overall Date Range:")
            print(f"  Min Date: {min_date}")
            print(f"  Max Date: {max_date}")
        else:
            print("No data found in kw_price_daily.")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    get_date_range()
