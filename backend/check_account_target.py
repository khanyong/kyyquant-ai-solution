
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

def check_target_account():
    target_acc = "81126100-01"
    print(f"Checking balance for account: {target_acc}...")
    
    # Check exact match
    resp = supabase.table('account_balance').select('*').eq('account_no', target_acc).execute()
    
    if resp.data:
        print(f"Found exact match: {resp.data[0]['available_cash']} KRW")
    else:
        print("No exact match found.")
        # Check similar
        print("Checking for similar accounts (81126100)...")
        resp = supabase.table('account_balance').select('*').ilike('account_no', '%81126100%').execute()
        if resp.data:
            print("Found similar accounts:")
            for acc in resp.data:
                print(f"- {acc['account_no']}: {acc['available_cash']} KRW")
        else:
            print("No similar accounts found.")

if __name__ == "__main__":
    check_target_account()
