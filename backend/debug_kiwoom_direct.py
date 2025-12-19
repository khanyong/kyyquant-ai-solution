
import sys
import os
import asyncio
from dotenv import load_dotenv

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(__file__))
sys.path.append(backend_dir)

load_dotenv()

from api.kiwoom_client import get_kiwoom_client

async def test_balance():
    client = get_kiwoom_client()
    print("Fetching account balance from KiwoomClient...")
    
    # Force detail mode logic if applicable? get_account_balance handles it.
    balance = client.get_account_balance()
    
    print("\n[Result from get_account_balance]:")
    print(balance)
    
    if balance and 'summary' in balance:
        print("\n[Summary Data]:")
        for k, v in balance['summary'].items():
            print(f"{k}: {v}")
            
    if balance and 'holdings' in balance:
        print(f"\n[Holdings Count]: {len(balance['holdings'])}")
        # Calculate totals manually to see what they SHOULD be
        calc_total_eval = sum([h['current_price'] * h['quantity'] for h in balance['holdings']])
        print(f"[Calculated Total Evaluation]: {calc_total_eval}")

if __name__ == "__main__":
    asyncio.run(test_balance())
