-- 스윙 트레이딩 전략의 MACD 컬럼명 수정
-- buyConditions[2].left를 'macd'에서 'macd_line'으로 변경

UPDATE strategies
SET
  config = jsonb_set(
    config,
    '{buyConditions,2,left}',
    '"macd_line"'::jsonb
  ),
  updated_at = now()
WHERE name LIKE '%스윙%' OR name LIKE '%Swing%';

-- 수정 확인
SELECT
  name,
  config->'buyConditions'->2->>'left' as macd_column_name,
  config->'buyConditions'->2 as full_condition
FROM strategies
WHERE name LIKE '%스윙%' OR name LIKE '%Swing%';
