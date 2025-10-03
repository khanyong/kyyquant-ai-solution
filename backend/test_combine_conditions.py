"""
combineWith 필드 지원 테스트
"""
import os
import sys
import io
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

import pandas as pd
import numpy as np
from backtest.engine import BacktestEngine

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_and_conditions():
    """AND 조건 테스트"""
    print("=" * 80)
    print("TEST 1: AND 조건")
    print("=" * 80)

    engine = BacktestEngine()

    # 테스트 데이터 생성
    row = pd.Series({
        'rsi': 25,
        'macd_line': 0.5,
        'macd_signal': 0.3
    })

    # 테스트 조건: RSI < 30 AND MACD > Signal
    conditions = [
        {'left': 'rsi', 'operator': '<', 'right': 30},
        {'left': 'macd_line', 'operator': '>', 'right': 'macd_signal', 'combineWith': 'AND'}
    ]

    result, reasons = engine._evaluate_conditions_with_combine(row, conditions)

    print(f"조건:")
    print(f"  [0] RSI < 30")
    print(f"  [1] MACD > Signal (combineWith: AND)")
    print(f"\n데이터:")
    print(f"  RSI: {row['rsi']}")
    print(f"  MACD Line: {row['macd_line']}")
    print(f"  MACD Signal: {row['macd_signal']}")
    print(f"\n결과: {result}")
    print(f"이유: {reasons}")
    print(f"\n예상: True (25 < 30 AND 0.5 > 0.3)")
    print(f"✅ 통과" if result else "❌ 실패")
    print()

    return result == True


def test_or_conditions():
    """OR 조건 테스트"""
    print("=" * 80)
    print("TEST 2: OR 조건")
    print("=" * 80)

    engine = BacktestEngine()

    # 테스트 데이터: RSI는 중간값
    row = pd.Series({
        'rsi': 50,
    })

    # 테스트 조건: RSI < 30 OR RSI > 70
    conditions = [
        {'left': 'rsi', 'operator': '<', 'right': 30},
        {'left': 'rsi', 'operator': '>', 'right': 70, 'combineWith': 'OR'}
    ]

    result, reasons = engine._evaluate_conditions_with_combine(row, conditions)

    print(f"조건:")
    print(f"  [0] RSI < 30")
    print(f"  [1] RSI > 70 (combineWith: OR)")
    print(f"\n데이터:")
    print(f"  RSI: {row['rsi']}")
    print(f"\n결과: {result}")
    print(f"이유: {reasons}")
    print(f"\n예상: False (50은 30보다 크고 70보다 작음)")
    print(f"✅ 통과" if result == False else "❌ 실패")
    print()

    # 테스트 2: RSI가 과매도 구간
    row2 = pd.Series({'rsi': 25})
    result2, reasons2 = engine._evaluate_conditions_with_combine(row2, conditions)

    print(f"데이터 2:")
    print(f"  RSI: {row2['rsi']}")
    print(f"\n결과: {result2}")
    print(f"이유: {reasons2}")
    print(f"\n예상: True (25 < 30)")
    print(f"✅ 통과" if result2 == True else "❌ 실패")
    print()

    # 테스트 3: RSI가 과매수 구간
    row3 = pd.Series({'rsi': 75})
    result3, reasons3 = engine._evaluate_conditions_with_combine(row3, conditions)

    print(f"데이터 3:")
    print(f"  RSI: {row3['rsi']}")
    print(f"\n결과: {result3}")
    print(f"이유: {reasons3}")
    print(f"\n예상: True (75 > 70)")
    print(f"✅ 통과" if result3 == True else "❌ 실패")
    print()

    return result == False and result2 == True and result3 == True


def test_mixed_conditions():
    """혼합 조건 테스트"""
    print("=" * 80)
    print("TEST 3: 혼합 조건 (AND + OR)")
    print("=" * 80)

    engine = BacktestEngine()

    # 테스트 데이터
    row = pd.Series({
        'rsi': 35,
        'macd_line': 0.5,
        'volume': 1500000,
        'volume_ma_20': 1000000
    })

    # 조건: (RSI < 40 AND MACD > 0) OR Volume > VMA
    # 순차 평가: RSI < 40 = True, MACD > 0 = True -> (True AND True) = True
    # Volume > VMA는 평가되지만 이미 True이므로 True 유지
    conditions = [
        {'left': 'rsi', 'operator': '<', 'right': 40},
        {'left': 'macd_line', 'operator': '>', 'right': 0, 'combineWith': 'AND'},
        {'left': 'volume', 'operator': '>', 'right': 'volume_ma_20', 'combineWith': 'OR'}
    ]

    result, reasons = engine._evaluate_conditions_with_combine(row, conditions)

    print(f"조건:")
    print(f"  [0] RSI < 40")
    print(f"  [1] MACD > 0 (combineWith: AND)")
    print(f"  [2] Volume > VMA (combineWith: OR)")
    print(f"\n데이터:")
    print(f"  RSI: {row['rsi']}")
    print(f"  MACD Line: {row['macd_line']}")
    print(f"  Volume: {row['volume']}")
    print(f"  Volume MA: {row['volume_ma_20']}")
    print(f"\n결과: {result}")
    print(f"이유: {reasons}")
    print(f"\n예상: True")
    print(f"  - (35 < 40) = True")
    print(f"  - (0.5 > 0) = True")
    print(f"  - True AND True = True")
    print(f"  - (1500000 > 1000000) = True")
    print(f"  - True OR True = True")
    print(f"✅ 통과" if result == True else "❌ 실패")
    print()

    # 테스트 2: 첫 두 조건은 거짓, 마지막만 참
    row2 = pd.Series({
        'rsi': 45,  # > 40
        'macd_line': -0.5,  # < 0
        'volume': 1500000,
        'volume_ma_20': 1000000
    })

    result2, reasons2 = engine._evaluate_conditions_with_combine(row2, conditions)

    print(f"데이터 2:")
    print(f"  RSI: {row2['rsi']}")
    print(f"  MACD Line: {row2['macd_line']}")
    print(f"  Volume: {row2['volume']}")
    print(f"\n결과: {result2}")
    print(f"이유: {reasons2}")
    print(f"\n예상: True (Volume 조건만으로)")
    print(f"  - (45 < 40) = False")
    print(f"  - False AND anything = False")
    print(f"  - (1500000 > 1000000) = True")
    print(f"  - False OR True = True")
    print(f"✅ 통과" if result2 == True else "❌ 실패")
    print()

    return result == True and result2 == True


def test_legacy_compatibility():
    """기존 형식 호환성 테스트"""
    print("=" * 80)
    print("TEST 4: 기존 형식 호환성")
    print("=" * 80)

    engine = BacktestEngine()

    row = pd.Series({
        'rsi': 25,
        'macd_line': 0.5
    })

    # 기존 형식 (combineWith 없음 = 기본 AND)
    conditions = [
        {'indicator': 'rsi', 'operator': '<', 'value': 30},
        {'indicator': 'macd_line', 'operator': '>', 'value': 0}
    ]

    result, reasons = engine._evaluate_conditions_with_combine(row, conditions)

    print(f"조건 (기존 형식):")
    print(f"  [0] indicator: rsi, operator: <, value: 30")
    print(f"  [1] indicator: macd_line, operator: >, value: 0")
    print(f"\n데이터:")
    print(f"  RSI: {row['rsi']}")
    print(f"  MACD Line: {row['macd_line']}")
    print(f"\n결과: {result}")
    print(f"이유: {reasons}")
    print(f"\n예상: True (기본 AND 동작)")
    print(f"✅ 통과" if result == True else "❌ 실패")
    print()

    return result == True


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print(" " * 20 + "combineWith 필드 지원 테스트")
    print("=" * 80)
    print()

    results = []

    results.append(("AND 조건", test_and_conditions()))
    results.append(("OR 조건", test_or_conditions()))
    results.append(("혼합 조건", test_mixed_conditions()))
    results.append(("기존 형식 호환성", test_legacy_compatibility()))

    print("=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{name:20} : {status}")

    all_passed = all(r[1] for r in results)
    print()
    if all_passed:
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️  일부 테스트 실패")
    print()
