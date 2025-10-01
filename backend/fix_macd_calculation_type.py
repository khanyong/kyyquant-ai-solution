"""
MACD 지표의 calculation_type을 builtin으로 수정
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv('.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

supabase = create_client(url, key)

print("Updating MACD calculation_type to 'builtin'...")

# 업데이트
response = supabase.table('indicators').update({
    'calculation_type': 'builtin'  # python_code -> builtin
}).eq('name', 'macd').execute()

print(f"[OK] Updated {len(response.data)} record(s)")

# 검증
verify = supabase.table('indicators').select('name, calculation_type').eq('name', 'macd').execute()

if verify.data:
    indicator = verify.data[0]
    print("\n[OK] Verification:")
    print(f"  Name: {indicator['name']}")
    print(f"  Calculation Type: {indicator['calculation_type']}")

    if indicator['calculation_type'] == 'builtin':
        print("\n[SUCCESS] MACD calculation_type is now 'builtin'")
    else:
        print(f"\n[ERROR] Expected 'builtin', got '{indicator['calculation_type']}'")