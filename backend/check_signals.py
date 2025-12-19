import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch recent signals
res = supabase.table('trading_signals').select('*').order('created_at', desc=True).limit(5).execute()

print("Recent Signals:")
for signal in res.data:
    print(f"ID: {signal['id']}, Type: {signal['signal_type']}, Status: {signal['signal_status']}, Created: {signal['created_at']}")
