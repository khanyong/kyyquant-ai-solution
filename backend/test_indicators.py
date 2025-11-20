"""
지표 테스트 스크립트 - 전략별로 사용되는 지표들을 순차적으로 검증
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

    # kw_price_daily 테이블 사용 (trade_date 컬럼)
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

def test_indicator(indicator_config, indicator_name):
    """지표 테스트"""
    print(f"\n{'='*80}")
    print(f"테스트: {indicator_name}")
    print(f"설정: {indicator_config}")
    print('='*80)

    # 데이터 가져오기
    df = get_stock_data()
    print(f"[OK] 데이터 개수: {len(df)}행")

    # 지표 계산
    calculator = IndicatorCalculator()

    try:
        result = calculator.calculate(
            df=df,
            config=indicator_config,
            options=ExecOptions(
                period=indicator_config.get('params', {}).get('period', 20),
                realtime=False
            ),
            stock_code='005930'
        )

        print(f"\n[SUCCESS] 계산 성공!")
        print(f"  - 실행 시간: {result.execution_time_ms:.2f}ms")
        print(f"  - NaN 비율: {result.nan_ratio*100:.1f}%")
        print(f"  - 생성된 컬럼: {list(result.columns.keys())}")

        if result.warnings:
            print(f"  - 경고: {result.warnings}")

        # 결과 샘플 출력
        print(f"\n최근 5일 데이터:")
        sample_df = df[['date', 'close']].copy()
        for col_name, col_data in result.columns.items():
            sample_df[col_name] = col_data
        print(sample_df.tail())

        # 통계
        print(f"\n지표 통계:")
        for col_name, col_data in result.columns.items():
            valid_count = col_data.notna().sum()
            null_count = col_data.isna().sum()
            if valid_count > 0:
                print(f"  - {col_name}: 유효 {valid_count}개, Null {null_count}개")
                print(f"    평균: {col_data.mean():.2f}, 최소: {col_data.min():.2f}, 최대: {col_data.max():.2f}")

        return True

    except Exception as e:
        print(f"\n[FAIL] 계산 실패!")
        print(f"  에러: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 실행"""
    print("="*80)
    print("지표 검증 테스트 시작")
    print("="*80)

    # 테스트할 지표 목록
    tests = [
        # 1. RSI (여러 전략에서 사용)
        {
            'name': 'RSI (14일)',
            'config': {
                'name': 'rsi',
                'params': {'period': 14}
            }
        },

        # 2. Bollinger Bands
        {
            'name': 'Bollinger Bands (20일, 2σ)',
            'config': {
                'name': 'bb',
                'params': {'period': 20, 'std': 2}
            }
        },

        # 3. Volume MA
        {
            'name': 'Volume MA (20일)',
            'config': {
                'name': 'volume_ma',
                'params': {'period': 20}
            }
        },

        # 4. SMA (여러 기간)
        {
            'name': 'SMA (5일)',
            'config': {
                'name': 'sma',
                'params': {'period': 5}
            }
        },

        # 5. 복합 테스트 - RSI + MACD
        {
            'name': 'MACD (12,26,9)',
            'config': {
                'name': 'macd',
                'params': {'fast': 12, 'slow': 26, 'signal': 9}
            }
        }
    ]

    results = []
    for test in tests:
        success = test_indicator(test['config'], test['name'])
        results.append({
            'name': test['name'],
            'success': success
        })
        print()

    # 전체 결과 요약
    print("\n" + "="*80)
    print("테스트 결과 요약")
    print("="*80)
    for r in results:
        status = "[OK] 성공" if r['success'] else "[FAIL] 실패"
        print(f"{status}: {r['name']}")

    success_count = sum(1 for r in results if r['success'])
    print(f"\n총 {len(results)}개 중 {success_count}개 성공")

if __name__ == '__main__':
    main()
