import os
import sys
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
from supabase import create_client

sys.path.append(os.path.dirname(__file__))
from api.kiwoom_client import get_kiwoom_client

load_dotenv()

def main():
    print("TEST: Updating 005930 (Samsung Electronics) for 3 years...")
    
    # Init
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(url, key)
    kiwoom = get_kiwoom_client()
    
    stock_code = "005930"
    current_base_date = None
    total_records = 0
    
    for page in range(1, 4):
        print(f"Page {page}: Fetching from {current_base_date if current_base_date else 'Today'}")
        data = kiwoom.get_historical_price(stock_code, period=600, base_date=current_base_date)
        
        if not data:
            print("  -> No data.")
            break
            
        print(f"  -> Got {len(data)} records.")
        
        # Save to DB
        db_data = []
        dates = []
        if len(data) > 0:
            import pprint
            print("SAMPLE ROW:")
            pprint.pprint(data[0])
            return
            
        for row in data:
            formatted_date = f"{trade_date[:4]}-{trade_date[4:6]}-{trade_date[6:]}"
            dates.append(trade_date)
            db_data.append({
                'stock_code': stock_code,
                'trade_date': formatted_date,
                'close': float(row['stck_clpr']),
                'open': float(row['stck_oprc']),
                'high': float(row['stck_hgpr']),
                'low': float(row['stck_lwpr']),
                'volume': int(row['acml_vol'])
            })
            
        supabase.table('kw_price_daily').upsert(db_data, on_conflict='stock_code,trade_date').execute()
        total_records += len(db_data)
        
        # Next Date
        oldest_date_str = min(dates)
        oldest = datetime.strptime(oldest_date_str, '%Y%m%d')
        current_base_date = (oldest - timedelta(days=1)).strftime('%Y%m%d')
        
        time.sleep(1)

    print(f"DONE. Total records upserted: {total_records}")

if __name__ == "__main__":
    main()
