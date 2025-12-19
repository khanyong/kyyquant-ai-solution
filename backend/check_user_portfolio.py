import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

target_user = 'f912da32-897f-4dbb-9242-3a438e9733a8'

print(f"--- Checking Portfolio for User {target_user} ---")

# Check Account Balance
bal = supabase.table('account_balance').select('*').eq('user_id', target_user).execute()
print(f"Balance: {bal.data}")

# Check Portfolio
port = supabase.table('portfolio').select('*').eq('user_id', target_user).execute()
print(f"Portfolio Count: {len(port.data)}")
print(f"Portfolio Data: {port.data}")

# Check Stocks (just to see if auto-registration worked)
stocks = supabase.table('stocks').select('*').limit(5).execute()
print(f"Stocks Sample: {stocks.data}")
