
import os
import sys
import time
import yfinance as yf
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def get_supabase_client():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    if not url or not key:
        print("[ERROR] Supabase credentials missing")
        return None
    return create_client(url, key)

def update_market_indices():
    """
    Fetch market indices from Yahoo Finance and update Supabase 'market_index' table
    """
    supabase = get_supabase_client()
    if not supabase:
        return

    # Mapping: Frontend Code -> Yahoo Ticker
    indices = {
        'KOSPI': '^KS11',
        'KOSDAQ': '^KQ11',
        'USD_KRW': 'KRW=X',
        'SPX': '^GSPC',
        'COMP': '^IXIC',
        'IEF': 'IEF',
        'TLT': 'TLT',
        'LQD': 'LQD'
    }

    print(f"[{datetime.now()}] Starting Market Index Update...")

    for code, ticker_symbol in indices.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            
            # Use history(period="5d") as primary method (more robust than fast_info)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                print(f"  [FAIL] {code}: Empty history")
                continue

            current_price = float(hist['Close'].iloc[-1])
            prev_close = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
            
            # Additional fallback check if current_price is NaN
            import math
            if math.isnan(current_price):
                 current_price = prev_close

            change_value = current_price - prev_close
            change_rate = (change_value / prev_close) * 100 if prev_close != 0 else 0
            
            # Upsert to Supabase
            data = {
                'index_id': code, # Use code as ID
                'index_code': code,
                'current_value': round(current_price, 2),
                'change_value': round(change_value, 2),
                'change_rate': round(change_rate, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            # 'market_index' table must exist with 'index_code' as primary key or unique
            result = supabase.table('market_index').upsert(data, on_conflict='index_code').execute()
            print(f"  [OK] {code}: {current_price:.2f} ({change_rate:+.2f}%)")
                
        except Exception as e:
            print(f"  [ERROR] {code}: {str(e)}")

def main():
    update_market_indices()

if __name__ == "__main__":
    main()
