
import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Supabase credentials missing.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check_balance():
    print("Fetching account_balance...")
    try:
        # Get the first user or specific user if known
        # We can just fetch all rows to see what's there
        response = supabase.table('account_balance').select('*').order('updated_at', desc=True).limit(1).execute()
        
        if response.data:
            print(f"Found {len(response.data)} records.")
            for row in response.data:
                print("--- Record ---")
                for k, v in row.items():
                    print(f"{k}: {v}")
        else:
            print("No records found in account_balance.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_balance())
