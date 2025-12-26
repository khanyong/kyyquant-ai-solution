import os
import sys
# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')
from supabase import create_client

def manual_load_env():
    env_paths = ['.env', '.env.development']
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '=' in line:
                        key, val = line.split('=', 1)
                        os.environ[key.strip()] = val.strip()

def populate_full_filters():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Populating Full Universe ===")
    
    try:
        # 1. Fetch ALL stock codes
        # Pagination might be needed if > 1000, but let's try fetching all or 3000
        # Supabase default limit is 1000 usually. We need to page.
        
        all_stocks = []
        offset = 0
        limit = 1000
        while True:
            res = supabase.table('kw_price_current').select('stock_code').range(offset, offset+limit-1).execute()
            if not res.data:
                break
            
            codes = [item['stock_code'] for item in res.data if item.get('stock_code')]
            all_stocks.extend(codes)
            
            if len(res.data) < limit:
                break
            offset += limit
            
        print(f"Fetched {len(all_stocks)} stock codes.")
        
        if not all_stocks:
            print("No stocks found to populate.")
            return

        # 2. Update Filters
        # Since we don't know market type, we put ALL into BOTH defaults.
        # This ensures 'Full Test' works for any strategy using these defaults.
        
        # Batch 1: KOSPI Default
        print("Updating KOSPI Default...")
        supabase.table('kw_investment_filters').update({
            'filtered_stocks': all_stocks,
            'filtered_stocks_count': len(all_stocks),
            'updated_at': 'now()'
        }).eq('name', 'KOSPI Default').execute()
        
        # Batch 2: KOSDAQ Default
        print("Updating KOSDAQ Default...")
        supabase.table('kw_investment_filters').update({
            'filtered_stocks': all_stocks,
            'filtered_stocks_count': len(all_stocks),
            'updated_at': 'now()'
        }).eq('name', 'KOSDAQ Default').execute()
        
        print("✅ Successfully populated both filters with FULL UNIVERSE.")

    except Exception as e:
        print(f"Error updating filters: {e}")

if __name__ == "__main__":
    populate_full_filters()
