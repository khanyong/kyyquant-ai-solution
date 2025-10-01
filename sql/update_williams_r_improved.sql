-- ========================================
-- Williams %R 지표 개선된 formula 업데이트
-- ========================================
-- 개선사항:
-- 1. period 타입 안전성 (int 변환 및 최소값 1 보장)
-- 2. 실시간 거래 지원 (realtime 파라미터)
-- 3. 0으로 나누기 방어 (where 조건)
-- 4. 데이터 정합성 (min_periods, clip)
-- ========================================

UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = int(params.get(''period'', 14)); period = 1 if period < 1 else period; rt = params.get(''realtime'', False); rt = str(rt).lower() in (''1'',''true'',''yes''); high_src = df[''high''].shift(1) if rt else df[''high'']; low_src = df[''low''].shift(1) if rt else df[''low'']; hh = high_src.rolling(window=period, min_periods=period).max(); ll = low_src.rolling(window=period, min_periods=period).min(); rng = hh - ll; wr = -100 * (hh - df[''close'']) / rng.where(rng != 0); result = wr.clip(-100, 0)"
  }',
  default_params = '{"period": 14, "realtime": false}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['williams_r'],
  updated_at = NOW()
WHERE name = 'williams';

-- ========================================
-- 실행 확인 쿼리
-- ========================================
SELECT
  name,
  display_name,
  calculation_type,
  left((formula::json->>'code')::text, 100) || '...' as formula_preview,
  default_params,
  output_columns,
  updated_at
FROM indicators
WHERE name = 'williams';

-- ========================================
-- 변경 사항 상세 확인
-- ========================================
SELECT
  name,
  display_name,
  jsonb_pretty(formula::jsonb) as formula_full,
  jsonb_pretty(default_params::jsonb) as params
FROM indicators
WHERE name = 'williams';