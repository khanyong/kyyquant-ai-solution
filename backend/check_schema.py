import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

res = supabase.table('trading_signals').select('*').limit(1).execute()
if res.data:
    print(f"Columns: {list(res.data[0].keys())}")
else:
    print("Table is empty, cannot infer columns from data.")
