import os
import sys
from supabase import create_client

# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')

def manual_load_env():
    env_paths = ['.env', '.env.development']
    for env_path in env_paths:
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'): continue
                    if '=' in line:
                        key, val = line.split('=', 1)
                        os.environ[key.strip()] = val.strip()

def list_indicators():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Listing Indicators from DB ===")
    try:
        res = supabase.table('indicators').select('*').execute()
        indicators = res.data
        if not indicators:
            print("No indicators found in DB.")
        else:
            names = [ind.get('name') for ind in indicators]
            print(f"Found {len(indicators)} indicators: {names}")
            
            print(f"Details:")
            for ind in indicators:
                print(f"ID: {ind.get('id')} | Name: {ind.get('name')} | Type: {ind.get('type')} | Key: {ind.get('key', 'N/A')}")
    except Exception as e:
        print(f"Error fetching indicators: {e}")

if __name__ == "__main__":
    list_indicators()
