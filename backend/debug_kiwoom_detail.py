import os
import sys
from dotenv import load_dotenv
import json
import requests

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from api.kiwoom_client import get_kiwoom_client

load_dotenv()

client = get_kiwoom_client()
print(f"--- Debugging Kiwoom Detail (qry_tp=2) ---")
print(f"Account: {client.account_no}")

# Manually manual request to test qry_tp=2
token = client._get_access_token()
url = f"{client.base_url}/api/dostk/acnt"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "authorization": f"Bearer {token}",
    "api-id": "kt00018",
    "cont-yn": "N",
    "next-key": ""
}
data = {
    "qry_tp": "2",  # Detail Mode?
    "dmst_stex_tp": "KRX",
    "acnt_no": client.account_no if client.account_no else ""
}

try:
    response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
    response.raise_for_status()
    result = response.json()
    
    print(f"Top Level Keys: {result.keys()}")
    
    holdings = result.get('acnt_evlt_remn_indv_tot', [])
    print(f"Holdings Count: {len(holdings)}")
    if holdings:
        print(f"First Holding: {json.dumps(holdings[0], indent=2, ensure_ascii=False)}")
        
except Exception as e:
    print(f"Error: {e}")
