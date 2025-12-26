import os
import sys
import pandas as pd
import asyncio
from datetime import datetime
# Force UTF-8 Output
sys.stdout.reconfigure(encoding='utf-8')
from supabase import create_client

# Add project root and backend to sys.path
sys.path.append('d:\\Dev\\auto_stock')
sys.path.append('d:\\Dev\\auto_stock\\backend')

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

async def analyze_signals():
    manual_load_env()
    url = os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Credentials missing")
        return

    supabase = create_client(url, key)
    
    print("=== Signal Generation Diagnosis ===")
    
    # 1. Check Data Freshness
    print("\n[1] Checking Data Freshness (kw_price_daily)...")
    try:
        res = supabase.table('kw_price_daily').select('trade_date').order('trade_date', desc=True).limit(1).execute()
        if res.data:
            latest = res.data[0]['trade_date']
            print(f"Latest DB Date: {latest}")
            # Simple check if it's recent (e.g. within 5 days)
            last_date = pd.to_datetime(latest)
            if (datetime.now() - last_date).days > 5:
                print("⚠️ WARNING: Data seems stale (> 5 days old). Signals might not generate.")
        else:
            print("⚠️ ERROR: No daily price data found.")
    except Exception as e:
        print(f"Error checking date: {e}")

    # 2. Dry Run Strategy on Samsung Elec (005930)
    target_code = '005930'
    print(f"\n[2] Dry Run: {target_code} (Samsung Electronics)")
    
    try:
        # Fetch Strategy Config (MACD)
        s_res = supabase.table('strategies').select('*').eq('name', 'TEST_STRATEGY_A_MACD').single().execute()
        if not s_res.data:
            print("Strategy TEST_STRATEGY_A_MACD not found.")
            return
            
        strategy = s_res.data
        config = strategy.get('config') or strategy
        print(f"Strategy: {strategy['name']}")
        print(f"Entry Conditions: {config.get('entry_conditions')}")
        
        # Fetch Price Data
        p_res = supabase.table('kw_price_daily').select('*').eq('stock_code', target_code).order('trade_date', desc=False).limit(300).execute()
        if not p_res.data:
            print("No price data for Samsung Elec.")
            return
            
        df = pd.DataFrame(p_res.data)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df.set_index('trade_date', inplace=True)
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        print(f"Loaded {len(df)} rows. Last row: {df.index[-1].date()} Close: {df.iloc[-1]['close']}")
        
        # Import Engine
        from backend.backtest.engine import BacktestEngine
        engine = BacktestEngine()
        
        # Evaluate
        print("\n--- Evaluating Logic ---")
        result = await engine.evaluate_snapshot(target_code, df, config)
        
        print(f"Result Signal: {result.get('signal')}")
        print(f"Score: {result.get('score')}")
        print(f"Indicators: {result.get('indicators')}")
        print(f"Reasons: {result.get('reasons')}")
        
        # Verify MACD logic specifically if result is HOLD
        if result.get('signal') == 'hold':
            inds = result.get('indicators', {})
            # Check if MACD exists
            if 'MACD' in inds:
                macd = inds['MACD'].get('macd')
                signal = inds['MACD'].get('signal')
                hist = inds['MACD'].get('macd_hist')
                print(f"\n[Analysis] MACD: {macd}, Signal: {signal}, Hist: {hist}")
                print(f"Logic: MACD > Signal (Golden Cross) required for BUY.")
                if macd is not None and signal is not None:
                     if macd <= signal:
                         print("=> Reason: MACD is below Signal line (No Buy).")
                     else:
                         print("=> MACD is above Signal line. Why no buy? Check thresholds/logic.")
            else:
                print("=> MACD indicators missing in result.")
                    


    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error checking strategy: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_signals())
