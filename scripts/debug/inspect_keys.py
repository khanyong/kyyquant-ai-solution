import os
import requests
import json

def load_keys():
    env = {}
    try:
        with open('.env', 'r', encoding='cp949') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k,v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    except:
        # Fallback to utf8
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    k,v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_keys()
APP_KEY = env.get('KIWOOM_APP_KEY')
APP_SECRET = env.get('KIWOOM_APP_SECRET')
ACNT = env.get('KIWOOM_ACCOUNT_NO')

print(f"Auth with: {APP_KEY[:5]}... / {ACNT}")

# Token
res = requests.post(
    "https://mockapi.kiwoom.com/oauth2/token",
    headers={"content-type":"application/json;charset=UTF-8"},
    json={"grant_type":"client_credentials", "appkey":APP_KEY, "secretkey":APP_SECRET}
)
try:
    data = res.json()
    token = data.get('access_token') or data.get('token')
    if not token:
        raise Exception("No token found")
except:
    print("Token Error:", res.text)
    exit(1)

# Balance
res = requests.post(
    "https://mockapi.kiwoom.com/api/dostk/acnt",
    headers={
        "authorization": f"Bearer {token}",
        "content-type": "application/json;charset=UTF-8",
        "api-id": "kt00018"
    },
    json={
        "qry_tp": "2",
        "dmst_stex_tp": "KRX",
        "acnt_no": ACNT
    }
)
body = res.json()
print("\n[Topology Check]")
print("Top Keys:", list(body.keys()))
if 'output' in body:
    print("Output Keys:", list(body['output'].keys()))
if 'acnt_evlt_remn_indv_tot' in body:
    print("Found 'acnt_evlt_remn_indv_tot' at TOP Level")
    print("Count:", len(body['acnt_evlt_remn_indv_tot']))
