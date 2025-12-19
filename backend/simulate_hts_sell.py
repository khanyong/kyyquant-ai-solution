import os
import sys
import datetime
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
target_user = 'f912da32-897f-4dbb-9242-3a438e9733a8'

print(f"--- Simulating HTS Sell Event for User {target_user} ---")

# 1. Fetch a holding to sell
print("1. Fetching current portfolio...")
port_res = supabase.table('portfolio').select('*').eq('user_id', target_user).execute()

if not port_res.data:
    print("❌ No holdings found in portfolio. Nothing to sell.")
    sys.exit(0)

# Pick the first one
holding = port_res.data[0]
print(f"Debug: Available keys in portfolio row: {holding.keys()}")

stock_code = holding['stock_code']
stock_name = holding.get('stock_name', stock_code) # fallback if name not there
quantity = float(holding['quantity'])
# Try logical alternatives for average price
avg_price = float(holding.get('avg_buy_price', holding.get('average_price', holding.get('purchase_price', 10000))))

# Simulate selling at +5% profit
sell_price = int(avg_price * 1.05)
total_amount = int(quantity * sell_price)

print(f"▶ Target Stock: {stock_name} ({stock_code})")
print(f"▶ Quantity: {quantity}")
print(f"▶ Avg Price: {avg_price:,.0f}")
print(f"▶ Simulation Sell Price: {sell_price:,.0f} (+5%)")
print(f"▶ Total Cash Required: {total_amount:,.0f}")

# 2. Update Balance (Add Cash)
print("\n2. Updating Account Balance (Adding Cash)...")
bal_res = supabase.table('account_balance').select('*').eq('user_id', target_user).execute()

if bal_res.data:
    balance = bal_res.data[0]
    current_cash = float(balance['available_cash'])
    new_cash = current_cash + total_amount
    
    # Update balance
    supabase.table('account_balance').update({
        'available_cash': new_cash,
        'updated_at': datetime.datetime.now().isoformat()
    }).eq('user_id', target_user).execute()
    
    print(f"✅ Cash Updated: {current_cash:,.0f} -> {new_cash:,.0f} (+{total_amount:,.0f})")
else:
    print("❌ Account balance not found!")

# 3. Delete Holding (Remove from Portfolio)
print(f"\n3. Removing Stock {stock_code} from Portfolio...")
# Using stock_code and user_id to identify the row
del_res = supabase.table('portfolio').delete().eq('user_id', target_user).eq('stock_code', stock_code).execute()

print(f"✅ Stock {stock_code} Sold (Removed from DB).")

print("\n---------------------------------------------------")
print("🎉 Simulation Complete!")
print("Please go to the UI and click '새로고침' (Refresh) button.")
print("You should see:")
print(f"1. {stock_name} is gone from the list.")
print(f"2. Available Cash increased by {total_amount:,.0f} KRW.")
print("---------------------------------------------------")
