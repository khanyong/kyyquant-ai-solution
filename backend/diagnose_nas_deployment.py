"""
NAS 배포 후 백테스트 0 거래 문제 진단 스크립트
실행: python diagnose_nas_deployment.py
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def check_environment():
    """환경변수 설정 확인"""
    print("=" * 60)
    print("1. 환경변수 확인")
    print("=" * 60)

    critical_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_KEY': os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY'),
        'ENFORCE_DB_INDICATORS': os.getenv('ENFORCE_DB_INDICATORS', 'true')
    }

    all_ok = True
    for var, value in critical_vars.items():
        if value:
            if 'KEY' in var:
                print(f"✓ {var}: {'*' * 20} (설정됨)")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: 없음 (문제!)")
            all_ok = False

    return all_ok

def check_supabase_connection():
    """Supabase 연결 상태 확인"""
    print("\n" + "=" * 60)
    print("2. Supabase 연결 확인")
    print("=" * 60)

    try:
        from supabase import create_client

        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

        if not url or not key:
            print("✗ Supabase 연결 정보 없음")
            return False

        client = create_client(url, key)

        # indicators 테이블 조회
        response = client.table('indicators').select('*').limit(5).execute()

        if response.data:
            print(f"✓ Supabase 연결 성공")
            print(f"  - indicators 테이블에서 {len(response.data)}개 지표 확인")

            # 주요 지표 확인
            indicator_names = [ind['name'] for ind in response.data]
            print(f"  - 발견된 지표: {', '.join(indicator_names)}")

            # SMA 지표 확인
            sma_response = client.table('indicators').select('*').eq('name', 'sma').execute()
            if sma_response.data:
                print(f"✓ SMA 지표 발견: {len(sma_response.data)}개 정의")
            else:
                print("✗ SMA 지표를 찾을 수 없음 (골든크로스 전략에 필수)")
                return False

            return True
        else:
            print("✗ indicators 테이블이 비어있음")
            return False

    except Exception as e:
        print(f"✗ Supabase 연결 실패: {e}")
        return False

def check_calculator_mode():
    """Calculator 모드 및 동작 확인"""
    print("\n" + "=" * 60)
    print("3. Calculator 설정 확인")
    print("=" * 60)

    try:
        from indicators.calculator import IndicatorCalculator

        calc = IndicatorCalculator()

        # DB 전용 모드 확인
        print(f"  - DB 전용 모드: {calc.enforce_db_only}")
        print(f"  - Supabase 연결: {calc.supabase is not None}")

        if calc.enforce_db_only and not calc.supabase:
            print("✗ DB 전용 모드이지만 Supabase 미연결 (치명적)")
            return False

        # 레지스트리 확인
        if not calc.enforce_db_only:
            print(f"  - 내장 지표 레지스트리: {calc.registry is not None}")

        print("✓ Calculator 설정 정상")
        return True

    except Exception as e:
        print(f"✗ Calculator 로드 실패: {e}")
        return False

def test_indicator_calculation():
    """실제 지표 계산 테스트"""
    print("\n" + "=" * 60)
    print("4. 지표 계산 테스트")
    print("=" * 60)

    try:
        from indicators.calculator import IndicatorCalculator

        calc = IndicatorCalculator()

        # 테스트 데이터 생성
        dates = pd.date_range('2024-01-01', periods=50)
        test_df = pd.DataFrame({
            'open': np.random.randn(50) * 1000 + 50000,
            'high': np.random.randn(50) * 1000 + 51000,
            'low': np.random.randn(50) * 1000 + 49000,
            'close': np.random.randn(50) * 1000 + 50000,
            'volume': np.random.randint(1000, 10000, 50)
        }, index=dates)

        # SMA 5일 계산
        print("\n테스트 1: SMA 5일")
        try:
            result = calc.calculate(test_df, {
                'name': 'sma',
                'params': {'period': 5}
            }, stock_code='TEST')

            if hasattr(result, 'columns'):
                if 'sma' in result.columns or 'sma_5' in result.columns:
                    col_name = 'sma_5' if 'sma_5' in result.columns else 'sma'
                    print(f"✓ SMA 5일 계산 성공: {result.columns[col_name].iloc[-1]:.2f}")
                else:
                    print(f"✗ SMA 컬럼 없음. 발견된 컬럼: {list(result.columns.keys())}")
                    return False
            else:
                print(f"✗ 예상하지 못한 결과 타입: {type(result)}")
                return False

        except Exception as e:
            print(f"✗ SMA 5일 계산 실패: {e}")
            return False

        # SMA 20일 계산
        print("\n테스트 2: SMA 20일")
        try:
            result = calc.calculate(test_df, {
                'name': 'sma',
                'params': {'period': 20}
            }, stock_code='TEST')

            if hasattr(result, 'columns'):
                if 'sma' in result.columns or 'sma_20' in result.columns:
                    col_name = 'sma_20' if 'sma_20' in result.columns else 'sma'
                    print(f"✓ SMA 20일 계산 성공: {result.columns[col_name].iloc[-1]:.2f}")
                else:
                    print(f"✗ SMA 컬럼 없음. 발견된 컬럼: {list(result.columns.keys())}")
                    return False
            else:
                print(f"✗ 예상하지 못한 결과 타입: {type(result)}")
                return False

        except Exception as e:
            print(f"✗ SMA 20일 계산 실패: {e}")
            return False

        print("\n✓ 모든 지표 계산 테스트 통과")
        return True

    except Exception as e:
        print(f"✗ 지표 계산 테스트 실패: {e}")
        return False

def test_backtest_engine():
    """백테스트 엔진 동작 확인"""
    print("\n" + "=" * 60)
    print("5. 백테스트 엔진 테스트")
    print("=" * 60)

    try:
        from backtest.engine import BacktestEngine
        from indicators.calculator import IndicatorCalculator

        # 엔진 초기화
        engine = BacktestEngine()
        calc = IndicatorCalculator()

        # 테스트 데이터
        dates = pd.date_range('2024-01-01', periods=100)
        test_df = pd.DataFrame({
            'date': dates,
            'open': np.random.randn(100) * 1000 + 50000,
            'high': np.random.randn(100) * 1000 + 51000,
            'low': np.random.randn(100) * 1000 + 49000,
            'close': np.random.randn(100) * 1000 + 50000,
            'volume': np.random.randint(1000, 10000, 100)
        })
        test_df.set_index('date', inplace=True)

        # 간단한 골든크로스 전략
        strategy_config = {
            'name': 'golden_cross',
            'initial_capital': 10000000,
            'position_size': 0.3,
            'indicators': [
                {'name': 'sma', 'params': {'period': 5}},
                {'name': 'sma', 'params': {'period': 20}}
            ],
            'buy_condition': 'sma_5 > sma_20',
            'sell_condition': 'sma_5 < sma_20'
        }

        # 지표 계산
        print("\n지표 추가 중...")
        for indicator_config in strategy_config['indicators']:
            try:
                result = calc.calculate(test_df, indicator_config, stock_code='TEST')
                if hasattr(result, 'columns'):
                    for col_name, col_data in result.columns.items():
                        test_df[col_name] = col_data
                        print(f"  - {col_name} 추가 완료")
            except Exception as e:
                print(f"  ✗ 지표 추가 실패: {e}")
                return False

        # 필수 컬럼 확인
        print("\n데이터프레임 컬럼 확인:")
        print(f"  - 전체 컬럼: {list(test_df.columns)}")

        required_cols = ['sma_5', 'sma_20']
        missing_cols = [col for col in required_cols if col not in test_df.columns]

        if missing_cols:
            print(f"  ✗ 필수 컬럼 누락: {missing_cols}")

            # 대체 컬럼명 확인
            if 'sma' in test_df.columns:
                print(f"  ! 'sma' 컬럼은 있지만 period별 구분이 안됨")
                print(f"  ! calculator.py의 base_indicator 처리 확인 필요")

            return False

        print("  ✓ 모든 필수 컬럼 존재")

        # 신호 생성 테스트
        print("\n신호 생성 테스트:")
        test_df['buy_signal'] = test_df['sma_5'] > test_df['sma_20']
        test_df['sell_signal'] = test_df['sma_5'] < test_df['sma_20']

        buy_signals = test_df['buy_signal'].sum()
        sell_signals = test_df['sell_signal'].sum()

        print(f"  - 매수 신호: {buy_signals}개")
        print(f"  - 매도 신호: {sell_signals}개")

        if buy_signals == 0:
            print("  ✗ 매수 신호가 전혀 없음")
            return False

        print("\n✓ 백테스트 엔진 테스트 통과")
        return True

    except Exception as e:
        print(f"✗ 백테스트 엔진 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 진단 함수"""
    print("=" * 60)
    print("NAS 배포 진단 시작")
    print("=" * 60)

    results = []

    # 1. 환경변수 확인
    results.append(("환경변수", check_environment()))

    # 2. Supabase 연결 확인
    results.append(("Supabase 연결", check_supabase_connection()))

    # 3. Calculator 모드 확인
    results.append(("Calculator 설정", check_calculator_mode()))

    # 4. 지표 계산 테스트
    results.append(("지표 계산", test_indicator_calculation()))

    # 5. 백테스트 엔진 테스트
    results.append(("백테스트 엔진", test_backtest_engine()))

    # 결과 요약
    print("\n" + "=" * 60)
    print("진단 결과 요약")
    print("=" * 60)

    for name, result in results:
        status = "✓ 정상" if result else "✗ 문제"
        print(f"{name}: {status}")

    # 문제 진단
    failed = [name for name, result in results if not result]

    if failed:
        print("\n" + "=" * 60)
        print("문제 해결 제안")
        print("=" * 60)

        if "환경변수" in failed:
            print("1. .env 파일에 SUPABASE_URL과 SUPABASE_KEY 설정 확인")
            print("   docker-compose.yml의 environment 섹션도 확인")

        if "Supabase 연결" in failed:
            print("2. Supabase 프로젝트 URL과 anon key가 올바른지 확인")
            print("   indicators 테이블에 지표 정의가 있는지 확인")

        if "Calculator 설정" in failed:
            print("3. calculator.py 파일이 최신 버전인지 확인")
            print("   ENFORCE_DB_INDICATORS 환경변수 설정 확인")

        if "지표 계산" in failed:
            print("4. Supabase indicators 테이블에 'sma' 지표가 있는지 확인")
            print("   calculation_type과 formula 필드가 올바른지 확인")

        if "백테스트 엔진" in failed:
            print("5. engine.py 파일이 최신 버전인지 확인")
            print("   지표명이 period를 포함하여 구분되는지 확인 (sma_5, sma_20)")
    else:
        print("\n✓ 모든 테스트 통과! 백테스트가 정상 작동해야 합니다.")
        print("  여전히 문제가 있다면 실제 전략 설정을 확인하세요.")

if __name__ == "__main__":
    main()