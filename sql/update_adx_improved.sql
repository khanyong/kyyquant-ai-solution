-- ========================================
-- ADX (Average Directional Index) 지표 개선된 formula 업데이트
-- ========================================
-- 개선사항:
-- 1. 표준 ADX 계산 (EWM 사용 - Wilder's smoothing)
-- 2. DM 계산 로직 수정 (+DM과 -DM 중 큰 값만 사용)
-- 3. 0으로 나누기 방어 (ATR, DI 합계)
-- 4. 실시간 거래 지원 (realtime 파라미터)
-- 5. 타입 안전성 (int 변환 및 최소값 보장)
-- ========================================

UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = int(params.get(''period'', 14)); period = max(1, period); rt = params.get(''realtime'', False); rt = str(rt).lower() in (''1'',''true'',''yes''); high_src = df[''high''].shift(1) if rt else df[''high'']; low_src = df[''low''].shift(1) if rt else df[''low'']; close_src = df[''close''].shift(1) if rt else df[''close'']; plus_dm = high_src.diff(); minus_dm = -low_src.diff(); plus_dm = plus_dm.where((plus_dm > 0) & (plus_dm > -minus_dm), 0); minus_dm = minus_dm.where((minus_dm > 0) & (minus_dm > plus_dm), 0); hl = high_src - low_src; hc = abs(high_src - close_src.shift(1)); lc = abs(low_src - close_src.shift(1)); tr = pd.concat([hl, hc, lc], axis=1).max(axis=1); atr = tr.ewm(span=period, adjust=False, min_periods=period).mean(); plus_di = 100 * (plus_dm.ewm(span=period, adjust=False, min_periods=period).mean() / atr.where(atr != 0)); minus_di = 100 * (minus_dm.ewm(span=period, adjust=False, min_periods=period).mean() / atr.where(atr != 0)); di_sum = plus_di + minus_di; dx = 100 * abs(plus_di - minus_di) / di_sum.where(di_sum != 0); result = dx.ewm(span=period, adjust=False, min_periods=period).mean().fillna(0)"
  }',
  default_params = '{"period": 14, "realtime": false}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['adx'],
  updated_at = NOW()
WHERE name = 'adx';

-- ========================================
-- DMI (Directional Movement Index) 지표도 함께 업데이트
-- ADX와 같은 계산 로직을 공유하므로 일관성 유지
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "period = int(params.get(''period'', 14)); period = max(1, period); rt = params.get(''realtime'', False); rt = str(rt).lower() in (''1'',''true'',''yes''); high_src = df[''high''].shift(1) if rt else df[''high'']; low_src = df[''low''].shift(1) if rt else df[''low'']; close_src = df[''close''].shift(1) if rt else df[''close'']; plus_dm = high_src.diff(); minus_dm = -low_src.diff(); plus_dm = plus_dm.where((plus_dm > 0) & (plus_dm > -minus_dm), 0); minus_dm = minus_dm.where((minus_dm > 0) & (minus_dm > plus_dm), 0); hl = high_src - low_src; hc = abs(high_src - close_src.shift(1)); lc = abs(low_src - close_src.shift(1)); tr = pd.concat([hl, hc, lc], axis=1).max(axis=1); atr = tr.ewm(span=period, adjust=False, min_periods=period).mean(); plus_di = 100 * (plus_dm.ewm(span=period, adjust=False, min_periods=period).mean() / atr.where(atr != 0)); minus_di = 100 * (minus_dm.ewm(span=period, adjust=False, min_periods=period).mean() / atr.where(atr != 0)); result = {''dmi_plus_di'': plus_di.fillna(0), ''dmi_minus_di'': minus_di.fillna(0)}"
  }',
  default_params = '{"period": 14, "realtime": false}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['dmi_plus_di', 'dmi_minus_di'],
  updated_at = NOW()
WHERE name = 'dmi';

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
WHERE name IN ('adx', 'dmi')
ORDER BY name;

-- ========================================
-- 변경 사항 상세 확인
-- ========================================
SELECT
  name,
  display_name,
  jsonb_pretty(formula::jsonb) as formula_full,
  jsonb_pretty(default_params::jsonb) as params
FROM indicators
WHERE name IN ('adx', 'dmi')
ORDER BY name;