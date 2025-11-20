"""
모든 Supabase 지표 일괄 검증 스크립트
"""

import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv
from indicators.calculator import IndicatorCalculator, ExecOptions

# 환경변수 로드
load_dotenv()

# Supabase 클라이언트 생성
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))

def get_stock_data(stock_code='005930', days=100):
    """주가 데이터 가져오기"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # kw_price_daily 테이블 사용
    result = client.table('kw_price_daily').select('*').eq(
        'stock_code', stock_code
    ).gte(
        'trade_date', start_date.strftime('%Y-%m-%d')
    ).lte(
        'trade_date', end_date.strftime('%Y-%m-%d')
    ).order('trade_date').execute()

    df = pd.DataFrame(result.data)

    # trade_date를 date로 변경
    if 'trade_date' in df.columns:
        df['date'] = pd.to_datetime(df['trade_date'])

    # 숫자형 컬럼 변환
    numeric_columns = ['open', 'high', 'low', 'close']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # volume 변환
    if 'volume' in df.columns:
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype('int64')

    return df

def test_indicator(indicator_name, default_params):
    """지표 테스트"""
    print(f"\n{'='*80}")
    print(f"테스트: {indicator_name}")
    print('='*80)

    # 데이터 가져오기
    df = get_stock_data()

    # 지표 계산
    calculator = IndicatorCalculator()
    config = {
        'name': indicator_name,
        'params': default_params
    }

    try:
        result = calculator.calculate(
            df=df,
            config=config,
            options=ExecOptions(
                period=default_params.get('period', 20),
                realtime=False
            ),
            stock_code='005930'
        )

        print(f"[SUCCESS] 계산 성공!")
        print(f"  - 실행 시간: {result.execution_time_ms:.2f}ms")
        print(f"  - NaN 비율: {result.nan_ratio*100:.1f}%")
        print(f"  - 생성된 컬럼: {list(result.columns.keys())}")

        if result.warnings:
            print(f"  - 경고: {result.warnings}")

        # 통계 (간략)
        for col_name, col_data in result.columns.items():
            valid_count = col_data.notna().sum()
            if valid_count > 0:
                print(f"  - {col_name}: {valid_count}개 유효 값")

        return True

    except Exception as e:
        print(f"[FAIL] 계산 실패!")
        print(f"  에러: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    print("="*80)
    print("Supabase 지표 전체 검증")
    print("="*80)

    # Supabase에서 모든 활성 지표 조회
    result = client.table('indicators').select('name, default_params').eq('is_active', True).order('name').execute()

    indicators = []
    for indicator in result.data:
        name = indicator['name']

        # default_params 파싱
        import json
        default_params = {}
        if indicator.get('default_params'):
            try:
                if isinstance(indicator['default_params'], str):
                    default_params = json.loads(indicator['default_params'])
                elif isinstance(indicator['default_params'], dict):
                    default_params = indicator['default_params']
            except:
                pass

        # 기본 파라미터 설정 (default_params가 없는 경우)
        if not default_params:
            if 'period' in ['sma', 'ema', 'rsi', 'atr', 'cci', 'williams']:
                default_params = {'period': 14}
            elif name == 'macd':
                default_params = {'fast': 12, 'slow': 26, 'signal': 9}
            elif name == 'bollinger':
                default_params = {'period': 20, 'std': 2}
            elif name == 'stochastic':
                default_params = {'k_period': 14, 'd_period': 3}
            elif name == 'ichimoku':
                default_params = {'tenkan': 9, 'kijun': 26, 'senkou': 52}
            elif name in ['volume_ma', 'ma']:
                default_params = {'period': 20}

        indicators.append({
            'name': name,
            'params': default_params
        })

    print(f"\n총 {len(indicators)}개 지표 테스트 시작\n")

    # 모든 지표 테스트
    results = []
    for idx, indicator in enumerate(indicators, 1):
        print(f"\n[{idx}/{len(indicators)}]", end=' ')
        success = test_indicator(indicator['name'], indicator['params'])
        results.append({
            'name': indicator['name'],
            'success': success
        })

    # 전체 결과 요약
    print("\n" + "="*80)
    print("테스트 결과 요약")
    print("="*80)

    success_list = []
    fail_list = []

    for r in results:
        if r['success']:
            success_list.append(r['name'])
        else:
            fail_list.append(r['name'])

    print(f"\n[성공] {len(success_list)}개:")
    for name in success_list:
        print(f"  - {name}")

    if fail_list:
        print(f"\n[실패] {len(fail_list)}개:")
        for name in fail_list:
            print(f"  - {name}")

    print(f"\n총 {len(results)}개 중 {len(success_list)}개 성공 ({len(success_list)/len(results)*100:.1f}%)")

if __name__ == '__main__':
    main()
