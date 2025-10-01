"""
MACD 지표 수정 - params 기본값 명시
"""

from supabase import create_client
import os
from dotenv import load_dotenv
import json

load_dotenv('.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

supabase = create_client(url, key)

# 새 코드 - params 기본값을 명시적으로 설정
new_code = """fast = params.get('fast', 12)
slow = params.get('slow', 26)
signal = params.get('signal', 9)

exp1 = df["close"].ewm(span=fast, adjust=False).mean()
exp2 = df["close"].ewm(span=slow, adjust=False).mean()
macd = exp1 - exp2
macd_signal = macd.ewm(span=signal, adjust=False).mean()
macd_hist = macd - macd_signal

result = {"macd": macd, "macd_signal": macd_signal, "macd_hist": macd_hist}"""

print("Updating MACD indicator with explicit params...")
print(f"New code:\n{new_code}\n")

# 업데이트
response = supabase.table('indicators').update({
    'formula': {'code': new_code},
    'output_columns': ['macd', 'macd_signal', 'macd_hist'],
    'default_params': json.dumps({'fast': 12, 'slow': 26, 'signal': 9})
}).eq('name', 'macd').execute()

print(f"[OK] Updated {len(response.data)} record(s)")

# 검증
verify = supabase.table('indicators').select('*').eq('name', 'macd').execute()

if verify.data:
    indicator = verify.data[0]
    print("\n[OK] Verification:")
    print(f"  Name: {indicator['name']}")
    print(f"  Output Columns: {indicator['output_columns']}")
    print(f"  Default Params: {indicator.get('default_params')}")

    formula = indicator['formula']
    if isinstance(formula, str):
        formula = json.loads(formula)

    code = formula.get('code', '')

    # 체크
    checks = {
        'Has params.get lines': 'params.get' in code,
        'Sets fast variable': 'fast = params.get' in code,
        'Sets slow variable': 'slow = params.get' in code,
        'Sets signal variable': 'signal = params.get' in code,
        'Uses "macd" (not "macd_line")': '"macd":' in code,
        'Sets result variable': 'result =' in code,
    }

    print("\n  Checks:")
    for check, passed in checks.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"    {status} {check}")

    if all(checks.values()):
        print("\n[SUCCESS] All checks passed!")
    else:
        print("\n[ERROR] Some checks failed!")
        print(f"\nActual code:\n{code}")