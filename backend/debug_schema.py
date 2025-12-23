
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

def inspect_schema():
    print("Inspecting 'account_balance' table...")
    # Fetch one row to see keys
    try:
        resp = supabase.table('account_balance').select('*').limit(1).execute()
        if resp.data:
            print("Columns found:")
            for k in sorted(resp.data[0].keys()):
                print(f"- {k}")
            print("\nSample row values:")
            for k, v in resp.data[0].items():
                print(f"{k}: {v}")
        else:
            print("Table appears empty, checking information_schema requires SQL execution or manual check.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_schema()
