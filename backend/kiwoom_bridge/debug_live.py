"""
실시간 디버깅 - 실제 백테스트 API 호출 추적
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import sys
import os

# 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_actual_strategy():
    """실제 저장된 전략 형식 테스트"""

    print("="*60)
    print("실제 전략 형식 디버깅")
    print("="*60)

    # 실제로 프론트엔드에서 전송되는 형식
    actual_strategy = {
        "config": {
            "indicators": [
                {"type": "ma", "period": 20},  # ← params 구조가 없음!
                {"type": "ma", "period": 60}
            ],
            "buyConditions": [
                {"indicator": "MA_20", "operator": "CROSS_ABOVE", "value": "MA_60"}  # ← 대문자!
            ],
            "sellConditions": [
                {"indicator": "MA_20", "operator": "CROSS_BELOW", "value": "MA_60"}
            ]
        }
    }

    print("실제 전략 config:")
    print(json.dumps(actual_strategy['config'], indent=2, ensure_ascii=False))

    # backtest_api.py의 Strategy 클래스 테스트
    try:
        from backtest_api import Strategy, USE_CORE

        print(f"\nCore 모듈 사용 가능: {USE_CORE}")

        if not USE_CORE:
            print("❌ Core 모듈이 로드되지 않음!")
            print("   core/ 폴더가 없거나 import 오류")
            return False

        # 테스트 데이터
        dates = pd.date_range('2024-01-01', periods=100)
        prices = []
        base = 50000

        for i in range(100):
            if i < 30:
                base = base * 0.98
            elif i < 70:
                base = base * 1.02
            else:
                base = base * 0.99
            prices.append(base)

        df = pd.DataFrame({
            'date': dates,
            'open': prices,
            'high': [p * 1.01 for p in prices],
            'low': [p * 0.99 for p in prices],
            'close': prices,
            'volume': [1000000] * 100
        })

        # execute_strategy 호출
        import asyncio
        result = asyncio.run(Strategy.execute_strategy(df, actual_strategy['config']))

        # 결과 확인
        if 'signal' in result.columns:
            buy_count = (result['signal'] == 1).sum()
            sell_count = (result['signal'] == -1).sum()
            print(f"\n✅ 신호 생성: 매수 {buy_count}개, 매도 {sell_count}개")

            if buy_count == 0 and sell_count == 0:
                print("\n❌ 신호가 생성되지 않음!")
                print("\n가능한 원인:")
                print("1. 지표명 불일치: MA_20 vs ma_20")
                print("2. operator 대소문자: CROSS_ABOVE vs cross_above")
                print("3. params 구조 없음")

                # 컬럼 확인
                indicator_cols = [col for col in result.columns
                                if col not in ['date', 'open', 'high', 'low', 'close', 'volume', 'price', 'signal', 'buy_signal', 'sell_signal']]
                print(f"\n생성된 지표 컬럼: {indicator_cols}")

                # 실제 값 확인
                if 'ma_20' in result.columns and 'ma_60' in result.columns:
                    print("\n이동평균 값 (처음 5개):")
                    print(result[['close', 'ma_20', 'ma_60']].head())
                else:
                    print("\n❌ ma_20, ma_60 컬럼이 생성되지 않음!")

        else:
            print("❌ signal 컬럼이 없음!")

    except ImportError as e:
        print(f"❌ Import 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def check_normalize_function():
    """정규화 함수 테스트"""
    print("\n" + "="*60)
    print("정규화 함수 테스트")
    print("="*60)

    try:
        from core import _normalize_conditions

        # 대문자 조건
        conditions = [
            {"indicator": "MA_20", "operator": "CROSS_ABOVE", "value": "MA_60"}
        ]

        normalized = _normalize_conditions(conditions)
        print(f"원본: {conditions}")
        print(f"정규화: {normalized}")

        if normalized[0]['indicator'] == 'ma_20':
            print("✅ 지표명 정규화 성공")
        else:
            print("❌ 지표명 정규화 실패")

        if normalized[0]['operator'] == 'cross_above':
            print("✅ 연산자 정규화 성공")
        else:
            print("❌ 연산자 정규화 실패")

    except ImportError:
        print("❌ Core 모듈을 찾을 수 없음")
    except Exception as e:
        print(f"❌ 오류: {e}")


def test_manual_fix():
    """수동으로 수정한 전략 테스트"""
    print("\n" + "="*60)
    print("수동 수정 전략 테스트")
    print("="*60)

    # 올바른 형식
    correct_strategy = {
        "config": {
            "indicators": [
                {"type": "ma", "params": {"period": 20}},  # params 추가
                {"type": "ma", "params": {"period": 60}}
            ],
            "buyConditions": [
                {"indicator": "ma_20", "operator": "cross_above", "value": "ma_60"}  # 소문자
            ],
            "sellConditions": [
                {"indicator": "ma_20", "operator": "cross_below", "value": "ma_60"}
            ]
        }
    }

    print("수정된 전략:")
    print(json.dumps(correct_strategy['config'], indent=2, ensure_ascii=False))

    # 테스트 (위와 동일한 코드)
    # ...


if __name__ == "__main__":
    # 1. 실제 전략 테스트
    print("STEP 1: 실제 전략 형식 테스트")
    test_actual_strategy()

    # 2. 정규화 함수 테스트
    print("\nSTEP 2: 정규화 함수 테스트")
    check_normalize_function()

    print("\n" + "="*60)
    print("디버깅 완료")
    print("="*60)
    print("\n문제 해결 방법:")
    print("1. Supabase에 저장된 전략의 형식을 확인")
    print("2. 프론트엔드에서 전송하는 형식을 확인")
    print("3. 백엔드 _normalize_conditions 함수가 제대로 작동하는지 확인")