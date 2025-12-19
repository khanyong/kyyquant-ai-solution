
import os
import asyncio
import math
import requests
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime, timedelta

load_dotenv()

# Config
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role to ensure permissions
BACKEND_URL = "http://localhost:8001" 

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

async def simulate_workflow():
    print("=== Simulating N8N Buy Workflow ===")
    
    # 1. Get Buy Candidates (RPC)
    print("\n[1] Calling get_buy_candidates...")
    rpc = supabase.rpc('get_buy_candidates', {'min_score': 0}).execute()
    candidates = rpc.data if rpc.data else []
    print(f"Candidates found: {len(candidates)}")
    
    if not candidates:
        print("No candidates. Workflow ends.")
        return

    # 2. Get Balance
    print("\n[2] Getting Balance...")
    bal_res = supabase.table('kw_account_balance').select('order_cash').limit(1).execute()
    if not bal_res.data:
        print("No balance data.")
        return
    
    account_cash = float(bal_res.data[0]['order_cash'])
    print(f"Account Cash: {account_cash:,.0f}")
    
    # Process each candidate
    for stock in candidates:
        print(f"\n[Processing] {stock['stock_name']} ({stock['stock_code']})")
        
        # 3. Calculate Order Details
        strategy_budget = float(stock.get('available_for_next_order', 0))
        current_price = float(stock.get('current_price', 0))
        
        if current_price <= 0:
            print("Invalid price, skipping.")
            continue
            
        final_budget = min(strategy_budget, account_cash)
        quantity = math.floor(final_budget / current_price)
        
        print(f"  Strategy Budget: {strategy_budget:,.0f}")
        print(f"  Final Budget: {final_budget:,.0f}")
        print(f"  Price: {current_price:,.0f}")
        print(f"  Quantity: {quantity}")
        
        if quantity <= 0:
            print("Quantity 0, skipping.")
            continue
            
        # 4. Send Order to Kiwoom (Backend)
        print("  [Step 4] Sending Order to Backend...")
        order_payload = {
            "stock_code": stock['stock_code'],
            "order_type": "buy",
            "price": current_price,
            "quantity": quantity
        }
        
        try:
            # Note: /api/order/order -> order_type needs to be lowercase 'buy' in api/order.py
            # But N8N sends 'BUY' (uppercase). 
            # api/order.py -> pattern="^(buy|sell)$" (lowercase!)
            # WAIT! N8N sends 'BUY'. api/order.py checks lowercase regex?
            # Let's check api/order.py regex again.
            
            # Sending 'buy' (lowercase) to be safe for now, but will test N8N's suspect param later.
            resp = requests.post(f"{BACKEND_URL}/api/order/order", json=order_payload)
            
            if resp.status_code != 200:
                print(f"  FAILED: {resp.text}")
                continue
                
            order_res = resp.json()
            print(f"  Order Success: {order_res.get('order_no')}")
            
            # 5. Insert Order to DB
            print("  [Step 5] Inserting Order to DB...")
            auto_cancel_at = (datetime.now() + timedelta(minutes=30)).isoformat()
            
            order_record = {
                "strategy_id": stock['strategy_id'],
                "stock_code": stock['stock_code'],
                "stock_name": stock['stock_name'],
                "order_type": "BUY",
                "order_price": current_price,
                "quantity": quantity,
                "status": "PENDING",
                "auto_cancel_at": auto_cancel_at,
                "cancel_after_minutes": 30,
                "kiwoom_order_no": order_res.get('order_no'),
                "created_at": datetime.now().isoformat()
            }
            ord_db_res = supabase.table('orders').insert(order_record).execute()
            order_id = ord_db_res.data[0]['id']
            print(f"  DB Order ID: {order_id}")
            
            # 6. Update Trading Signal
            print("  [Step 6] Updating Trading Signal...")
            signal_record = {
                "strategy_id": stock['strategy_id'],
                "stock_code": stock['stock_code'],
                "stock_name": stock['stock_name'],
                "signal_type": "BUY",
                "current_price": current_price,
                "order_id": order_id,
                "signal_status": "ORDERED",
                "created_at": datetime.now().isoformat() # This forces INSERT
            }
            # UPSERT logic in N8N uses `on_conflict` but unique key usually includes created_at??
            # Actually N8N probably just Inserts a new row.
            supabase.table('trading_signals').insert(signal_record).execute()
            print("  Signal Saved!")
            
        except Exception as e:
            print(f"  Error processing stock: {e}")

if __name__ == "__main__":
    asyncio.run(simulate_workflow())
