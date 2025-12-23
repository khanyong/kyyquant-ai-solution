
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

def fix_position_size():
    target_id = 'f72eab97-ef68-4723-b49f-1e731554a576' # kyy_short_term_v01
    new_size = 100000000 # 100 Million KRW (Effectively no limit)
    
    print(f"Updating position_size for strategy {target_id} to {new_size}...")
    
    data, count = supabase.table('strategies').update({'position_size': new_size}).eq('id', target_id).execute()
    
    print("Update result:", data)

if __name__ == "__main__":
    fix_position_size()
