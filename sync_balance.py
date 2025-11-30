
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load .env manually to ensure we get VITE keys if needed, 
# but KiwoomClient uses KIWOOM_ prefixed keys which are in .env
load_dotenv()

from backend.api.kiwoom_client import KiwoomAPIClient

def main():
    print("Initializing Kiwoom Client...")
    client = KiwoomAPIClient()
    
    print("Getting Account Balance...")
    balance = client.get_account_balance()
    
    if balance:
        print("Balance:", balance)
    else:
        print("Failed to get balance.")

    print("Getting Holdings...")
    holdings = client.get_holdings()
    
    if holdings:
        print(f"Holdings: {len(holdings)} items")
        for h in holdings:
            print(f"- {h['stock_name']}: {h['quantity']} shares")
    else:
        print("Failed to get holdings.")

if __name__ == "__main__":
    main()
