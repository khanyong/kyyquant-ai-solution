"""
Kiwoom Account Sync Verification Script
Fetches balance from Kiwoom API and Supabase DB to verify synchronization.
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from api.kiwoom_client import get_kiwoom_client
from supabase import create_client

def verify_sync():
    print("=" * 80)
    print("🔍 Kiwoom Account Sync Verification")
    print("=" * 80)

    # 1. Load Environment Variables
    load_dotenv()
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment")
        return

    # 2. Fetch from Kiwoom API
    print("\n[1] Fetching from Kiwoom API...")
    kiwoom = get_kiwoom_client()
    kiwoom_balance = kiwoom.get_account_balance()
    
    if not kiwoom_balance:
        print("❌ Failed to fetch balance from Kiwoom API (Expected for Mock Account)")
        kiwoom_balance = None
    else:
        print(f"✅ Kiwoom API Balance:")
        print(f"   - Total Asset: {kiwoom_balance['total_asset']:,.0f} KRW")
        print(f"   - Cash Balance: {kiwoom_balance['cash_balance']:,.0f} KRW")
        print(f"   - Stock Value: {kiwoom_balance['stock_value']:,.0f} KRW")
        print(f"   - Profit/Loss: {kiwoom_balance['profit_loss']:+,.0f} KRW")

    # 3. Fetch from Supabase
    print("\n[2] Fetching from Supabase DB...")
    supabase = create_client(supabase_url, supabase_key)
    
    # Get latest account balance
    response = supabase.table('kw_account_balance').select('*').order('updated_at', desc=True).limit(1).execute()
    
    if not response.data:
        print("⚠️ No account balance data found in Supabase")
        db_balance = None
    else:
        db_balance = response.data[0]
        print(f"ℹ️ DB Columns: {list(db_balance.keys())}")
        print(f"✅ Supabase DB Balance (Last Updated: {db_balance.get('updated_at')}):")
        print(f"   - Total Asset: {db_balance.get('total_asset', 0):,.0f} KRW")
        print(f"   - Cash Balance: {db_balance.get('cash_balance', db_balance.get('deposit', 0)):,.0f} KRW") # Try 'deposit' if cash_balance missing
        print(f"   - Stock Value: {db_balance.get('stock_value', 0):,.0f} KRW")
        print(f"   - Profit/Loss: {db_balance.get('profit_loss', 0):+,.0f} KRW")

    # 4. Compare
    print("\n[3] Comparison Result:")
    if db_balance:
        if kiwoom_balance:
            diff_asset = kiwoom_balance['total_asset'] - db_balance['total_asset']
            
            if abs(diff_asset) < 100:  # Allow small difference
                print("✅ Synchronization is UP-TO-DATE")
            else:
                print(f"❌ Synchronization is OUT-OF-SYNC (Difference: {diff_asset:+,.0f} KRW)")
                print("   -> Recommendation: Run 'python backend/run_balance_sync.py' or check if the service is running.")
        else:
            print("⚠️ Cannot compare: Kiwoom balance missing.")
            print(f"ℹ️ DB Last Updated: {db_balance['updated_at']}")
            
            # Check if updated recently (e.g. within 5 minutes)
            from datetime import datetime, timedelta, timezone
            
            # Parse DB time (handle Z or offset)
            db_time_str = db_balance['updated_at']
            if db_time_str.endswith('Z'):
                db_time_str = db_time_str[:-1] + '+00:00'
            
            db_time = datetime.fromisoformat(db_time_str)
            
            # Ensure both are timezone-aware or both naive
            now = datetime.now(timezone.utc)
            if db_time.tzinfo is None:
                db_time = db_time.replace(tzinfo=timezone.utc)
            
            diff = now - db_time
            print(f"ℹ️ Time since last update: {diff}")
            
            if diff < timedelta(minutes=5):
                 print("✅ DB was updated recently (Sync Service is likely working)")
            else:
                 print("⚠️ DB data is OLD (Sync Service might not be updating)")
    else:
        print("❌ Synchronization status: UNKNOWN (No DB data)")

if __name__ == "__main__":
    verify_sync()
