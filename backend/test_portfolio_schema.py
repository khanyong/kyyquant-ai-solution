import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Use the user_id found previously
user_id = 'c1c30582-3dac-455d-a7e8-1a47e2846482'

print("--- Testing Portfolio Insert ---")
data = {
    'user_id': user_id,
    'stock_code': '005930',
    'quantity': 10,
    'avg_price': 50000,
    'current_price': 51000,
    'profit_loss': 10000,
    'profit_loss_rate': 2.0
}

try:
    print(f"Attempting insert with: {data.keys()}")
    res = supabase.table('portfolio').insert(data).execute()
    print("Insert success!")
    # Cleanup
    supabase.table('portfolio').delete().eq('user_id', user_id).eq('stock_code', '005930').execute()
except Exception as e:
    print(f"Insert Failed: {e}")
