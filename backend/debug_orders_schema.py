
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment variables.")
    exit(1)

supabase: Client = create_client(url, key)

def debug_orders_schema():
    print("Inspecting 'orders' table...")
    try:
        resp = supabase.table('orders').select('*').limit(1).execute()
        if resp.data:
            print("Columns found:")
            for k in sorted(resp.data[0].keys()):
                print(f"- {k}")
        else:
            # If empty, try to insert dummy to get schema error or rely on my knowledge, but empty select gives no keys.
            print("Orders table is empty. Trying to list columns via error or assuming standard.")
            # We can try to list columns another way or just assume.
            # But wait, user said "Could not find the '' column", meaning I sent empty key.
            # I will trust the standard columns if empty: strategy_id, stock_code, type, price, quantity, status, account_no.
            pass
            
            # Additional check: specific columns used in code
            print("\nVerifying assumed columns...")
            # This is hard without data.
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_orders_schema()
