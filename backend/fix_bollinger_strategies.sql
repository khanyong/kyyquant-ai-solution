-- 볼린저밴드 전략 수정

-- 첫 번째 전략: 지표 이름 'bb' -> 'bollinger'로 수정, 조건 컬럼명 수정
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      jsonb_set(
        jsonb_set(
          config,
          '{indicators,0,name}',
          '"bollinger"'::jsonb
        ),
        '{buyConditions,0,right}',
        '"bollinger_lower"'::jsonb
      ),
      '{buyConditions,1,left}',
      '"rsi"'::jsonb
    ),
    '{sellConditions,0,right}',
    '"bollinger_upper"'::jsonb
  ),
  '{buyConditions,1,right}',
  '30'::jsonb
)
WHERE id = '0828cb5b-442b-4895-afdf-790135fc1a54';

-- 두 번째 전략: 'type' -> 'name'으로 변경, 지표 이름 수정, 조건 컬럼명 수정
UPDATE strategies
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      jsonb_set(
        jsonb_set(
          jsonb_set(
            jsonb_set(
              config - 'indicators',
              '{indicators}',
              jsonb_build_array(
                jsonb_build_object(
                  'name', 'bollinger',
                  'params', (config->'indicators'->0->'params')
                ),
                jsonb_build_object(
                  'name', 'rsi',
                  'params', (config->'indicators'->1->'params')
                )
              )
            ),
            '{buyConditions,0,indicator}',
            '"close"'::jsonb
          ),
          '{buyConditions,0,value}',
          '"bollinger_lower"'::jsonb
        ),
        '{buyConditions,1,indicator}',
        '"rsi"'::jsonb
      ),
      '{sellConditions,0,indicator}',
      '"close"'::jsonb
    ),
    '{sellConditions,0,value}',
    '"bollinger_upper"'::jsonb
  ),
  '{buyConditions,1,value}',
  '30'::jsonb
)
WHERE id = '505a4558-55e2-49f3-920b-30bed716b383';

-- 확인 쿼리
SELECT
  id,
  name,
  config->'indicators' as indicators,
  config->'buyConditions' as buyConditions,
  config->'sellConditions' as sellConditions
FROM strategies
WHERE id IN ('0828cb5b-442b-4895-afdf-790135fc1a54', '505a4558-55e2-49f3-920b-30bed716b383');
