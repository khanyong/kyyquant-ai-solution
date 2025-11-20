#!/usr/bin/env python3
"""
모든 활성화된 지표를 검증하는 스크립트
- AST 보안 검증 통과 여부
- 컬럼명 일치 여부 (code의 result dict vs output_columns)
- 실제 계산 가능 여부
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# 환경 변수 로드
from dotenv import load_dotenv
env_path = os.path.join(backend_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

from supabase import create_client, Client
import pandas as pd
import numpy as np
import json
import re

def get_supabase_client() -> Client:
    """Supabase 클라이언트 생성"""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment")
    return create_client(url, key)

def extract_result_keys_from_code(code: str):
    """Python 코드에서 result dict의 키 추출"""
    # result = {"key1": val1, "key2": val2} 패턴 찾기
    pattern = r'result\s*=\s*\{([^}]+)\}'
    match = re.search(pattern, code)
    if match:
        dict_content = match.group(1)
        # "key": value 패턴에서 key만 추출
        keys = re.findall(r'["\'](\w+)["\']', dict_content)
        return keys
    return []

def create_test_dataframe():
    """테스트용 DataFrame 생성"""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    close = 100 + np.cumsum(np.random.randn(100) * 2)
    high = close + np.abs(np.random.randn(100) * 1)
    low = close - np.abs(np.random.randn(100) * 1)
    open_price = close + np.random.randn(100) * 0.5
    volume = np.random.randint(1000000, 10000000, 100)

    return pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)

def validate_indicator(indicator_def, calculator, test_df):
    """개별 지표 검증"""
    name = indicator_def['name']
    calc_type = indicator_def['calculation_type']
    output_columns = indicator_def['output_columns'] or []

    issues = []

    print(f"\n{'='*60}")
    print(f"지표: {name} ({calc_type})")
    print(f"출력 컬럼: {output_columns}")

    # python_code 타입만 상세 검증
    if calc_type == 'python_code':
        formula = indicator_def['formula']
        if isinstance(formula, str):
            formula = json.loads(formula)

        code = formula.get('code', '')

        # 1. result dict 키 추출
        result_keys = extract_result_keys_from_code(code)
        print(f"코드 반환 키: {result_keys}")

        # 2. 컬럼명 일치 여부
        if set(result_keys) != set(output_columns):
            issues.append(f"컬럼명 불일치: code={result_keys}, output_columns={output_columns}")

        # 3. AST 검증이 필요한 변수 확인
        # 현재 허용된 prefix: df, params, result, _, exp, ema, sma, signal, fast, slow, macd
        allowed_prefixes = ('df', 'params', 'result', '_', 'exp', 'ema', 'sma', 'signal', 'fast', 'slow', 'macd')

        # 코드에서 변수명 추출 (간단한 패턴)
        variables = re.findall(r'\b([a-zA-Z_]\w*)\s*=', code)
        blocked_vars = []
        for var in set(variables):
            if var not in ['result', 'df', 'params']:
                if not var.startswith(allowed_prefixes):
                    blocked_vars.append(var)

        if blocked_vars:
            issues.append(f"AST 검증 실패 가능 변수: {blocked_vars}")

    # 4. 실제 계산 테스트
    if calculator is not None:
        try:
            config = {'name': name}
            if indicator_def.get('default_params'):
                params = indicator_def['default_params']
                if isinstance(params, str):
                    params = json.loads(params)
                config['params'] = params

            result = calculator.calculate(test_df, config)

            if result and hasattr(result, 'columns'):
                actual_columns = list(result.columns.keys())
                print(f"✅ 계산 성공: {actual_columns}")

                # 실제 반환된 컬럼과 output_columns 비교
                if set(actual_columns) != set(output_columns):
                    issues.append(f"실제 컬럼과 정의 불일치: actual={actual_columns}, expected={output_columns}")
            else:
                issues.append("계산 결과가 None이거나 columns 속성 없음")

        except Exception as e:
            issues.append(f"계산 실패: {str(e)}")
            print(f"❌ 계산 오류: {e}")
    else:
        print("⚠️  계산 테스트 건너뜀 (Calculator 없음)")

    # 결과 출력
    if issues:
        print(f"\n⚠️  발견된 문제:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print(f"✅ 모든 검증 통과")
        return True

def main():
    print("="*60)
    print("지표 검증 스크립트")
    print("="*60)

    # Supabase에서 모든 활성 지표 가져오기
    client = get_supabase_client()
    result = client.table('indicators').select('*').eq('is_active', True).order('name').execute()

    if not result.data:
        print("활성화된 지표가 없습니다.")
        return

    print(f"\n총 {len(result.data)}개 지표 검증 중...\n")

    # Calculator 초기화 (동적 import)
    try:
        from indicators.calculator import IndicatorCalculator
        calculator = IndicatorCalculator()
    except Exception as e:
        print(f"IndicatorCalculator 로드 실패: {e}")
        print("계산 테스트는 건너뛰고 정적 검증만 수행합니다.")
        calculator = None

    # 테스트 데이터 생성
    test_df = create_test_dataframe()

    # 각 지표 검증
    passed = []
    failed = []

    for indicator in result.data:
        try:
            if validate_indicator(indicator, calculator, test_df):
                passed.append(indicator['name'])
            else:
                failed.append(indicator['name'])
        except Exception as e:
            print(f"\n❌ {indicator['name']} 검증 중 예외 발생: {e}")
            failed.append(indicator['name'])

    # 최종 결과
    print("\n" + "="*60)
    print("검증 결과 요약")
    print("="*60)
    print(f"✅ 통과: {len(passed)}개 - {passed}")
    print(f"❌ 실패: {len(failed)}개 - {failed}")

    if failed:
        print("\n⚠️  실패한 지표들을 수정해야 합니다.")
        sys.exit(1)
    else:
        print("\n✅ 모든 지표 검증 완료!")
        sys.exit(0)

if __name__ == '__main__':
    main()
