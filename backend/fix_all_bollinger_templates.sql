-- 모든 볼린저밴드 관련 템플릿 수정
-- 지표 이름: bb → bollinger
-- 컬럼명: bb_lower → bollinger_lower, bb_upper → bollinger_upper

-- 1. [템플릿] 볼린저밴드 수정
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
  AND user_id IS NULL
  AND config->'indicators'->0->>'name' = 'bb';

-- 2. [템플릿] 복합 전략 B 수정
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      '{indicators,1,name}',
      '"bollinger"'::jsonb
    ),
    '{buyConditions,1,right}',
    '"bollinger_lower"'::jsonb
  ),
  '{sellConditions,0,right}',
  '"bollinger_upper"'::jsonb
)
WHERE name = '[템플릿] 복합 전략 B'
  AND user_id IS NULL
  AND config->'indicators'->1->>'name' = 'bb';

-- 확인 쿼리
SELECT
  name,
  user_id,
  config->'indicators' as indicators,
  config->'buyConditions' as buy_conditions,
  config->'sellConditions' as sell_conditions
FROM strategies
WHERE name IN ('[템플릿] 볼린저밴드', '[템플릿] 복합 전략 B')
  AND user_id IS NULL
ORDER BY name;
