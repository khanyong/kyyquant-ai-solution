
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
# Use ANON KEY explicitly to simulate N8N
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")

# Fallback if variable names differ
if not SUPABASE_KEY:
    # Try to find it in .env manually or just fail
    print("WARNING: Could not find ANON KEY in env. Using SERVICE KEY for now (invalid test).")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"Using Key starting with: {SUPABASE_KEY[:10]}...")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def check():
    print("--- START (ANON TEST) ---")
    try:
        # Check RPC
        rpc = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
        data = rpc.data if rpc.data else []
        print(f"RPC Result Count: {len(data)}")
    except Exception as e:
        print(f"Error: {e}")
    print("--- END ---")

if __name__ == "__main__":
    asyncio.run(check())
