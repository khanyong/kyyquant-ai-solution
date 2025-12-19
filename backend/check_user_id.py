import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("--- Checking Users ---")
try:
    res = supabase.table('users').select('*').limit(5).execute()
    if res.data:
        for u in res.data:
            print(f"User: {u['id']} ({u.get('email', 'no-email')})")
    else:
        print("Users table is empty.")
except Exception as e:
    print(f"Failed to query users: {e}")

print("\n--- Checking Orders (User ID) ---")
try:
    res = supabase.table('orders').select('id, user_id, stock_code').limit(5).order('created_at', desc=True).execute()
    if res.data:
        for o in res.data:
            print(f"Order {o['id']}: UserID={o.get('user_id')}")
    else:
        print("Orders table is empty.")
except Exception as e:
    print(f"Failed to query orders: {e}")
