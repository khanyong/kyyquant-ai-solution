-- SMA formula 확인 및 f-string 패턴 검증

SELECT
  name,
  output_columns,
  formula->>'code' as formula_code,
  -- result = 패턴 확인
  CASE
    WHEN formula->>'code' LIKE '%result = {f%'
    THEN 'f-string 패턴 있음 ✓'
    ELSE 'f-string 패턴 없음 ✗'
  END as fstring_check,
  -- sma_{period} 패턴 확인
  CASE
    WHEN formula->>'code' LIKE '%sma_{period}%'
    THEN 'sma_{period} 패턴 있음 ✓'
    ELSE 'sma_{period} 패턴 없음 ✗'
  END as period_pattern_check
FROM indicators
WHERE name = 'sma';
