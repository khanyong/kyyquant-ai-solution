
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

def debug_latest_balance():
    print("Fetching last 5 account_balance entries...")
    try:
        resp = supabase.table('account_balance')\
            .select('id, user_id, available_cash, updated_at, account_no')\
            .order('updated_at', desc=True)\
            .limit(5)\
            .execute()
            
        if resp.data:
            for item in resp.data:
                print("-" * 30)
                print(f"ID: {item.get('id')}")
                print(f"Updated At: {item.get('updated_at')}")
                print(f"Available Cash: {item.get('available_cash')}")
                print(f"Account No: {item.get('account_no')}")
        else:
            print("No entries found in account_balance.")

    except Exception as e:
        print(f"Error fetching balance: {e}")

if __name__ == "__main__":
    debug_latest_balance()
