"""
Check the actual MACD code stored in Supabase
"""

from supabase import create_client
import os
from dotenv import load_dotenv
import json

load_dotenv('.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, key)

print("Fetching MACD indicator from Supabase...")
result = supabase.table('indicators').select('*').eq('name', 'macd').execute()

if not result.data:
    print("[ERROR] MACD indicator not found")
    exit(1)

indicator = result.data[0]

print(f"\n[OK] Found MACD indicator:")
print(f"  ID: {indicator['id']}")
print(f"  Name: {indicator['name']}")
print(f"  Output columns: {indicator.get('output_columns')}")
print(f"  Default params: {indicator.get('default_params')}")
print(f"  Calculation type: {indicator.get('calculation_type')}")

formula = indicator.get('formula')
print(f"\n  Formula type: {type(formula)}")
print(f"  Formula value: {formula}")

if formula:
    if isinstance(formula, str):
        try:
            formula = json.loads(formula)
        except:
            pass

    if isinstance(formula, dict):
        code = formula.get('code', '')
        print(f"\n[CODE] Length: {len(code)} characters")
        print(f"\n{code}")
    else:
        print(f"\n[ERROR] Formula is not a dict: {type(formula)}")
else:
    print("\n[ERROR] Formula is empty or None!")