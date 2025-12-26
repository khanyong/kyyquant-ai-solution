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

def check_schema():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Checking 'indicators' Table ===")
    try:
        res = supabase.table('indicators').select('*').execute()
        indicators = res.data
        print(f"Count: {len(indicators)}")
        if indicators:
            print(f"{'Name':<15} {'Type':<15} {'Has Code?':<10}")
            print("-" * 40)
            for ind in indicators:
                name = ind.get('name')
                c_type = ind.get('calculation_type')
                formula = ind.get('formula')
                has_code = 'Yes' if isinstance(formula, dict) and 'code' in formula else 'No'
                print(f"{name:<15} {c_type:<15} {has_code:<10}")
        else:
            print("Table is empty.")
    except Exception as e:
        print(f"Error accessing 'indicators': {e}")

    print("\n=== Checking 'indicator_columns' Table ===")
    try:
        res = supabase.table('indicator_columns').select('*').execute()
        columns = res.data
        print(f"Count: {len(columns)}")
        if columns:
            print("Sample Rows:", json.dumps(columns[:2], indent=2, default=str))
        else:
            print("Table is empty.")
    except Exception as e:
        print(f"Error accessing 'indicator_columns': {e}")

if __name__ == "__main__":
    check_schema()
