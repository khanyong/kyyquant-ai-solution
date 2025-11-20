"""
MACD 지표의 calculation_type을 builtin으로 수정 (ID 사용)
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, key)

macd_id = '134ecf94-fcec-4b75-81ef-05ef498750ad'

print(f"Updating MACD (ID: {macd_id}) calculation_type to 'builtin'...")

# ID로 업데이트
response = supabase.table('indicators').update({
    'calculation_type': 'builtin'
}).eq('id', macd_id).execute()

print(f"[OK] Updated {len(response.data)} record(s)")

# 검증
verify = supabase.table('indicators').select('name, calculation_type').eq('id', macd_id).execute()

if verify.data:
    indicator = verify.data[0]
    print("\n[OK] Verification:")
    print(f"  Name: {indicator['name']}")
    print(f"  Calculation Type: {indicator['calculation_type']}")

    if indicator['calculation_type'] == 'builtin':
        print("\n[SUCCESS] MACD calculation_type is now 'builtin'")
        print("\nNow test backtest on NAS server!")
    else:
        print(f"\n[ERROR] Expected 'builtin', got '{indicator['calculation_type']}'")