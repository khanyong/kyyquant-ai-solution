import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Try to insert a row with all possible keys to see which ones are rejected, 
# or try to select * limit 1 to see keys if any row exists.
print("--- Checking 'positions' table ---")
try:
    res = supabase.table('positions').select('*').limit(1).execute()
    if res.data:
        print(f"Existing Data Sample: {res.data[0]}")
    else:
        print("Table 'positions' is empty.")
        # Try to discover schema by error message
        try:
           supabase.table('positions').insert({'dummy_col': 1}).execute()
        except Exception as e:
           print(f"Error Hint: {e}")

except Exception as e:
    print(f"Select Error: {e}")

print("\n--- Checking 'portfolio' table ---")
try:
    res = supabase.table('portfolio').select('*').limit(1).execute()
    if res.data:
        print(f"Existing Data Sample: {res.data[0]}")
    else:
        print("Table 'portfolio' is empty.")
except Exception as e:
    print(f"Select Error: {e}")
