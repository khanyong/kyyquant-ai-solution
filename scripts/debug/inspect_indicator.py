import os
import sys
import json
from supabase import create_client

# Force UTF-8
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

def inspect_indicator():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Inspecting 'bollinger' Indicator ===")
    try:
        res = supabase.table('indicators').select('*').eq('name', 'bollinger').execute()
        if res.data:
            print(json.dumps(res.data[0], indent=2, default=str))
        else:
            print("Indicator 'bollinger' not found.")
            # Try finding ANY indicator
            res = supabase.table('indicators').select('*').limit(1).execute()
            if res.data:
                print("Showing first available indicator instead:")
                print(json.dumps(res.data[0], indent=2, default=str))

    except Exception as e:
        print(f"Error fetching indicator: {e}")

if __name__ == "__main__":
    inspect_indicator()
