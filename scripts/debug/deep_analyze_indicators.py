import os
import sys
import json
import logging
from supabase import create_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend'))

try:
    from indicators.calculator import IndicatorCalculator, ExecOptions
except ImportError:
    print("Could not import IndicatorCalculator. Make sure you are in the project root or correct path.")
    sys.exit(1)

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

def analyze():
    # 1. Load Env
    manual_load_env()
    print(f"ENFORCE_DB_INDICATORS: {os.getenv('ENFORCE_DB_INDICATORS')}")

    # 2. Inspect DB Raw
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    supabase = create_client(url, key)

    print("\n[DB Inspection] Fetching 'indicators' table...")
    res = supabase.table('indicators').select('*').execute()
    db_rows = res.data
    
    print(f"Total Rows in DB: {len(db_rows)}")
    print(f"{'Name':<20} {'IsActive':<10} {'CalcType':<15} {'ParsedName (repr)':<25}")
    print("-" * 70)
    for row in db_rows:
        name = row.get('name')
        active = row.get('is_active')
        ctype = row.get('calculation_type')
        print(f"{name:<20} {str(active):<10} {ctype:<15} {repr(name):<25}")
    
    # 3. Test Calculator Loading
    print("\n[Calculator Inspection] Initializing IndicatorCalculator...")
    calc = IndicatorCalculator()
    
    print(f"\nCalculator Cache Keys ({len(calc.indicators_cache)}):")
    print(list(calc.indicators_cache.keys()))

    # 4. Simulation
    target = 'macd'
    print(f"\n[Simulation] Trying to resolve '{target}'...")
    if target in calc.indicators_cache:
        print(f"SUCCESS: '{target}' found in cache.")
        defn = calc.indicators_cache[target]
        print(f"Definition Formula Code Length: {len(str(defn.get('formula', {}).get('code', '')))}")
    else:
        print(f"FAILURE: '{target}' NOT found in cache.")
        # Check for case mismatch
        for key in calc.indicators_cache.keys():
            if key.lower() == target.lower():
                 print(f"  -> But found '{key}' (Case mismatch?)")

if __name__ == "__main__":
    analyze()
