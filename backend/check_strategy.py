
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

def check_strategy_settings():
    print("Checking 'strategies' table settings...")
    resp = supabase.table('strategies').select('id, name, position_size, allocated_capital').eq('is_active', True).execute()
    
    for s in resp.data:
        print(f"Strategy: {s['name']}")
        print(f" - ID: {s['id']}")
        print(f" - Position Size (KRW): {s['position_size']}")
        print(f" - Allocated Capital: {s['allocated_capital']}")
        print("-" * 30)

if __name__ == "__main__":
    check_strategy_settings()
