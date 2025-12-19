
import asyncio
import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client
from backtest.engine import BacktestEngine
from api.strategy import _sanitize_for_json

# Load env from .env file up one directory or current
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    print("Error: SUPABASE_URL not found in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def debug_strategy():
    print("=== Strategy Logic Debugger ===")
    
    # 1. Fetch Strategy
    print("1. Fetching 'kyy_short_term_v01' strategy...")
    strategies = supabase.table('strategies').select('*').execute()
    target_strategy = None
    for s in strategies.data:
        # Assuming the user meant one of these, or we pick the first one
        print(f"   Found strategy: {s.get('name')} (ID: {s.get('id')})")
        if 'kyy' in s.get('name', '').lower() or 'short' in s.get('name', '').lower():
            target_strategy = s
            break
    
    if not target_strategy:
        if len(strategies.data) > 0:
            target_strategy = strategies.data[0]
            print(f"   Target not found, selecting first available: {target_strategy['name']}")
        else:
            print("   No strategies found in DB.")
            return

    config = target_strategy.get('config') or target_strategy
    print(f"   Strategy Selected: {target_strategy.get('name')}")
    print(f"   Buy Conditions: {config.get('buyConditions')}")
    print(f"   Indicators: {config.get('indicators')}")

    # 2. Fetch Data for a sample stock
    stock_code = "100250" # Sample from walkthrough
    print(f"\n2. Fetching data for stock {stock_code}...")
    
    p_resp = supabase.table('kw_price_daily').select('trade_date,open,high,low,close,volume').eq('stock_code', stock_code).order('trade_date', desc=False).limit(200).execute()
    
    if not p_resp.data:
        print("   No data found for stock.")
        return

    df = pd.DataFrame(p_resp.data)
    df['trade_date'] = pd.to_datetime(df['trade_date'])
    df.set_index('trade_date', inplace=True)
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"   Loaded {len(df)} rows. Last date: {df.index[-1]}")
    print(f"   Last Close: {df.iloc[-1]['close']}")

    # 3. Request current price (Mock or Fetch)
    # We will just use the last close for this test to permit "offline" debugging if market is closed
    pass

    # 4. Run Engine
    print("\n3. Running BacktestEngine.evaluate_snapshot...")
    engine = BacktestEngine()
    
    try:
        result = await engine.evaluate_snapshot(stock_code, df, config)
        
        print("\n=== EVALUATION RESULTS ===")
        print(f"Signal: {result.get('signal')}")
        print(f"Score: {result.get('score')}")
        print(f"Reasons: {result.get('reasons')}")
        
        print("\n--- Calculated Indicators (Last Row) ---")
        indicators = result.get('indicators', {})
        for k, v in indicators.items():
            print(f"   {k}: {v}")
            
    except Exception as e:
        print(f"Engine Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_strategy())
