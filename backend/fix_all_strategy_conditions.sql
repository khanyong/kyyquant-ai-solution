-- ============================================================================
-- 전략 조건 일괄 수정 SQL
-- 목적: 접미사 컬럼명을 표준 컬럼명으로 변경하여 백테스트 거래 0회 문제 해결
-- ============================================================================

-- 1. [템플릿] MACD 시그널
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "macd", "compareTo": "macd_signal", "operator": "cross_above"},
      {"indicator": "macd", "value": 0, "operator": ">"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "macd", "compareTo": "macd_signal", "operator": "cross_below"}
  ]'::jsonb
)
WHERE id = '82b9e26e-e115-4d43-a81b-1fa1f444acd0';

-- 2. [템플릿] RSI 과매수/과매도
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "rsi", "value": 30, "operator": "<"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "rsi", "value": 70, "operator": ">"}
  ]'::jsonb
)
WHERE id = '97d50901-504e-4e53-8e29-0d535dc095f0';

-- 3. [템플릿] 골든크로스
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "sma_20", "compareTo": "sma_60", "operator": "cross_above"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "sma_20", "compareTo": "sma_60", "operator": "cross_below"}
  ]'::jsonb
)
WHERE id = '8bc841c7-8ecb-4107-b3a4-674cb304d462';

-- 4. [템플릿] 볼린저밴드
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "close", "compareTo": "bb_lower", "operator": "<"},
      {"indicator": "rsi", "value": 40, "operator": "<"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "close", "compareTo": "bb_upper", "operator": ">"}
  ]'::jsonb
)
WHERE id = '5d2e10ac-559d-4561-9b3c-932bac4de9df';

-- 5. [템플릿] 중장기 트레이딩
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "sma_20", "compareTo": "sma_60", "operator": ">"},
      {"indicator": "rsi", "value": 60, "operator": "<"},
      {"indicator": "macd", "value": 0, "operator": ">"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "sma_20", "compareTo": "sma_60", "operator": "<"},
    {"indicator": "rsi", "value": 70, "operator": ">"}
  ]'::jsonb
)
WHERE id = '62aa9b84-f438-4111-b56f-20a5f7004317';

-- 6. [템플릿] 단기 스캘핑
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "close", "compareTo": "sma_5", "operator": ">"},
      {"indicator": "rsi", "value": 50, "operator": "<"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "rsi", "value": 70, "operator": ">"}
  ]'::jsonb
)
WHERE id = 'a8fafa87-6485-49bf-9efc-50df554e2eff';

-- 7. 중장기 트레이딩 (user created)
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "sma_20", "compareTo": "sma_60", "operator": "cross_above"},
      {"indicator": "rsi", "value": 60, "operator": "<"},
      {"indicator": "macd", "value": 0, "operator": "cross_above"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "sma_20", "compareTo": "sma_60", "operator": "cross_below"},
    {"indicator": "rsi", "value": 70, "operator": ">"}
  ]'::jsonb
)
WHERE id = '931f0e11-afb3-4620-acfe-a24efd325ba0';

-- 8. 단기 스캘핑 (user created)
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    config,
    '{buyConditions}',
    '[
      {"indicator": "close", "compareTo": "sma_5", "operator": ">"},
      {"indicator": "rsi", "value": 50, "operator": "<"}
    ]'::jsonb
  ),
  '{sellConditions}',
  '[
    {"indicator": "rsi", "value": 70, "operator": ">"}
  ]'::jsonb
)
WHERE id = 'ce9b7e21-af26-4bb3-b46f-348c6af3d106';

-- 결과 확인
SELECT
  id,
  name,
  config->'buyConditions' as buy_conditions,
  config->'sellConditions' as sell_conditions
FROM strategies
WHERE id IN (
  '82b9e26e-e115-4d43-a81b-1fa1f444acd0',
  '97d50901-504e-4e53-8e29-0d535dc095f0',
  '8bc841c7-8ecb-4107-b3a4-674cb304d462',
  '5d2e10ac-559d-4561-9b3c-932bac4de9df',
  '62aa9b84-f438-4111-b56f-20a5f7004317',
  'a8fafa87-6485-49bf-9efc-50df554e2eff',
  '931f0e11-afb3-4620-acfe-a24efd325ba0',
  'ce9b7e21-af26-4bb3-b46f-348c6af3d106'
);