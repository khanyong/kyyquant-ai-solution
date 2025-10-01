-- ========================================
-- ADX (Average Directional Index) 최종 최적화 formula 업데이트
-- ========================================
-- 개선사항:
-- 1. Wilder's alpha (1.0/period) 정확한 구현
-- 2. NumPy 벡터화로 성능 최적화
-- 3. 0으로 나누기 방어 강화 (np.inf 사용)
-- 4. 실시간 거래 지원 (realtime 파라미터)
-- 5. 결과 범위 제한 (0-100) 및 NaN 처리
-- ========================================

UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "import numpy as np; period = int(params.get(''period'', 14)); period = max(1, period); rt = params.get(''realtime'', False); rt = str(rt).lower() in (''1'',''true'',''yes''); h = df[''high''].shift(1) if rt else df[''high'']; l = df[''low''].shift(1) if rt else df[''low'']; c = df[''close''].shift(1) if rt else df[''close'']; h_prev = h.shift(1); l_prev = l.shift(1); c_prev = c.shift(1); up_move = h - h_prev; down_move = l_prev - l; plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index); minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index); tr = pd.concat([h - l, (h - c_prev).abs(), (l - c_prev).abs()], axis=1).max(axis=1); alpha = 1.0 / period; atr = tr.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); plus_dm_smooth = plus_dm.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); minus_dm_smooth = minus_dm.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); plus_di = 100.0 * (plus_dm_smooth / atr.where(atr != 0, np.inf)); minus_di = 100.0 * (minus_dm_smooth / atr.where(atr != 0, np.inf)); di_sum = plus_di + minus_di; dx = 100.0 * (plus_di - minus_di).abs() / di_sum.where(di_sum != 0, np.inf); adx = dx.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); result = adx.clip(0, 100).fillna(0)"
  }',
  default_params = '{"period": 14, "realtime": false}',
  required_data = ARRAY['high', 'low', 'close'],
  output_columns = ARRAY['adx'],
  updated_at = NOW()
WHERE name = 'adx';

-- ========================================
-- DMI (Directional Movement Index) 최종 최적화
-- ADX와 동일한 계산 로직 사용
-- ========================================
UPDATE indicators SET
  calculation_type = 'python_code',
  formula = '{
    "code": "import numpy as np; period = int(params.get(''period'', 14)); period = max(1, period); rt = params.get(''realtime'', False); rt = str(rt).lower() in (''1'',''true'',''yes''); h = df[''high''].shift(1) if rt else df[''high'']; l = df[''low''].shift(1) if rt else df[''low'']; c = df[''close''].shift(1) if rt else df[''close'']; h_prev = h.shift(1); l_prev = l.shift(1); c_prev = c.shift(1); up_move = h - h_prev; down_move = l_prev - l; plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=df.index); minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=df.index); tr = pd.concat([h - l, (h - c_prev).abs(), (l - c_prev).abs()], axis=1).max(axis=1); alpha = 1.0 / period; atr = tr.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); plus_dm_smooth = plus_dm.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); minus_dm_smooth = minus_dm.ewm(alpha=alpha, adjust=False, min_periods=period).mean(); plus_di = 100.0 * (plus_dm_smooth / atr.where(atr != 0, np.inf)); minus_di = 100.0 * (minus_dm_smooth / atr.where(atr != 0, np.inf)); result = {''dmi_plus_di'': plus_di.clip(0, 100).fillna(0), ''dmi_minus_di'': minus_di.clip(0, 100).fillna(0)}"
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
-- 상세 변경 사항 확인
-- ========================================
SELECT
  name,
  display_name,
  jsonb_pretty(formula::jsonb) as formula_full,
  jsonb_pretty(default_params::jsonb) as params
FROM indicators
WHERE name IN ('adx', 'dmi')
ORDER BY name;

-- ========================================
-- 테스트 데이터로 검증 (선택사항)
-- ========================================
-- ADX는 일반적으로 0-100 범위, 25 이상이면 트렌드 강함
-- +DI > -DI: 상승 트렌드
-- -DI > +DI: 하락 트렌드