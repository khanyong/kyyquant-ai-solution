import os
import sys
from dotenv import load_dotenv
import json

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from api.kiwoom_client import get_kiwoom_client

load_dotenv()

client = get_kiwoom_client()
print(f"--- Debugging Kiwoom Holdings (Account: {client.account_no}) ---")

data = client.get_account_balance()
print(f"Summary Keys: {data.get('summary', {}).keys()}")
print(f"Holdings Count: {len(data.get('holdings', []))}")
print(f"Holdings Data: {json.dumps(data.get('holdings', []), indent=2, ensure_ascii=False)}")

if not data.get('holdings'):
    print("WARNING: No holdings found. Checking raw response requires modifying client code or trying different qry_tp.")
