
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment variables.")
    exit(1)

supabase: Client = create_client(url, key)

def check_signals():
    print("Checking 'trading_signals' table...")
    
    # Check total count first
    resp = supabase.table('trading_signals').select('*', count='exact').execute()
    print(f"Total signals in DB: {resp.count}")
    
    # Check last 24h
    one_day_ago = (datetime.utcnow() - timedelta(days=1)).isoformat()
    resp_recent = supabase.table('trading_signals').select('*').gte('created_at', one_day_ago).order('created_at', desc=True).execute()
    
    print(f"Signals in last 24h: {len(resp_recent.data)}")
    
    if resp_recent.data:
        print("\nRecent Signals:")
        for s in resp_recent.data[:5]:
            print(f" - [{s['created_at']}] {s['stock_name']} ({s['stock_code']}) - {s['signal_type']} - Strategy: {s['strategy_id']}")
    else:
        print("No recent signals found.")

    # Check Active Strategies
    print("\nChecking Active Strategies...")
    resp_strat = supabase.table('strategies').select('id, name, is_active, auto_trade_enabled').eq('is_active', True).execute()
    print(f"Active Strategies ({len(resp_strat.data)}):")
    for s in resp_strat.data:
        print(f" - {s['name']} (ID: {s['id']}) - AutoTrade: {s['auto_trade_enabled']}")

    # Check Strategy Monitoring
    print("\nChecking 'strategy_monitoring' (Candidates)...")
    one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
    resp_monitor = supabase.table('strategy_monitoring').select('*').gte('updated_at', one_hour_ago).gte('condition_match_score', 80).order('condition_match_score', desc=True).execute()
    
    print(f"Candidates in last 1h (Score >= 80): {len(resp_monitor.data)}")
    if resp_monitor.data:
         for m in resp_monitor.data[:5]:
             print(f" - {m['stock_name']} ({m['stock_code']}) - Score: {m['condition_match_score']} - Updated: {m['updated_at']}")

if __name__ == "__main__":
    check_signals()
