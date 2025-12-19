import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

stock_to_check = ['005010', '031430', '004020'] # From previous outputs: Incheon, Shinsegae, Husteel

print(f"--- Checking Stocks {stock_to_check} ---")
res = supabase.table('stocks').select('*').in_('code', stock_to_check).execute()
found_codes = [s['code'] for s in res.data]
print(f"Found: {found_codes}")

missing = set(stock_to_check) - set(found_codes)
if missing:
    print(f"MISSING: {missing}")
    # Plan: Update sync_account.py to insert missing stocks dynamically?
else:
    print("All stocks found.")
