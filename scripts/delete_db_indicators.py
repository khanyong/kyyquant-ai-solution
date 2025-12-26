import os
import sys
from supabase import create_client

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

def delete_indicators():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    targets = ['macd', 'bollinger', 'MACD', 'Bollinger Bands']
    print(f"=== Deleting Indicators: {targets} ===")
    
    try:
        # Check before delete
        res = supabase.table('indicators').select('name').in_('name', targets).execute()
        found = [r['name'] for r in res.data]
        print(f"Found in DB: {found}")
        
        if found:
            supabase.table('indicators').delete().in_('name', found).execute()
            print("Successfully deleted indicators.")
        else:
            print("No matching indicators found to delete.")
            
    except Exception as e:
        print(f"Error deleting indicators: {e}")

if __name__ == "__main__":
    delete_indicators()
