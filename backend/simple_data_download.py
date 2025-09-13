"""
Simple data download script without unicode issues
NAS -> Supabase data pipeline
"""

import requests
import json
from datetime import datetime
from supabase import create_client
import os
from dotenv import load_dotenv
import sys

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def download_and_save():
    """Simple data download and save to Supabase"""

    # Configuration
    nas_url = "http://192.168.50.150:8080"
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    print("=" * 50)
    print("Data Download Test")
    print("=" * 50)

    # Test stocks
    stocks = ['005930', '000660', '035720']  # Samsung, SK Hynix, Kakao

    try:
        supabase = create_client(supabase_url, supabase_key)
        print(f"Supabase connected: {supabase_url[:30]}...")

        for stock_code in stocks:
            print(f"\nProcessing: {stock_code}")

            # 1. Get current price from NAS
            response = requests.post(
                f"{nas_url}/api/market/current-price",
                json={"stock_code": stock_code},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    output = data['data']['output']

                    # 2. Prepare data for Supabase
                    price_data = {
                        'stock_code': stock_code,
                        'current_price': int(output['stck_prpr']),
                        'change_price': int(output.get('prdy_vrss', 0)),
                        'change_rate': float(output['prdy_ctrt']),
                        'volume': int(output['acml_vol']),
                        'trading_value': int(output.get('acml_tr_pbmn', 0)),
                        'high_52w': int(output.get('stck_mxpr', 0)),
                        'low_52w': int(output.get('stck_llam', 0)),
                        'market_cap': 0,
                        'shares_outstanding': 0,
                        'foreign_ratio': 0.0,
                        'updated_at': datetime.now().isoformat()
                    }

                    print(f"  Price: {price_data['current_price']:,} won")
                    print(f"  Change: {price_data['change_rate']}%")

                    # 3. Save to Supabase
                    result = supabase.table('kw_price_current').upsert(price_data).execute()
                    print(f"  Saved to Supabase: OK")

                    # 4. Verify saved data
                    saved = supabase.table('kw_price_current').select("*").eq('stock_code', stock_code).execute()
                    if saved.data:
                        print(f"  Verified: {saved.data[0]['current_price']:,} won")
                    else:
                        print(f"  Verification: FAILED")

                else:
                    print(f"  API Error: {data}")
            else:
                print(f"  HTTP Error: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("Data download completed")
    print("=" * 50)

if __name__ == "__main__":
    download_and_save()