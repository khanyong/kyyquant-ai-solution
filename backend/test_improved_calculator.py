"""
개선된 계산기 테스트
- 캐시 키 종목 구분 확인
- DB 전용 모드 기본값 확인
- 레지스트리 None 가드 확인
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_improvements():
    """개선사항 테스트"""

    print("=" * 60)
    print("TEST 1: Default Mode Check (should be DB-only)")
    print("=" * 60)

    # 환경변수 제거하여 기본값 확인
    if 'ENFORCE_DB_INDICATORS' in os.environ:
        del os.environ['ENFORCE_DB_INDICATORS']

    from indicators.calculator import IndicatorCalculator
    calc = IndicatorCalculator()

    print(f"Default enforce_db_only: {calc.enforce_db_only}")
    assert calc.enforce_db_only == True, "Default should be DB-only mode"
    print("[PASS] Default mode is DB-only (safe for production)")

    print("\n" + "=" * 60)
    print("TEST 2: Cache Key with Stock Code")
    print("=" * 60)

    # 개발 모드로 전환
    os.environ['ENFORCE_DB_INDICATORS'] = 'false'

    import importlib
    import indicators.calculator
    importlib.reload(indicators.calculator)

    calc_dev = indicators.calculator.IndicatorCalculator()

    # 테스트용 데이터
    dates = pd.date_range('2024-01-01', periods=10)
    df = pd.DataFrame({
        'close': np.random.randn(10) + 100
    }, index=dates)

    from indicators.calculator import ExecOptions
    options = ExecOptions(period=5)

    # 캐시 키 테스트 - 종목코드 없이
    key1 = calc_dev._get_cache_key('test', options)
    print(f"Key without stock_code: {key1}")

    # 캐시 키 테스트 - 종목코드 포함
    key2 = calc_dev._get_cache_key('test', options, stock_code='005930')
    print(f"Key with stock_code: {key2}")

    # 캐시 키 테스트 - 종목코드와 인덱스 포함
    key3 = calc_dev._get_cache_key('test', options, stock_code='005930', df_index=df.index)
    print(f"Key with stock_code and index: {key3}")

    # 키가 모두 다른지 확인
    assert key1 != key2, "Keys should differ with stock_code"
    assert key2 != key3, "Keys should differ with index"
    print("[PASS] Cache keys properly differentiated")

    print("\n" + "=" * 60)
    print("TEST 3: Registry None Guard in DB-only Mode")
    print("=" * 60)

    # DB 전용 모드로 전환
    os.environ['ENFORCE_DB_INDICATORS'] = 'true'
    importlib.reload(indicators.calculator)

    calc_prod = indicators.calculator.IndicatorCalculator()

    # 가짜 DB 정의 (method만 있고 code가 없음)
    fake_definition = {
        'name': 'test_indicator',
        'calculation_type': 'built-in',
        'formula': '{"method": "sma"}'  # code가 없음
    }

    # registry가 None일 때 에러 발생 확인
    try:
        result = calc_prod._calculate_from_definition(df, fake_definition, options)
        print("[FAIL] Should have raised error for missing code in DB-only mode")
    except ValueError as e:
        if "requires 'code' in formula" in str(e) and "DB-only mode" in str(e):
            print(f"[PASS] Properly blocked: {e}")
        else:
            print(f"[FAIL] Wrong error: {e}")

    print("\n" + "=" * 60)
    print("All Tests Completed")
    print("=" * 60)

    # 환경변수 복원
    os.environ['ENFORCE_DB_INDICATORS'] = 'false'

if __name__ == "__main__":
    test_improvements()