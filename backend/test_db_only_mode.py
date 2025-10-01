"""
DB 전용 모드 테스트 - ENFORCE_DB_INDICATORS 플래그 동작 확인
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 환경변수 설정
from dotenv import load_dotenv
load_dotenv()

def test_db_only_mode():
    """DB 전용 모드 테스트"""

    # 테스트용 데이터 생성
    dates = pd.date_range('2024-01-01', periods=100)
    df = pd.DataFrame({
        'open': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'high': 102 + np.cumsum(np.random.randn(100) * 0.5),
        'low': 98 + np.cumsum(np.random.randn(100) * 0.5),
        'close': 100 + np.cumsum(np.random.randn(100) * 0.5),
        'volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)

    print("=" * 60)
    print("테스트 1: DB 전용 모드 OFF (개발 모드)")
    print("=" * 60)

    # DB 전용 모드 OFF
    os.environ['ENFORCE_DB_INDICATORS'] = 'false'

    from indicators.calculator import IndicatorCalculator
    calc_dev = IndicatorCalculator()

    print(f"enforce_db_only: {calc_dev.enforce_db_only}")
    print(f"registry available: {calc_dev.registry is not None}")

    # 내장 지표 테스트
    try:
        result = calc_dev.calculate(df, {
            'name': 'sma_test',
            'calculation_type': 'builtin',
            'base_indicator': 'sma',
            'params': {'period': 10}
        })
        print("[OK] 내장 지표 사용 가능")
    except Exception as e:
        print(f"[FAIL] 내장 지표 실패: {e}")

    # 커스텀 수식 테스트
    try:
        result = calc_dev.calculate(df, {
            'name': 'custom_test',
            'calculation_type': 'custom_formula',
            'formula': 'df["close"].rolling(window=10).mean()'
        })
        print("[OK] 커스텀 수식 사용 가능")
    except Exception as e:
        print(f"[FAIL] 커스텀 수식 실패: {e}")

    print("\n" + "=" * 60)
    print("테스트 2: DB 전용 모드 ON (운영 모드)")
    print("=" * 60)

    # DB 전용 모드 ON
    os.environ['ENFORCE_DB_INDICATORS'] = 'true'

    # 새 인스턴스 생성 (환경변수 반영)
    import importlib
    import indicators.calculator
    importlib.reload(indicators.calculator)

    calc_prod = indicators.calculator.IndicatorCalculator()

    print(f"enforce_db_only: {calc_prod.enforce_db_only}")
    print(f"registry available: {calc_prod.registry is not None}")

    # Supabase에 있는 지표 테스트 (sma)
    try:
        result = calc_prod.calculate(df, {
            'name': 'sma',
            'params': {'period': 20}
        })
        print("[OK] Supabase 지표 사용 가능")
    except Exception as e:
        print(f"[FAIL] Supabase 지표 실패: {e}")

    # 내장 지표 테스트 (차단되어야 함)
    try:
        result = calc_prod.calculate(df, {
            'name': 'builtin_blocked_test',
            'calculation_type': 'builtin',
            'base_indicator': 'sma'
        })
        print("[ERROR] 내장 지표가 차단되지 않음 (오류)")
    except ValueError as e:
        if "ENFORCE_DB_INDICATORS" in str(e):
            print(f"[OK] 내장 지표 차단됨: {e}")
        else:
            print(f"[FAIL] 예상치 못한 에러: {e}")
    except Exception as e:
        print(f"✗ 예상치 못한 에러: {e}")

    # 커스텀 수식 테스트 (차단되어야 함)
    try:
        result = calc_prod.calculate(df, {
            'name': 'custom_blocked_test',
            'calculation_type': 'custom_formula',
            'formula': 'df["close"].rolling(window=10).mean()'
        })
        print("[ERROR] 커스텀 수식이 차단되지 않음 (오류)")
    except ValueError as e:
        if "database" in str(e).lower() or "supabase" in str(e).lower():
            print(f"[OK] 커스텀 수식 차단됨: {e}")
        else:
            print(f"[FAIL] 예상치 못한 에러: {e}")
    except Exception as e:
        print(f"✗ 예상치 못한 에러: {e}")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

    # 환경변수 복원
    os.environ['ENFORCE_DB_INDICATORS'] = 'false'

if __name__ == "__main__":
    test_db_only_mode()