import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

APP_KEY = os.getenv('KIWOOM_APP_KEY')
APP_SECRET = os.getenv('KIWOOM_APP_SECRET')
ACCOUNT_NO = os.getenv('KIWOOM_ACCOUNT_NO')
IS_DEMO = os.getenv('KIWOOM_IS_DEMO', 'true').lower() == 'true'

print(f"Debug Env: KEY={bool(APP_KEY)}, SECRET={bool(APP_SECRET)}, ACC={ACCOUNT_NO}")

BASE_URL = "https://mockapi.kiwoom.com" if IS_DEMO else "https://api.kiwoom.com"

def get_token():
    if not APP_KEY or not APP_SECRET:
        print("Missing Credentials")
        return None
    
    urls_to_try = [
        f"{BASE_URL}/oauth2/token",
        "https://openapi.kiwoom.com:9443/oauth2/token", # Used in websocket code
        "https://api.kiwoom.com/oauth2/token"
    ]
    
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = {"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET}
    
    for url in urls_to_try:
        try:
            print(f"Trying Token URL: {url}")
            res = requests.post(url, headers=headers, data=json.dumps(data), timeout=5)
            if res.status_code == 200:
                print("Token Success!")
                js = res.json()
                print(f"Token Response Keys: {js.keys()}")
                return js.get('access_token') or js.get('token')
            else:
                print(f"Token Failed ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"Token Connection Failed ({url}): {e}")
            
    return None

def debug_profit_fields():
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    url = f"{BASE_URL}/api/dostk/acnt"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {token}",
        "api-id": "kt00018",
        "cont-yn": "N",
        "next-key": ""
    }
    
    # Query Type 1: Summary
    data_sum = {
        "qry_tp": "1",
        "dmst_stex_tp": "KRX",
        "acnt_no": ACCOUNT_NO
    }
    
    print("\n--- [Query Type 1: Account Summary] ---")
    res1 = requests.post(url, headers=headers, data=json.dumps(data_sum))
    json1 = res1.json()
    
    # Print purely profit related keys
    for k, v in json1.items():
        if 'pfls' in k or 'evlu' in k or 'amt' in k or 'rt' in k:
            print(f"{k}: {v}")

    # Query Type 2: Holdings
    data_det = {
        "qry_tp": "2",
        "dmst_stex_tp": "KRX",
        "acnt_no": ACCOUNT_NO
    }
    
    print("\n--- [Query Type 2: Individual Holdings] ---")
    res2 = requests.post(url, headers=headers, data=json.dumps(data_det))
    json2 = res2.json()
    
    details = json2.get('acnt_evlt_remn_indv_tot', [])
    for item in details:
        print(f"\nStock: {item.get('stk_nm')} ({item.get('stk_cd')})")
        # Print all keys for inspection
        for k, v in item.items():
            if 'prft' in k or 'pfls' in k or 'evl' in k or 'amt' in k or 'fee' in k or 'tax' in k:
                print(f"  {k}: {v}")

if __name__ == "__main__":
    debug_profit_fields()
