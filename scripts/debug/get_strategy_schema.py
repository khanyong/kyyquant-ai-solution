import os
import sys
# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')
from supabase import create_client

def manual_load_env():
    env_path = '.env.development'
    if not os.path.exists(env_path):
        env_path = '.env'
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

def get_schema():
    manual_load_env()
    # Use Service Role for access
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("Fetching 1 strategy to inspect columns...")
    try:
        res = supabase.table('strategies').select('*').limit(1).execute()
        if res.data:
            print("Columns found:", list(res.data[0].keys()))
            print("Sample 'conditions':", res.data[0].get('conditions'))
            print("Sample 'entry_conditions':", res.data[0].get('entry_conditions'))
        else:
            print("No strategies found, but query worked.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_schema()
