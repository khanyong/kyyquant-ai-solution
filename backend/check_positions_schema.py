import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

res = supabase.table('positions').select('*').limit(1).execute()
if res.data:
    print(f"Columns: {list(res.data[0].keys())}")
else:
    print("Table is empty. Checking schema via error message or other means.")
    # Attempt to insert dummy to get error with columns
    try:
        supabase.table('positions').insert({'dummy': 'test'}).execute()
    except Exception as e:
        print(f"Error (contains hints?): {e}")
