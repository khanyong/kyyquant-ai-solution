import os
import uuid
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Try to create a dummy user in public.users
new_user_id = str(uuid.uuid4())
print(f"Attempting to create user: {new_user_id}")

try:
    user_data = {
        'id': new_user_id,
        'email': 'admin@auto-stock.com',
        'name': 'Admin User'
    }
    # Note: If public.users exists, this should work.
    res = supabase.table('users').insert(user_data).execute()
    print(f"User created: {res.data}")
except Exception as e:
    print(f"Failed to create user: {e}")
    # Maybe checking if 'strategies' has a user_id?
    try:
        res = supabase.table('strategies').select('user_id').limit(1).execute()
        if res.data:
            print(f"Found user_id in strategies: {res.data[0]['user_id']}")
    except Exception as e2:
        print(f"Strategy check failed: {e2}")

