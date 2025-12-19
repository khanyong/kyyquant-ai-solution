import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("--- Checking Profiles Table ---")
try:
    res = supabase.table('profiles').select('*').limit(1).execute()
    if res.data:
        print(f"Data Sample: {res.data[0]}")
    else:
        print("profiles table is empty.")
except Exception as e:
    print(f"Failed to query profiles: {e}")
