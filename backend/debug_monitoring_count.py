import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

def check_monitoring():
    print("=== Strategy Monitoring Status ===")
    
    # 1. Total rows
    res = supabase.table('strategy_monitoring').select('count', count='exact').execute()
    print(f"Total Rows: {res.count}")
    
    # 2. Rows with is_near_entry = true
    res_entry = supabase.table('strategy_monitoring').select('count', count='exact').eq('is_near_entry', True).execute()
    print(f"Near Entry (True): {res_entry.count}")
    
    # 3. Last Updated time of a few rows
    res_recent = supabase.table('strategy_monitoring').select('updated_at').order('updated_at', desc=True).limit(5).execute()
    print("Recent Updates:")
    for r in res_recent.data:
        print(f"  - {r['updated_at']}")

if __name__ == "__main__":
    check_monitoring()
