"""
SMA 동적 컬럼명 생성 테스트
"""
import asyncio
import os
from supabase import create_client
from backtest.preflight import IndicatorColumnMapper
from indicators.calculator import IndicatorCalculator

async def test_sma_columns():
    # Supabase 클라이언트
    supabase = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')
    )

    # Calculator와 Mapper 생성
    calculator = IndicatorCalculator(
        supabase_client=supabase,
        enforce_db_only=True
    )
    mapper = IndicatorColumnMapper(calculator)

    print("=" * 60)
    print("SMA 동적 컬럼명 생성 테스트")
    print("=" * 60)

    # 1. Supabase에서 SMA 정의 확인
    print("\n1. Supabase SMA 정의 조회:")
    result = supabase.table('indicators') \
        .select('name, output_columns, formula') \
        .eq('name', 'sma') \
        .single() \
        .execute()

    if result.data:
        print(f"  name: {result.data['name']}")
        print(f"  output_columns: {result.data['output_columns']}")
        formula_code = result.data.get('formula', {}).get('code', '')
        print(f"  formula code:")
        print("  " + "\n  ".join(formula_code.split('\n')))

    # 2. period=20으로 컬럼명 확인
    print("\n2. SMA(20) 컬럼명 생성:")
    columns_20 = mapper.get_output_columns('sma', {'period': 20})
    print(f"  Result: {columns_20}")
    print(f"  Expected: ['sma_20']")
    print(f"  Match: {columns_20 == ['sma_20']}")

    # 3. period=60으로 컬럼명 확인
    print("\n3. SMA(60) 컬럼명 생성:")
    columns_60 = mapper.get_output_columns('sma', {'period': 60})
    print(f"  Result: {columns_60}")
    print(f"  Expected: ['sma_60']")
    print(f"  Match: {columns_60 == ['sma_60']}")

    # 4. _extract_dynamic_columns 직접 테스트
    print("\n4. _extract_dynamic_columns 직접 테스트:")
    if result.data:
        formula_code = result.data.get('formula', {}).get('code', '')
        dynamic_cols_20 = mapper._extract_dynamic_columns(formula_code, {'period': 20})
        dynamic_cols_60 = mapper._extract_dynamic_columns(formula_code, {'period': 60})
        print(f"  period=20: {dynamic_cols_20}")
        print(f"  period=60: {dynamic_cols_60}")

    # 5. EMA도 테스트
    print("\n5. EMA 컬럼명 생성:")
    ema_columns_20 = mapper.get_output_columns('ema', {'period': 20})
    print(f"  EMA(20): {ema_columns_20}")
    print(f"  Expected: ['ema_20']")

    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(test_sma_columns())
