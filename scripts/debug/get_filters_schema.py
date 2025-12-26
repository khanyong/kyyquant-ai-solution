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
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("Fetching 1 filter to inspect columns...")
    try:
        res = supabase.table('kw_investment_filters').select('*').limit(1).execute()
        if res.data:
            print("Columns found:", list(res.data[0].keys()))
        else:
            print("No filters found, attempting to error to get columns or check logic.")
            # If empty, we can't see keys easily. Let's try to insert dummy to fail and see error, or just assume standard fields.
            # But the error message "column universe does not exist" is already a strong hint.
            pass
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_schema()
