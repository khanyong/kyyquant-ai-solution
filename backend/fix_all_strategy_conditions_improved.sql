-- ============================================================================
-- 전략 조건 일괄 수정 SQL (개선 버전)
-- 목적: 접미사 컬럼명을 표준 컬럼명으로 변경 + indicators 배열 추가
-- 특징:
--   1. 트랜잭션으로 안전성 보장 (전체 성공 또는 전체 롤백)
--   2. indicators 배열 명시로 명확성 증가
--   3. 현재 백엔드 코드와 100% 호환 (indicator/compareTo/value 구조)
-- ============================================================================

BEGIN;

-- 1. [템플릿] MACD 시그널
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'macd', 'compareTo', 'macd_signal', 'operator', 'cross_above'),
      jsonb_build_object('indicator', 'macd', 'value', 0, 'operator', '>')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'macd', 'compareTo', 'macd_signal', 'operator', 'cross_below')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'macd',
        'type', 'MACD',
        'params', jsonb_build_object('fast', 12, 'slow', 26, 'signal', 9)
      )
    )
  )
WHERE id = '82b9e26e-e115-4d43-a81b-1fa1f444acd0';

-- 2. [템플릿] RSI 과매수/과매도
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'rsi', 'value', 30, 'operator', '<')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'rsi', 'value', 70, 'operator', '>')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'rsi',
        'type', 'RSI',
        'params', jsonb_build_object('period', 14)
      )
    )
  )
WHERE id = '97d50901-504e-4e53-8e29-0d535dc095f0';

-- 3. [템플릿] 골든크로스 (SMA 20 vs 60)
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'sma_20', 'compareTo', 'sma_60', 'operator', 'cross_above')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'sma_20', 'compareTo', 'sma_60', 'operator', 'cross_below')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 20)
      ),
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 60)
      )
    )
  )
WHERE id = '8bc841c7-8ecb-4107-b3a4-674cb304d462';

-- 4. [템플릿] 볼린저밴드
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'close', 'compareTo', 'bb_lower', 'operator', '<'),
      jsonb_build_object('indicator', 'rsi', 'value', 40, 'operator', '<')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'close', 'compareTo', 'bb_upper', 'operator', '>')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'bb',
        'type', 'BollingerBands',
        'params', jsonb_build_object('period', 20, 'stddev', 2)
      ),
      jsonb_build_object(
        'name', 'rsi',
        'type', 'RSI',
        'params', jsonb_build_object('period', 14)
      )
    )
  )
WHERE id = '5d2e10ac-559d-4561-9b3c-932bac4de9df';

-- 5. [템플릿] 중장기 트레이딩
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'sma_20', 'compareTo', 'sma_60', 'operator', '>'),
      jsonb_build_object('indicator', 'rsi', 'value', 60, 'operator', '<'),
      jsonb_build_object('indicator', 'macd', 'value', 0, 'operator', '>')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'sma_20', 'compareTo', 'sma_60', 'operator', '<'),
      jsonb_build_object('indicator', 'rsi', 'value', 70, 'operator', '>')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 20)
      ),
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 60)
      ),
      jsonb_build_object(
        'name', 'rsi',
        'type', 'RSI',
        'params', jsonb_build_object('period', 14)
      ),
      jsonb_build_object(
        'name', 'macd',
        'type', 'MACD',
        'params', jsonb_build_object('fast', 12, 'slow', 26, 'signal', 9)
      )
    )
  )
WHERE id = '62aa9b84-f438-4111-b56f-20a5f7004317';

-- 6. [템플릿] 단기 스캘핑
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'close', 'compareTo', 'sma_5', 'operator', '>'),
      jsonb_build_object('indicator', 'rsi', 'value', 50, 'operator', '<')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'rsi', 'value', 70, 'operator', '>')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 5)
      ),
      jsonb_build_object(
        'name', 'rsi',
        'type', 'RSI',
        'params', jsonb_build_object('period', 14)
      )
    )
  )
WHERE id = 'a8fafa87-6485-49bf-9efc-50df554e2eff';

-- 7. 중장기 트레이딩 (user created)
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'sma_20', 'compareTo', 'sma_60', 'operator', 'cross_above'),
      jsonb_build_object('indicator', 'rsi', 'value', 60, 'operator', '<'),
      jsonb_build_object('indicator', 'macd', 'value', 0, 'operator', '>')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'sma_20', 'compareTo', 'sma_60', 'operator', 'cross_below'),
      jsonb_build_object('indicator', 'rsi', 'value', 70, 'operator', '>')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 20)
      ),
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 60)
      ),
      jsonb_build_object(
        'name', 'rsi',
        'type', 'RSI',
        'params', jsonb_build_object('period', 14)
      ),
      jsonb_build_object(
        'name', 'macd',
        'type', 'MACD',
        'params', jsonb_build_object('fast', 12, 'slow', 26, 'signal', 9)
      )
    )
  )
WHERE id = '931f0e11-afb3-4620-acfe-a24efd325ba0';

-- 8. 단기 스캘핑 (user created)
UPDATE strategies
SET config = config
  || jsonb_build_object(
    'buyConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'close', 'compareTo', 'sma_5', 'operator', '>'),
      jsonb_build_object('indicator', 'rsi', 'value', 50, 'operator', '<')
    ),
    'sellConditions', jsonb_build_array(
      jsonb_build_object('indicator', 'rsi', 'value', 70, 'operator', '>')
    ),
    'indicators', jsonb_build_array(
      jsonb_build_object(
        'name', 'sma',
        'type', 'SMA',
        'params', jsonb_build_object('period', 5)
      ),
      jsonb_build_object(
        'name', 'rsi',
        'type', 'RSI',
        'params', jsonb_build_object('period', 14)
      )
    )
  )
WHERE id = 'ce9b7e21-af26-4bb3-b46f-348c6af3d106';

COMMIT;

-- ============================================================================
-- 검증 쿼리
-- ============================================================================

-- 수정된 전략 확인
SELECT
  id,
  name,
  config->'buyConditions' as buy_conditions,
  config->'sellConditions' as sell_conditions,
  config->'indicators' as indicators
FROM strategies
WHERE id IN (
  '82b9e26e-e115-4d43-a81b-1fa1f444acd0',  -- MACD
  '97d50901-504e-4e53-8e29-0d535dc095f0',  -- RSI
  '8bc841c7-8ecb-4107-b3a4-674cb304d462',  -- 골든크로스
  '5d2e10ac-559d-4561-9b3c-932bac4de9df',  -- 볼린저밴드
  '62aa9b84-f438-4111-b56f-20a5f7004317',  -- 중장기
  'a8fafa87-6485-49bf-9efc-50df554e2eff',  -- 단기
  '931f0e11-afb3-4620-acfe-a24efd325ba0',  -- 중장기(user)
  'ce9b7e21-af26-4bb3-b46f-348c6af3d106'   -- 단기(user)
)
ORDER BY name;