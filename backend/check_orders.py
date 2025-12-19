import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch recent orders
res = supabase.table('orders').select('*').order('created_at', desc=True).limit(5).execute()

print("Recent Orders:")
for order in res.data:
    print(f"ID: {order['id']}, Stock: {order['stock_code']}, Status: {order['status']}, KiwoomNo: {order['kiwoom_order_no']}")
