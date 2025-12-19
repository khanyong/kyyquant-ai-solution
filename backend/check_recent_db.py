
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    print("Error: SUPABASE_URL not found")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_recent_activity():
    print("=== Checking Recent DB Activity ===")
    
    # Check Orders
    print("\n[Recent Orders]")
    try:
        orders = supabase.table('orders').select('*').order('created_at', desc=True).limit(5).execute()
        if not orders.data:
            print("No recent orders found.")
        else:
            for o in orders.data:
                print(f"- {o['created_at']}: {o['stock_code']} {o['side']} (Status: {o['status']})")
    except Exception as e:
        print(f"Error checking orders: {e}")

    # Check Trading Signals
    print("\n[Recent Trading Signals]")
    try:
        signals = supabase.table('trading_signals').select('*').order('created_at', desc=True).limit(5).execute()
        if not signals.data:
            print("No recent trading signals found.")
        else:
            for s in signals.data:
                print(f"- {s['created_at']}: {s['stock_code']} {s['signal_type']} (Strategy: {s.get('strategy_id')})")
    except Exception as e:
        print(f"Error checking signals: {e}")

if __name__ == "__main__":
    asyncio.run(check_recent_activity())
