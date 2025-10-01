-- ============================================================================
-- MACD 지표 수정 SQL
-- 목적: macd_line -> macd 컬럼명 변경
-- ============================================================================

-- MACD 지표 수정
UPDATE indicators
SET
  formula = jsonb_build_object(
    'code',
    'exp1 = df["close"].ewm(span=params.get("fast", 12), adjust=False).mean()
exp2 = df["close"].ewm(span=params.get("slow", 26), adjust=False).mean()
macd = exp1 - exp2
macd_signal = macd.ewm(span=params.get("signal", 9), adjust=False).mean()
macd_hist = macd - macd_signal
result = {"macd": macd, "macd_signal": macd_signal, "macd_hist": macd_hist}'
  ),
  output_columns = ARRAY['macd', 'macd_signal', 'macd_hist']::text[]
WHERE name = 'macd';

-- 검증
SELECT
  name,
  output_columns,
  formula->>'code' as code_preview
FROM indicators
WHERE name = 'macd';