-- [템플릿] 볼린저밴드 전략 수정
-- 지표 이름: bb → bollinger
-- 컬럼명: bb_lower → bollinger_lower, bb_upper → bollinger_upper

UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{indicators,0,name}',
      '"bollinger"'::jsonb
    ),
    '{buyConditions,0,right}',
    '"bollinger_lower"'::jsonb
  ),
  '{sellConditions,0,right}',
  '"bollinger_upper"'::jsonb
)
WHERE name = '[템플릿] 볼린저밴드'
  AND config->'indicators'->0->>'name' = 'bb';

-- 확인 쿼리
SELECT
  name,
  config->'indicators'->0->>'name' as indicator_0_name,
  config->'buyConditions'->0->>'right' as buy_condition_0_right,
  config->'sellConditions'->0->>'right' as sell_condition_0_right
FROM strategies
WHERE name = '[템플릿] 볼린저밴드';
