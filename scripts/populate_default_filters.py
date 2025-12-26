import os
import sys
import json
# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')
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

def populate_filters():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    # Sample Stocks (Major KOSPI/KOSDAQ)
    # Samsung Elec, SK Hynix, Naver, Kakao, LG Energy, Hyundai Motor, POSCO, KB Financial
    kospi_samples = [
        "005930", "000660", "035420", "035720", 
        "373220", "005380", "005490", "105560",
        "051910", "000270"
    ]
    # EcoPro BM, EcoPro, HLB, Pearl Abyss, etc.
    kosdaq_samples = [
        "247540", "086520", "028300", "263750",
        "293490", "091990", "066970", "035900"
    ]

    print("=== Populating Default Filters ===")
    
    try:
        # Update KOSPI Default
        supabase.table('kw_investment_filters').update({
            'filtered_stocks': kospi_samples,
            'filtered_stocks_count': len(kospi_samples),
            'updated_at': 'now()'
        }).eq('name', 'KOSPI Default').execute()
        print(f"✅ Populated KOSPI Default with {len(kospi_samples)} stocks.")

        # Update KOSDAQ Default
        supabase.table('kw_investment_filters').update({
            'filtered_stocks': kosdaq_samples,
            'filtered_stocks_count': len(kosdaq_samples),
            'updated_at': 'now()'
        }).eq('name', 'KOSDAQ Default').execute()
        print(f"✅ Populated KOSDAQ Default with {len(kosdaq_samples)} stocks.")
        
    except Exception as e:
        print(f"Error updating filters: {e}")

if __name__ == "__main__":
    populate_filters()
