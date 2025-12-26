import os
import requests
import json
import sys

# Load env
env_vars = {}
cwd = os.getcwd()

# Try loading .env files
cwd = os.getcwd()
files_to_try = ['.env.development', '.env']
found_env = False

# Force load .env which has the keys
fpath = os.path.join(cwd, '.env')
if os.path.exists(fpath):
    print(f"Loading env from: {fpath}")
    loaded = False
    for encoding in ['utf-8', 'cp949', 'latin-1']:
        try:
            with open(fpath, 'r', encoding=encoding) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        k, v = line.strip().split('=', 1)
                        v = v.strip().strip('"').strip("'")
                        env_vars[k.strip()] = v
                        os.environ[k.strip()] = v
            loaded = True
            print(f"Successfully loaded .env with {encoding}")
            break
        except UnicodeDecodeError:
            continue
    if not loaded:
        print("Error: Failed to decode .env file!")
        exit(1)
else:
    print("Error: .env file not found!")
    exit(1)

# Debug Keys
print(f"Keys Loaded: KIWOOM_APP_KEY={bool(os.environ.get('KIWOOM_APP_KEY'))}, ACCOUNT={os.environ.get('KIWOOM_ACCOUNT_NO')}")

# FORCE DEMO MODE TO TEST KEY VALIDITY
print("--- FORCING DEMO MODE TO TEST KEY VALIDITY ---")
os.environ['KIWOOM_IS_DEMO'] = 'true'
# Re-import or clear singleton if needed, but in this script we create it fresh.
# However, we need to ensure we don't import before setting env?
# We imported at the top? No, inside try block.

# Adjust base_url for manual requests too
is_demo = True 
base_url = "https://mockapi.kiwoom.com"


# We need a token. We can't easily import TokenManager due to dependencies.
# We'll try to get it from the running backend if possible, or just re-authenticate if we had credentials.
# But simpler: Let's assume the user can run this where backend code is imports.
# Actually, let's just use the backend code directly by adding to sys.path
sys.path.append(os.path.join(cwd, 'backend'))

try:
    from api.kiwoom_client import get_kiwoom_client
    client = get_kiwoom_client()
    
    print(f"--- Diagnosing Kiwoom API Balance (Mode: {'DEMO' if client.is_demo else 'REAL'}) ---")
    print(f"Base URL: {client.base_url}")
    print(f"Account: {client.account_no}")
    
    token = client._get_access_token()
    print(f"Token obtained: {token[:10]}...")

    # Manual Request to see RAW response
    url = f"{client.base_url}/api/dostk/acnt"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {token}",
        "api-id": "kt00018",
        "cont-yn": "N",
        "next-key": ""
    }
    
    # 1. Summary
    data_summary = {"qry_tp": "1", "dmst_stex_tp": "KRX"}
    # ALWAYS SEND ACCOUNT NO
    data_summary["acnt_no"] = client.account_no
         
    res = requests.post(url, headers=headers, data=json.dumps(data_summary))
    print(f"\n[Raw Response - Summary]: {res.status_code}")
    print(json.dumps(res.json(), indent=2, ensure_ascii=False))

    # 2. Detail (Holdings)
    data_detail = {"qry_tp": "2", "dmst_stex_tp": "KRX"}
    # ALWAYS SEND ACCOUNT NO
    data_detail["acnt_no"] = client.account_no
         
    res2 = requests.post(url, headers=headers, data=json.dumps(data_detail))
    print(f"\n[Raw Response - Holdings]: {res2.status_code}")
    print(json.dumps(res2.json(), indent=2, ensure_ascii=False))
    
    # Check what Python sees
    print("\n[Client Parsed Result]")
    parsed = client.get_account_balance()
    print(f"Holdings Count: {len(parsed['holdings'])}")
    for h in parsed['holdings']:
        print(f" - {h['stock_name']} ({h['stock_code']}) Qty: {h['quantity']}")

except Exception as e:
    print(f"Error: {e}")
