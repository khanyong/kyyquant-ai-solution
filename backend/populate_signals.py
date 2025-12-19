import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def populate_signals():
    print("=== Populating Missing Signals ===")
    
    # 1. Get recent orders (last 24h)
    one_day_ago = (datetime.now() - timedelta(hours=24)).isoformat()
    res = supabase.table('orders').select('*').gte('created_at', one_day_ago).execute()
    orders = res.data
    
    print(f"Found {len(orders)} recent orders.")
    
    for order in orders:
        # Check if signal exists
        sig_res = supabase.table('trading_signals').select('id').eq('order_id', order['id']).execute()
        if sig_res.data:
            print(f"Signal already exists for Order {order['id']}")
            continue
            
        print(f"Creating Signal for Order {order['id']} ({order['stock_name']})...")
        
        signal_record = {
            "strategy_id": order['strategy_id'],
            "stock_code": order['stock_code'],
            "stock_name": order['stock_name'],
            "signal_type": "BUY",  # UPPERCASE!
            "current_price": order['order_price'],
            "order_id": order['id'],
            "signal_status": "ORDERED",
            "created_at": order['created_at'] # Use order timestamp
        }
        
        try:
            supabase.table('trading_signals').insert(signal_record).execute()
            print("  Success!")
        except Exception as e:
            print(f"  Failed: {e}")

if __name__ == "__main__":
    asyncio.run(populate_signals())
