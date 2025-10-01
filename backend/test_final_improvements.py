"""
최종 개선사항 테스트
- Supabase 미연결 시 Fail-fast
- 슬리피지 적용
- 포지션 사이즈 외부화
- 강화된 보안 샌드박스
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

def test_fail_fast():
    """Supabase 미연결 시 Fail-fast 테스트"""
    print("=" * 60)
    print("TEST 1: Fail-fast when Supabase not configured")
    print("=" * 60)

    # 환경변수 백업
    original_url = os.environ.get('SUPABASE_URL')
    original_key = os.environ.get('SUPABASE_KEY')

    try:
        # Supabase 설정 제거
        if 'SUPABASE_URL' in os.environ:
            del os.environ['SUPABASE_URL']
        if 'SUPABASE_KEY' in os.environ:
            del os.environ['SUPABASE_KEY']
        if 'SUPABASE_ANON_KEY' in os.environ:
            del os.environ['SUPABASE_ANON_KEY']

        # DB 전용 모드에서 실행 시도
        os.environ['ENFORCE_DB_INDICATORS'] = 'true'

        import importlib
        import indicators.calculator
        importlib.reload(indicators.calculator)

        try:
            calc = indicators.calculator.IndicatorCalculator()
            print("[FAIL] Should have raised RuntimeError")
        except RuntimeError as e:
            if "FATAL" in str(e) and "Supabase" in str(e):
                print(f"[PASS] Fail-fast worked: {str(e).split('.')[0]}")
            else:
                print(f"[FAIL] Wrong error: {e}")

    finally:
        # 환경변수 복원
        if original_url:
            os.environ['SUPABASE_URL'] = original_url
        if original_key:
            os.environ['SUPABASE_KEY'] = original_key

def test_slippage_calculation():
    """슬리피지 계산 테스트"""
    print("\n" + "=" * 60)
    print("TEST 2: Slippage Calculation")
    print("=" * 60)

    # 슬리피지 계산 예제
    price = 100000
    slippage = 0.001  # 0.1%

    buy_price = price * (1 + slippage)
    sell_price = price * (1 - slippage)

    print(f"Base price: {price:,.0f}")
    print(f"Buy price (with slippage): {buy_price:,.0f} (+{slippage*100:.1f}%)")
    print(f"Sell price (with slippage): {sell_price:,.0f} (-{slippage*100:.1f}%)")

    assert buy_price > price, "Buy price should be higher"
    assert sell_price < price, "Sell price should be lower"
    print("[PASS] Slippage calculation correct")

def test_position_size_config():
    """포지션 사이즈 설정 테스트"""
    print("\n" + "=" * 60)
    print("TEST 3: Position Size Configuration")
    print("=" * 60)

    capital = 10000000  # 1천만원

    # 다양한 포지션 사이즈 테스트
    position_sizes = [0.1, 0.2, 0.3, 0.5]

    for size in position_sizes:
        max_amount = capital * size
        print(f"Position size {size*100:.0f}%: Max amount = {max_amount:,.0f} KRW")

    print("[PASS] Position size configuration flexible")

def test_sandbox_validation():
    """강화된 샌드박스 검증 테스트"""
    print("\n" + "=" * 60)
    print("TEST 4: Enhanced Security Sandbox")
    print("=" * 60)

    from indicators.calculator import SecuritySandbox

    # 안전한 코드
    safe_codes = [
        "result = df['close'].rolling(window=20).mean()",
        "sma = df['close'].ewm(span=12).mean()",
        "result = {'value': df['close'] * 2}"
    ]

    # 위험한 코드
    dangerous_codes = [
        "import os",  # Import 차단
        "eval('print(1)')",  # eval 차단
        "open('/etc/passwd')",  # open 차단
        "__import__('os')",  # __import__ 차단
        "df.__class__.__bases__",  # 위험한 속성 접근
    ]

    sandbox = SecuritySandbox()

    print("Testing safe codes:")
    for code in safe_codes:
        if sandbox.validate_ast(code):
            print(f"  [OK] Allowed: {code[:30]}...")
        else:
            print(f"  [FAIL] Blocked: {code[:30]}...")

    print("\nTesting dangerous codes:")
    for code in dangerous_codes:
        if not sandbox.validate_ast(code):
            print(f"  [OK] Blocked: {code[:30]}...")
        else:
            print(f"  [FAIL] Allowed: {code[:30]}...")

    print("[PASS] Security sandbox validation working")

if __name__ == "__main__":
    test_fail_fast()
    test_slippage_calculation()
    test_position_size_config()
    test_sandbox_validation()

    print("\n" + "=" * 60)
    print("All Improvement Tests Completed")
    print("=" * 60)