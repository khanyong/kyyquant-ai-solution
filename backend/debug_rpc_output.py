
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment variables.")
    exit(1)

supabase: Client = create_client(url, key)

def debug_rpc():
    print("Calling 'get_buy_candidates' RPC...")
    try:
        resp = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
        data = resp.data
        
        print(f"Total candidates: {len(data)}")
        
        if data:
            print("\nFirst candidate details:")
            item = data[0]
            for k, v in item.items():
                print(f"{k}: {v}")
                
            # Analysis
            price = item.get('current_price', 0)
            pos_size = item.get('position_size', 0)
            
            if price > 0:
                est_qty = pos_size / price
                print(f"\nEstimated Quantity check: {pos_size} / {price} = {est_qty}")
            else:
                print("\nError: Current Price is 0")
                
        else:
            print("No candidates found.")

    except Exception as e:
        print(f"RPC Call Error: {e}")

if __name__ == "__main__":
    debug_rpc()
