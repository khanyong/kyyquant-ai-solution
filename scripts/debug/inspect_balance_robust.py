import os
import requests
import json
import time

def load_env():
    cwd = os.getcwd()
    fpath = os.path.join(cwd, '.env')
    print(f"[Setup] Loading .env from {fpath}")
    
    env_vars = {}
    if os.path.exists(fpath):
        for encoding in ['utf-8', 'cp949', 'latin-1']:
            try:
                with open(fpath, 'r', encoding=encoding) as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            k, v = line.strip().split('=', 1)
                            env_vars[k.strip()] = v.strip().strip('"').strip("'")
                print(f"[Setup] Loaded .env with {encoding}")
                return env_vars
            except UnicodeDecodeError:
                continue
    return env_vars

def main():
    env = load_env()
    
    # Credentials
    APP_KEY = env.get('KIWOOM_APP_KEY')
    APP_SECRET = env.get('KIWOOM_APP_SECRET')
    ACCOUNT_NO = env.get('KIWOOM_ACCOUNT_NO')
    IS_DEMO = True # Force Demo for this test
    
    print(f"\n[Config] ACCOUNT_NO: '{ACCOUNT_NO}' (Len: {len(ACCOUNT_NO) if ACCOUNT_NO else 0})")
    print(f"[Config] IS_DEMO: {IS_DEMO}")
    
    if not APP_KEY or not APP_SECRET:
        print("[Error] Missing API Keys")
        return

    # Base URL
    BASE_URL = "https://mockapi.kiwoom.com" if IS_DEMO else "https://api.kiwoom.com"
    
    # 1. Get Token (Simple fetch, no cache for debug)
    print("\n[1] Fetching Access Token...")
    token_url = f"{BASE_URL}/oauth2/token"
    # Match TokenManager: Use JSON
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "secretkey": APP_SECRET  # CORRECT KEY NAME
    }
    
    try:
        # Use json=data to send as JSON body
        res = requests.post(token_url, headers=headers, json=data, timeout=10)
        res.raise_for_status()
        
        body = res.json()
        print(f"[1] Token Response Body: {json.dumps(body)}")
        
        token = body.get('access_token') or body.get('token')
        if not token:
             print("[Error] No access_token found!")
             return
             
        print(f"[1] Token Received: {token[:10]}...")
    except Exception as e:
        print(f"[Error] Token Fetch Failed: {e}")
        if hasattr(e, 'response') and e.response:
             print(e.response.text)
        return

    # 2. Fetch Balance (Holdings)
    print("\n[2] Fetching Balance (Detail)...")
    url = f"{BASE_URL}/api/dostk/acnt"
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "authorization": f"Bearer {token}",
        "api-id": "kt00018", # Balance API
        "cont-yn": "N",
        "next-key": ""
    }
    
    # Payload
    # CRITICAL: We explicitly send acnt_no with hyphens
    payload = {
        "qry_tp": "2", # 2=Detail/Holdings
        "dmst_stex_tp": "KRX",
        "acnt_no": ACCOUNT_NO 
    }
    
    print(f"[2] Payload: {json.dumps(payload)}")
    
    # Retry Loop for 429
    max_retries = 3
    for i in range(max_retries):
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            
            if res.status_code == 429:
                print(f"[Warn] 429 Too Many Requests. Retrying in 5 seconds... ({i+1}/{max_retries})")
                time.sleep(5)
                continue
                
            print(f"\n[3] Response Status: {res.status_code}")
            print("[3] Raw Body:")
            print(json.dumps(res.json(), indent=2, ensure_ascii=False))
            break
            
        except Exception as e:
            print(f"[Error] Request Failed: {e}")
            break

if __name__ == "__main__":
    main()
