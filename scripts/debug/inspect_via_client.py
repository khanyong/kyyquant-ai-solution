import sys
import os
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from api.kiwoom_client import KiwoomAPIClient

def test_live_client():
    print("--- Live Kiwoom Client Test ---")
    
    # Check Env
    if not os.getenv('KIWOOM_APP_KEY'):
        # Try load .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("[Setup] Loaded .env")
        except:
            print("[Setup] dotenv not found, assuming env vars set or checking file manually")
            # Minimal env loader if dotenv missing
            pass

    client = KiwoomAPIClient()
    print(f"Client initialized. Account: {client.account_no}")
    
    print("Calling get_account_balance()...")
    try:
        result = client.get_account_balance()
        print(f"Result Type: {type(result)}")
        
        if isinstance(result, list):
             print("❌ FAILED: Returned empty list (Exception caught inside).")
             # Exception print should be in stderr
        else:
             holdings = result.get('holdings', [])
             print(f"✅ SUCCESS: Got Result. Holdings Count: {len(holdings)}")
             for h in holdings:
                 print(f" - {h['stock_name']} ({h['stock_code']}) : {h['quantity']} @ {h['current_price']}")
                 
                 # [TEST] Try Selling 1 share of the first holding
                 if h['quantity'] > 0:
                     print(f"\n[TEST ALERT] Attempting to SELL 1 share of {h['stock_name']} ({h['stock_code']})...")
                     try:
                        # order_type='sell', price=0 (Market)
                        order_res = client.order_stock(h['stock_code'], 1, 0, 'sell')
                        print(f"Order Result: {json.dumps(order_res, indent=2, ensure_ascii=False)}")
                     except Exception as oe:
                        print(f"Order Failed: {oe}")
                     break # Try only one
                 
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")

if __name__ == "__main__":
    test_live_client()
