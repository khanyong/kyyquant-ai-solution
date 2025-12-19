import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

target_user = 'f912da32-897f-4dbb-9242-3a438e9733a8'

print(f"--- Checking for User {target_user} ---")
try:
    # Check profiles
    res = supabase.table('profiles').select('*').eq('id', target_user).execute()
    if res.data:
        print(f"Found in profiles: {res.data[0]}")
    else:
        print("Not found in profiles.")
        
    # Check auth.users (if accessible via service key? wrapper usually doesn't expose auth table directly via postgrest)
    # We can try admin api if available, but supabase-py client `auth.admin` is distinct.
    
except Exception as e:
    print(f"Error: {e}")
