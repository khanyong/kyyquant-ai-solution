import os
import time
import sys
from dotenv import load_dotenv
from supabase import create_client

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def debug_performance():
    log("=== Starting Performance Debug ===")
    
    log("Loading .env...")
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not key:
        log("❌ Missing credentials!")
        return

    log("Initializing Supabase client...")
    try:
        supabase = create_client(url, key)
        log("Client initialized.")
        
        # 1. Test basic connectivity
        log("Step 1: Testing basic connectivity (fetching 1 strategy)...")
        start = time.time()
        strategies = supabase.table('strategies').select('id, name').limit(1).execute()
        log(f"Step 1 Complete. Time: {time.time() - start:.2f}s")
        
        # 2. Test Strategy Monitoring Table Count
        log("Step 2: Checking 'strategy_monitoring' table count...")
        start = time.time()
        # count='exact' can be slow on large tables, using 'planned' or just fetching a few
        monitoring = supabase.table('strategy_monitoring').select('count', count='exact').limit(1).execute()
        count = monitoring.count
        log(f"Step 2 Complete. Rows: {count}. Time: {time.time() - start:.2f}s")
        
        # 3. Test RPC call
        log("Step 3: Calling 'get_buy_candidates' RPC...")
        start = time.time()
        # Set a low timeout or just measure it
        rpc = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
        data_len = len(rpc.data) if rpc.data else 0
        log(f"Step 3 Complete. Candidates returned: {data_len}. Time: {time.time() - start:.2f}s")
        
        if data_len > 0:
            log(f"First candidate: {rpc.data[0]}")
            
    except Exception as e:
        log(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    debug_performance()
