"""
MACD 지표 정의 수정 스크립트
macd_line -> macd 로 변경
"""

from supabase import create_client
import os
from dotenv import load_dotenv
import json

load_dotenv('../.env')

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, key)

# 새 코드 (macd_line -> macd)
new_code = """exp1 = df["close"].ewm(span=params.get("fast", 12), adjust=False).mean()
exp2 = df["close"].ewm(span=params.get("slow", 26), adjust=False).mean()
macd = exp1 - exp2
macd_signal = macd.ewm(span=params.get("signal", 9), adjust=False).mean()
macd_hist = macd - macd_signal
result = {"macd": macd, "macd_signal": macd_signal, "macd_hist": macd_hist}"""

print("Updating MACD indicator...")
print(f"New code:\n{new_code}\n")

# 업데이트
response = supabase.table('indicators').update({
    'formula': {'code': new_code},  # dict로 직접 전달
    'output_columns': ['macd', 'macd_signal', 'macd_hist']
}).eq('name', 'macd').execute()

print(f"[OK] Updated {len(response.data)} record(s)")

# 검증
verify = supabase.table('indicators').select('*').eq('name', 'macd').execute()

if verify.data:
    indicator = verify.data[0]
    print("\n[OK] Verification:")
    print(f"  Name: {indicator['name']}")
    print(f"  Output Columns: {indicator['output_columns']}")

    formula = indicator['formula']
    if isinstance(formula, str):
        formula = json.loads(formula)

    code = formula.get('code', '')

    # 체크
    checks = {
        'Uses "macd" (not "macd_line")': '"macd":' in code,
        'Uses "macd_signal"': '"macd_signal":' in code,
        'Uses "macd_hist"': '"macd_hist":' in code,
        'Sets result variable': 'result =' in code,
        'No old "macd_line"': 'macd_line' not in code
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