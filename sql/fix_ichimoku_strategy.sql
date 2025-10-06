-- =====================================================
-- Fix Ichimoku Strategy - Convert price_above_tenkan to standard format
-- =====================================================
--
-- 이 스크립트는 일목균형표 조건을 구 형식에서 표준 형식으로 변환합니다.
--
-- 변환 내용:
-- - buyConditions[2]: { left: "ichimoku", operator: "price_above_tenkan", right: 30 }
--   → { left: "close", operator: ">", right: "ichimoku_tenkan" }
--
-- - buyStageStrategy.stages[2].conditions[0]: 동일하게 변환
-- =====================================================

-- 1. 전략 ID 확인 (실제 ID로 변경 필요)
-- SELECT id, name, config->'buyConditions' as buy_conditions
-- FROM strategies
-- WHERE name = '나의 전략 A1';

-- 2. 특정 전략만 업데이트 (안전)
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      config,
      -- buyConditions[2] 수정
      '{buyConditions,2}',
      '{"left": "close", "operator": ">", "right": "ichimoku_tenkan"}'::jsonb,
      true
    ),
    -- buyStageStrategy.stages[2].conditions[0] 수정
    '{buyStageStrategy,stages,2,conditions,0}',
    '{"left": "close", "operator": ">", "right": "ichimoku_tenkan", "combineWith": "AND"}'::jsonb,
    true
  ),
  -- buyStageStrategy.stages[2].indicators[0]에서 value 제거 (필요시)
  '{buyStageStrategy,stages,2,indicators,0}',
  (config->'buyStageStrategy'->'stages'->2->'indicators'->0) - 'value',
  true
),
updated_at = NOW()
WHERE name = '나의 전략 A1'  -- 또는 id = 'your-strategy-id'
  AND config->'buyConditions'->2->>'operator' = 'price_above_tenkan';

-- 3. 업데이트 결과 확인
SELECT
  id,
  name,
  config->'buyConditions'->2 as buy_condition_3,
  config->'buyStageStrategy'->'stages'->2->'conditions'->0 as stage3_condition_1,
  config->'buyStageStrategy'->'stages'->2->'indicators'->0 as stage3_indicator_1,
  updated_at
FROM strategies
WHERE name = '나의 전략 A1';

-- =====================================================
-- 전체 Config 확인 (디버깅용)
-- =====================================================
-- SELECT
--   id,
--   name,
--   config
-- FROM strategies
-- WHERE name = '나의 전략 A1';

-- =====================================================
-- 롤백 (필요시)
-- =====================================================
-- 만약 잘못 수정했다면, 아래 JSON으로 원복 가능:
/*
UPDATE strategies
SET config = '{
  "stopLoss": {"value": 10.6, "enabled": true},
  "indicators": [...],
  "buyConditions": [
    {"left": "rsi", "right": 32, "operator": "<"},
    {"left": "stochastic_k", "right": 20, "operator": "<"},
    {"left": "close", "operator": ">", "right": "ichimoku_tenkan"}
  ],
  ...
}'::jsonb
WHERE name = '나의 전략 A1';
*/
