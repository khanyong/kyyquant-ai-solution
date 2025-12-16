import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

async def check_last_date():
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)
    
    # Check a few stocks: Start (000120), Early (000210), Target (005930)
    stock_codes = ["000120", "000210", "005930"]
    
    for code in stock_codes:
        print(f"\nChecking {code}...")
        response = supabase.table('kw_price_daily').select('trade_date, close').eq('stock_code', code).order('trade_date', desc=True).limit(1).execute()
        
        if response.data:
            print(f"Last Date: {response.data[0]['trade_date']}")
            print(f"Last Close: {response.data[0]['close']}")
        else:
            print("No data found.")

if __name__ == "__main__":
    asyncio.run(check_last_date())
