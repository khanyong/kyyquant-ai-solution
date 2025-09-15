-- ================================================
-- Supabase 전략 수정 - 수동 실행용
-- 각 쿼리를 개별적으로 실행
-- ================================================

-- ========================================
-- STEP 1: 현재 문제 확인
-- ========================================

-- 빈 indicators를 가진 전략 확인
SELECT
    id,
    name,
    config->>'templateId' as template_id,
    CASE
        WHEN config->'indicators' IS NULL THEN 'NULL'
        WHEN jsonb_array_length(config->'indicators') = 0 THEN 'EMPTY'
        ELSE 'OK'
    END as indicator_status
FROM strategies
ORDER BY indicator_status DESC;

-- ========================================
-- STEP 2: 특정 전략 확인 (ID로)
-- ========================================

-- 특정 전략의 config 상세 확인 (ID를 변경하세요)
SELECT
    name,
    jsonb_pretty(config) as full_config
FROM strategies
WHERE id = 'YOUR_STRATEGY_ID_HERE';

-- ========================================
-- STEP 3: 템플릿별 수정
-- ========================================

-- 3-1. Golden Cross 전략만 수정
UPDATE strategies
SET
    config = config ||
    '{
        "indicators": [
            {"type": "ma", "params": {"period": 20}},
            {"type": "ma", "params": {"period": 60}}
        ]
    }'::jsonb,
    updated_at = NOW()
WHERE config->>'templateId' = 'golden-cross'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 3-2. RSI Reversal 전략만 수정
UPDATE strategies
SET
    config = config ||
    '{
        "indicators": [
            {"type": "rsi", "params": {"period": 14}}
        ]
    }'::jsonb,
    updated_at = NOW()
WHERE config->>'templateId' = 'rsi-reversal'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 3-3. Bollinger Band 전략만 수정
UPDATE strategies
SET
    config = config ||
    '{
        "indicators": [
            {"type": "bb", "params": {"period": 20, "std": 2}},
            {"type": "rsi", "params": {"period": 14}}
        ]
    }'::jsonb,
    updated_at = NOW()
WHERE config->>'templateId' = 'bollinger-band'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- 3-4. MACD Signal 전략만 수정
UPDATE strategies
SET
    config = config ||
    '{
        "indicators": [
            {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
        ]
    }'::jsonb,
    updated_at = NOW()
WHERE config->>'templateId' = 'macd-signal'
  AND (config->'indicators' IS NULL OR jsonb_array_length(config->'indicators') = 0);

-- ========================================
-- STEP 4: 대문자 조건 수정
-- ========================================

-- 4-1. MA_20, MA_60을 ma_20, ma_60으로 변경
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{buyConditions}',
        REPLACE(
            REPLACE(
                (config->'buyConditions')::text,
                'MA_20', 'ma_20'
            ),
            'MA_60', 'ma_60'
        )::jsonb
    ),
    updated_at = NOW()
WHERE (config->'buyConditions')::text LIKE '%MA_%';

UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{sellConditions}',
        REPLACE(
            REPLACE(
                (config->'sellConditions')::text,
                'MA_20', 'ma_20'
            ),
            'MA_60', 'ma_60'
        )::jsonb
    ),
    updated_at = NOW()
WHERE (config->'sellConditions')::text LIKE '%MA_%';

-- 4-2. RSI_14를 rsi_14로 변경
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{buyConditions}',
        REPLACE(
            (config->'buyConditions')::text,
            'RSI_14', 'rsi_14'
        )::jsonb
    ),
    updated_at = NOW()
WHERE (config->'buyConditions')::text LIKE '%RSI_%';

UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{sellConditions}',
        REPLACE(
            (config->'sellConditions')::text,
            'RSI_14', 'rsi_14'
        )::jsonb
    ),
    updated_at = NOW()
WHERE (config->'sellConditions')::text LIKE '%RSI_%';

-- 4-3. CROSS_ABOVE, CROSS_BELOW를 소문자로 변경
UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{buyConditions}',
        REPLACE(
            REPLACE(
                (config->'buyConditions')::text,
                'CROSS_ABOVE', 'cross_above'
            ),
            'CROSS_BELOW', 'cross_below'
        )::jsonb
    ),
    updated_at = NOW()
WHERE (config->'buyConditions')::text LIKE '%CROSS_%';

UPDATE strategies
SET
    config = jsonb_set(
        config,
        '{sellConditions}',
        REPLACE(
            REPLACE(
                (config->'sellConditions')::text,
                'CROSS_ABOVE', 'cross_above'
            ),
            'CROSS_BELOW', 'cross_below'
        )::jsonb
    ),
    updated_at = NOW()
WHERE (config->'sellConditions')::text LIKE '%CROSS_%';

-- ========================================
-- STEP 5: 특정 전략 직접 수정 (예시)
-- ========================================

-- 특정 ID의 전략을 완전히 수정 (ID를 변경하세요)
UPDATE strategies
SET config = '{
    "name": "골든크로스 전략",
    "templateId": "golden-cross",
    "indicators": [
        {"type": "ma", "params": {"period": 20}},
        {"type": "ma", "params": {"period": 60}}
    ],
    "buyConditions": [
        {"indicator": "ma_20", "operator": "cross_above", "value": "ma_60"}
    ],
    "sellConditions": [
        {"indicator": "ma_20", "operator": "cross_below", "value": "ma_60"}
    ],
    "stopLoss": 5,
    "takeProfit": 10,
    "trailingStop": false,
    "maxHoldingDays": 30
}'::jsonb,
updated_at = NOW()
WHERE id = 'YOUR_STRATEGY_ID_HERE';

-- ========================================
-- STEP 6: 결과 확인
-- ========================================

-- 수정된 전략 확인
SELECT
    id,
    name,
    config->>'templateId' as template,
    jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) as indicator_count,
    config->'indicators' as indicators,
    updated_at
FROM strategies
WHERE updated_at > NOW() - INTERVAL '10 minutes'
ORDER BY updated_at DESC;

-- 여전히 문제가 있는 전략 확인
SELECT
    id,
    name,
    'Empty indicators' as issue
FROM strategies
WHERE config->'indicators' IS NULL
   OR jsonb_array_length(config->'indicators') = 0;

-- ========================================
-- STEP 7: 통계
-- ========================================

SELECT
    COUNT(*) as total_strategies,
    COUNT(CASE WHEN jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) > 0 THEN 1 END) as fixed_strategies,
    COUNT(CASE WHEN jsonb_array_length(COALESCE(config->'indicators', '[]'::jsonb)) = 0 THEN 1 END) as still_broken
FROM strategies;