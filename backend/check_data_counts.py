import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def main():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)
    
    print("VERIFYING DATA COUNTS...")
    
    # Check a few random stocks that we saw in the log
    target_stocks = ['001250', '001420', '000370', '000140']
    
    for stock in target_stocks:
        try:
            # Simple count query
            response = supabase.table('kw_price_daily').select('count', count='exact').eq('stock_code', stock).execute()
            count = response.count
            
            # Date range query
            date_res = supabase.table('kw_price_daily').select('trade_date').eq('stock_code', stock).order('trade_date', desc=False).limit(1).execute()
            min_date = date_res.data[0]['trade_date'] if date_res.data else 'N/A'
            
            date_res_desc = supabase.table('kw_price_daily').select('trade_date').eq('stock_code', stock).order('trade_date', desc=True).limit(1).execute()
            max_date = date_res_desc.data[0]['trade_date'] if date_res_desc.data else 'N/A'
            
            print(f"Stock {stock}: {count} records ({min_date} ~ {max_date})")
            
            if count and count > 1000:
                print(f"  -> SUCCESS: > 1000 records (Approx {count/250:.1f} years)")
            else:
                 print(f"  -> WARNING: Only {count} records found.")
                 
        except Exception as e:
            print(f"Error checking {stock}: {e}")

if __name__ == "__main__":
    main()
