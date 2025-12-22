import os
import time
from dotenv import load_dotenv
from supabase import create_client

def test_connection():
    print("Loading .env...")
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"URL: {url}")
    print(f"Key length: {len(key) if key else 0}")
    
    if not url or not key:
        print("❌ Missing credentials!")
        return

    print("Initializing Supabase client...")
    try:
        supabase = create_client(url, key)
        print("Client initialized. Attempting simple query...")
        
        start_time = time.time()
        # Try a very simple query, e.g. count on a small table or just a health check if possible
        # We will use 'strategies' count as it was used in the hanging script
        response = supabase.table('strategies').select('id', count='exact').limit(1).execute()
        end_time = time.time()
        
        print(f"✅ Connection successful!")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"Data: {response.data}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
